import json
import sqlite3
import tempfile
import time
import unittest
from datetime import datetime, UTC
from pathlib import Path
from pilotsuite.core.selections import SelectionStore, InvalidSelection
from pilotsuite.core.zones import ZoneStore
from pilotsuite.core.context import ContextStore, validate_detector
from pilotsuite.core.learning_views import time_bucket, coverage_report, activation_context, context_report


def stamp(value):
    return datetime.fromisoformat(value).timestamp()


class LocalTimeTests(unittest.TestCase):
    def test_midnight_uses_local_day_and_weekend(self):
        detector = {'timezone': 'Europe/Berlin', 'day_mode': 'weekday_weekend'}
        self.assertEqual((('weekend', 0), '2026-09-26'), time_bucket(stamp('2026-09-25T22:30:00+00:00'), detector))
        self.assertEqual((('weekday', 11), '2026-09-25'), time_bucket(stamp('2026-09-25T21:30:00+00:00'), detector))

    def test_dst_repeat_is_one_local_date_window(self):
        detector = {'timezone': 'Europe/Berlin'}
        a = time_bucket(stamp('2026-10-25T00:30:00+00:00'), detector)
        b = time_bucket(stamp('2026-10-25T01:30:00+00:00'), detector)
        self.assertEqual(a, b)
        self.assertEqual(('all', 1), a[0])

    def test_spring_skips_nonexistent_local_hour(self):
        detector = {'timezone': 'Europe/Berlin'}
        self.assertEqual(('all', 0), time_bucket(stamp('2026-03-29T00:30:00+00:00'), detector)[0])
        self.assertEqual(('all', 1), time_bucket(stamp('2026-03-29T01:30:00+00:00'), detector)[0])

    def test_invalid_zone_and_mode_and_default_identity(self):
        base = {'min_events': 5, 'min_days': 3}
        for extra in ({'timezone':'Missing/Zone'}, {'timezone':'/etc/passwd'}, {'day_mode':'person'}, {'timezone':False}):
            with self.assertRaises(InvalidSelection): validate_detector(dict(base, **extra))
        self.assertEqual(base, validate_detector(dict(base, timezone='UTC', day_mode='all')))

    def test_coverage_does_not_turn_mixed_bucket_or_missing_check_into_ready(self):
        report = coverage_report([(0,'ready'), (0,'disconnected'), (600,'ready')])
        self.assertEqual(2, report['sampled_slots'])
        self.assertEqual(1, report['impaired_slots'])
        self.assertEqual(1, report['ready_only_slots'])
        self.assertEqual(1, report['unobserved_slots_between_checks'])
        self.assertEqual(0, coverage_report([])['sampled_slots'])

    def test_context_uses_explicit_complete_sources_only(self):
        summary = {'light': {'sources':['light.a'], 'status':'available', 'active':True},
                   'illuminance': {'sources':['sensor.lux'], 'status':'partial', 'value':40}}
        self.assertIsNone(activation_context(summary,{})['light']['value'])
        data = activation_context(summary, {'light':['light.a'], 'illuminance':['sensor.lux']})
        self.assertTrue(data['light']['value'])
        self.assertIsNone(data['illuminance']['value'])

    def test_unknown_days_cannot_qualify_light_context(self):
        records = [(stamp(f'2026-09-{day}T08:00:00+00:00'), {'light':{'value': True if day==20 else None}}) for day in (20,21,22)]
        records += [(stamp(f'2026-09-20T08:{minute}:00+00:00'), {'light':{'value':True}}) for minute in (10,20,30,40)]
        report = context_report(records, {'min_events':5,'min_days':3})[0]
        self.assertEqual(5, report['light_on'])
        self.assertFalse(report['review_ready'])
        self.assertIsNone(report['lux_median'])


class ContextStorageTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.selections = SelectionStore(Path(self.tmp.name)); await self.selections.initialize()
        self.zones = ZoneStore(self.selections); await self.zones.bootstrap(('a',))
        await self.selections.patch('a',0,{'binary_sensor.p':'relevant'})
        self.store = ContextStore(self.selections); self.now = time.time()
        self.roles = {'presence':['binary_sensor.p'], 'light':['light.a'], 'illuminance':['sensor.lux']}
        self.data = {'light':{'value':True,'sources':['light.a']}, 'illuminance':{'value':20,'sources':['sensor.lux']}}

    async def configure(self, **kwargs):
        rev = (await self.selections.get('a'))['revision']
        return await self.store.configure('a', rev, self.roles, kwargs.pop('learning',True), now=kwargs.pop('now',self.now-1), **kwargs)

    async def test_context_needs_own_consent_and_persists_without_duplicates(self):
        await self.configure()
        await self.store.record('a','binary_sensor.p',self.now,'unknown',now=self.now,context=self.data)
        self.assertEqual([], (await self.store.report('a',now=self.now))['context_evidence'])
        await self.configure(context_learning=True, now=self.now+300)
        await self.store.record('a','binary_sensor.p',self.now+301,'unknown',now=self.now+301,context=self.data)
        await self.store.record('a','binary_sensor.p',self.now+302,'unknown',now=self.now+302,context=self.data)
        report = await ContextStore(self.selections).report('a',now=self.now+302)
        self.assertEqual(2, report['event_count']); self.assertEqual(1,len(report['context_evidence']))
        self.assertEqual(1, report['context_windows'][0]['light_on'])
        self.assertEqual([], (await self.store.report('other',now=self.now+302))['context_evidence'])

    async def test_bounded_origin_categories_persist_but_identifiers_do_not(self):
        await self.configure()
        origins = ('parented_service_context', 'service_context', 'derived_context', 'invalid-private-id')
        for index, origin in enumerate(origins):
            occurred = self.now + index * 301
            await self.store.record(
                'a', 'binary_sensor.p', occurred, origin, now=occurred
            )
        report = await self.store.report('a', now=self.now + 904)
        self.assertEqual(
            ['parented_service_context', 'service_context', 'derived_context', 'unknown'],
            [item['origin'] for item in report['evidence']],
        )
        self.assertNotIn('invalid-private-id', json.dumps(report))

    async def test_context_withdrawal_and_role_change(self):
        await self.configure(context_learning=True)
        await self.store.record('a','binary_sensor.p',self.now,'unknown',now=self.now,context=self.data)
        await self.configure(context_learning=False)
        await self.store.record('a','binary_sensor.p',self.now+301,'unknown',now=self.now+301,context=self.data)
        self.assertEqual(1,len((await self.store.report('a',now=self.now+301))['context_evidence']))
        self.roles['light']=['light.b']; await self.configure()
        report=await self.store.report('a',now=self.now+301)
        self.assertEqual([], report['context_evidence']); self.assertEqual(2,report['event_count'])

    async def test_reset_retention_and_checkpoint_consent(self):
        await self.store.checkpoint('a','ready',now=self.now)
        self.assertEqual(0,(await self.store.report('a',now=self.now))['coverage']['sampled_slots'])
        await self.configure(context_learning=True)
        await self.store.checkpoint('a','ready',now=self.now)
        await self.store.checkpoint('a','disconnected',now=self.now)
        await self.store.record('a','binary_sensor.p',self.now,'unknown',now=self.now,context=self.data)
        report=await self.store.report('a',now=self.now)
        self.assertEqual(1,report['coverage']['impaired_slots'])
        await self.configure(reset=True)
        report=await self.store.report('a',now=self.now)
        self.assertEqual([], report['coverage_samples']); self.assertEqual([],report['context_evidence'])
        self.assertFalse(report['config']['context_learning'])
        await self.configure(context_learning=True)
        await self.store.checkpoint('a','ready',now=self.now)
        report=await self.store.report('a',now=self.now+15*86400)
        self.assertEqual([], report['coverage_samples'])

    async def test_v4_migration_backs_up_and_preserves_roles_and_choices(self):
        await self.configure()
        with sqlite3.connect(self.selections.path) as db:
            db.execute('DROP TABLE activity_context'); db.execute('DROP TABLE coverage_checks')
            db.execute('PRAGMA user_version=4')
        await self.selections.initialize()
        backups=list(Path(self.tmp.name).glob('selections.v4.*.bak'))
        self.assertEqual(1,len(backups))
        with sqlite3.connect(backups[0]) as db:
            self.assertEqual(4,db.execute('PRAGMA user_version').fetchone()[0])
            self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='activity_context'").fetchone())
        self.assertEqual(self.roles, (await self.store.get('a'))['roles'])
        self.assertFalse((await self.store.get('a'))['context_learning'])
        self.assertEqual('relevant',(await self.selections.get('a'))['decisions']['binary_sensor.p'])
        with sqlite3.connect(self.selections.path) as db:
            self.assertEqual(5,db.execute('PRAGMA user_version').fetchone()[0])

    async def test_progress_counts_local_days_at_utc_midnight(self):
        first=stamp('2026-09-25T22:30:00+00:00')
        second=stamp('2026-09-26T00:30:00+00:00')
        await self.configure(detector={'min_events':5,'min_days':3,'timezone':'Europe/Berlin'},now=first-1)
        for t in (first,second):
            await self.store.record('a','binary_sensor.p',t,'unknown',now=t)
        report=await self.store.report('a',now=second)
        self.assertEqual(1,report['progress']['observed_days'])
        self.assertEqual(2,report['progress']['observed_days_utc'])

    async def test_threshold_edit_preserves_timezone_and_explicit_utc_clears_it(self):
        await self.configure(detector={'min_events':5,'min_days':3,'timezone':'Europe/Berlin','day_mode':'weekday_weekend'})
        await self.configure(detector={'min_events':10,'min_days':4})
        self.assertEqual('Europe/Berlin',(await self.store.get('a'))['detector']['timezone'])
        await self.configure(detector={'min_events':10,'min_days':4,'timezone':'UTC','day_mode':'all'})
        self.assertEqual({'min_events':10,'min_days':4},(await self.store.get('a'))['detector'])

    async def test_local_report_groups_weekdays_and_weekends(self):
        now=stamp('2026-09-28T12:00:00+00:00')
        await self.configure(detector={'min_events':5,'min_days':3,'timezone':'Europe/Berlin','day_mode':'weekday_weekend'}, now=now-10*86400)
        for day in (22,23,24,26,27):
            for minute in (0,10):
                t=stamp(f'2026-09-{day}T06:{minute:02d}:00+00:00')
                await self.store.record('a','binary_sensor.p',t,'unknown',now=t)
        report=await self.store.report('a',now=now)
        self.assertEqual('Europe/Berlin',report['time_basis'])
        self.assertEqual(1,len(report['patterns']))
        stats=report['patterns'][0]['statistics']
        self.assertEqual('weekday',stats['day_group']); self.assertEqual(8,stats['window_local']['start_hour'])
        self.assertIsNone(stats['window_utc'])
        self.assertEqual(2,len(report['progress']['windows']))
