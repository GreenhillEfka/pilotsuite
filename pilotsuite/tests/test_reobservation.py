"""Synthetic temporal review; never connects to HA or changes live consent."""
import copy
from datetime import datetime, UTC
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pilotsuite.core.context import ContextStore
from pilotsuite.core.history import retrospective
from pilotsuite.core.review import review_brief
from pilotsuite.core.selections import SelectionStore
from pilotsuite.core.zones import ZoneStore

DAY = 86400
BASE = datetime(2026, 9, 7, tzinfo=UTC).timestamp()
DETECTOR = {'min_events': 5, 'min_days': 3}


class TemporalPartitionTests(unittest.TestCase):
    def test_later_evidence_cannot_qualify_earlier_window(self):
        events = [(BASE+d*DAY+8*3600+i*600, 'synthetic')
                  for d in (0, 8, 9) for i in (0, 1)]
        result = retrospective(events, DETECTOR, BASE, BASE+10*DAY)
        self.assertEqual([], result['checks'])
        window = result['windows'][0]
        self.assertEqual('insufficient_earlier_evidence', window['state'])
        self.assertEqual((2, 4), (window['training_events'], window['later_events']))

    def test_half_open_period_and_exact_split_have_no_overlap(self):
        end, split = BASE+10*DAY, BASE+7*DAY
        events = [(t, 'synthetic') for t in (BASE-1, BASE, split-1, split, end-1, end, end+1)]
        result = retrospective(events, DETECTOR, BASE, end)
        self.assertEqual(2, sum(w['training_events'] for w in result['windows']))
        self.assertEqual(2, sum(w['later_events'] for w in result['windows']))
        self.assertEqual(4, sum(w['events'] for w in result['heatmap']))
        midnight = next(w for w in result['windows'] if w['start_hour'] == 0)
        self.assertEqual(1, midnight['later_events'])

    def test_later_other_hour_or_day_group_does_not_confirm_pattern(self):
        events = [(BASE+d*DAY+8*3600+i*600, 'synthetic')
                  for d in (0, 1, 2) for i in (0, 1)]
        events += [(BASE+11*DAY+12*3600, 'synthetic'),
                   (BASE+13*DAY+8*3600, 'synthetic')]
        result = retrospective(events, {**DETECTOR, 'timezone':'Europe/Berlin',
                               'day_mode':'weekday_weekend'}, BASE, BASE+14*DAY)
        early = result['checks'][0]
        self.assertEqual(('weekday', 10), (early['day_group'], early['start_hour']))
        self.assertEqual('insufficient_later_evidence', early['state'])
        self.assertEqual(0, early['later_events'])

    def test_empty_period_stays_without_checks(self):
        result = retrospective([], DETECTOR, BASE, BASE+14*DAY)
        self.assertEqual([], result['checks'])
        self.assertEqual([], result['windows'])


class RetainedEvidenceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.selections = SelectionStore(Path(tmp.name))
        await self.selections.initialize()
        self.zones = ZoneStore(self.selections)
        await self.zones.bootstrap(('cellar_synthetic',))
        other = await self.zones.save(dict(name='Synthetic neutral zone', area_ids=[],
            extra_entity_ids=['binary_sensor.second'], enabled=True, profile='observe'))
        self.other = other['zone_id']
        self.store = ContextStore(self.selections)
        self.now = BASE+14*DAY
        self.clock = patch('pilotsuite.core.context.time.time', return_value=self.now)
        self.clock.start()
        self.addCleanup(self.clock.stop)
        for zone, source, hour, detector in [
            ('cellar_synthetic', 'binary_sensor.first', 8, DETECTOR),
            (self.other, 'binary_sensor.second', 18,
             {**DETECTOR, 'timezone':'Europe/Berlin', 'day_mode':'weekday_weekend'})]:
            revision = (await self.selections.get(zone))['revision']
            await self.selections.patch(zone, revision, {source:'relevant'})
            await self.store.configure(zone, revision+1, {'presence':[source]}, True,
                                       now=BASE-1, detector=detector)
            for d in (0, 1, 2):
                for minute in (0, 10):
                    t = BASE+d*DAY+hour*3600+minute*60
                    self.assertTrue(await self.store.record(zone, source, t, 'unknown', now=t))
        t = BASE+11*DAY+8*3600
        self.assertTrue(await self.store.record('cellar_synthetic', 'binary_sensor.first', t, 'unknown', now=t))

    async def test_two_zones_keep_review_counts_sources_and_feedback_separate(self):
        first = await self.store.report('cellar_synthetic', now=self.now)
        second = await self.store.report(self.other, now=self.now)
        p1, p2 = first['patterns'][0], second['patterns'][0]
        r1, r2 = review_brief(p1, first), review_brief(p2, second)
        self.assertEqual('reobserved', r1['temporal_check']['state'])
        self.assertEqual('insufficient_later_evidence', r2['temporal_check']['state'])
        self.assertEqual(1, r1['temporal_check']['later_events'])
        self.assertEqual(20, r2['temporal_check']['start_hour'])
        self.assertEqual(['binary_sensor.second'], r2['sources'])
        before = copy.deepcopy(first)
        await self.store.feedback('cellar_synthetic', p1['id'], 'accepted')
        after = await ContextStore(self.selections).report('cellar_synthetic', now=self.now)
        for key in ('evidence', 'reobservation', 'event_count'):
            self.assertEqual(before[key], after[key])
        for key in ('statistics', 'rule_strength', 'confidence', 'risk'):
            self.assertEqual(p1[key], after['patterns'][0][key])
        self.assertEqual('accepted', after['patterns'][0]['preference'])
        self.assertIsNone((await self.store.report(self.other, now=self.now))['patterns'][0]['preference'])
        self.assertFalse(review_brief(after['patterns'][0], after)['execution']['allowed'])

    async def test_revoked_consent_and_returned_brief_do_not_change_retained_evidence(self):
        zone = 'cellar_synthetic'
        before = await self.store.report(zone, now=self.now)
        revision = (await self.selections.get(zone))['revision']
        await self.store.configure(zone, revision, before['config']['roles'], False)
        after = await self.store.report(zone, now=self.now)
        self.assertEqual(before['reobservation'], after['reobservation'])
        self.assertEqual(before['evidence'], after['evidence'])
        brief = review_brief(after['patterns'][0], after)
        self.assertTrue(any('aufbewahrte' in w for w in brief['warnings']))
        brief['temporal_check']['later_events'] = 999
        self.assertEqual(1, after['reobservation']['checks'][0]['later_events'])
        self.assertFalse(brief['execution']['allowed'])

    async def test_recent_candidate_does_not_claim_prior_detection(self):
        zone = 'cellar_synthetic'
        revision = (await self.selections.get(zone))['revision']
        roles = {'presence':['binary_sensor.first']}
        await self.store.configure(zone, revision, roles, False, reset=True)
        await self.store.configure(zone, revision+1, roles, True, now=BASE)
        for d in (10, 11, 12):
            for minute in (0, 10):
                t = BASE+d*DAY+8*3600+minute*60
                self.assertTrue(await self.store.record(zone, roles['presence'][0], t, 'unknown', now=t))
        report = await self.store.report(zone, now=self.now)
        pattern = report['patterns'][0]
        self.assertTrue(pattern['rule_strength']['threshold_met'])
        check = review_brief(pattern, report)
        self.assertEqual('insufficient_earlier_evidence', check['temporal_check']['state'])
        self.assertEqual(0, check['temporal_check']['training_events'])
        self.assertEqual(6, check['temporal_check']['later_events'])
        self.assertTrue(any('rückwirkend' in w for w in check['warnings']))
