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
from pilotsuite.core.learning_views import (time_bucket, coverage_report,
                                             activation_context, context_report,
                                             sanitize_context_record)


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

    def test_context_rejects_invalid_current_lux_and_malformed_sources(self):
        roles = {'illuminance': ['sensor.lux']}
        for value in (float('nan'), float('inf'), float('-inf'), -1, True, '20'):
            data = activation_context(
                {'illuminance': {'sources': ['sensor.lux'], 'status': 'available', 'value': value}},
                roles,
            )
            self.assertEqual({'value': None, 'sources': ['sensor.lux'], 'status': 'unknown'},
                             data['illuminance'])
        data = activation_context(
            {'illuminance': {'sources': ['sensor.lux', {'bad': 'source'}],
                             'status': 'available', 'value': 20}}, roles)
        self.assertEqual(20, data['illuminance']['value'])

    def test_historical_context_never_exports_invalid_lux(self):
        invalid = (float('nan'), float('inf'), float('-inf'), -1, True, '20')
        records = [
            (stamp(f'2026-09-2{index}T08:00:00+00:00'),
             {'light': {'value': True, 'sources': ['light.a', 'Not.AnEntity', {'bad': 'source'}]},
              'illuminance': {'value': value, 'sources': ['sensor.lux']}})
            for index, value in enumerate(invalid)
        ]
        report = context_report(records, {'min_events': 5, 'min_days': 3})[0]
        self.assertEqual(0, report['lux_count'])
        self.assertIsNone(report['lux_median'])
        self.assertEqual(['light.a', 'sensor.lux'], report['sources'])
        json.dumps(report, allow_nan=False)

    def test_invalid_time_inputs_are_controlled_or_ignored(self):
        for value in (float('nan'), float('inf'), float('-inf'), True, 'now'):
            with self.assertRaises(InvalidSelection):
                time_bucket(value, {'timezone': 'UTC'})
        report = coverage_report([(float('nan'), 'ready'), (0, 'ready')])
        self.assertEqual(1, report['sampled_slots'])
        self.assertEqual([], context_report([(float('inf'), {})], {'min_events': 5, 'min_days': 3}))

    def test_retained_context_projection_is_bounded_and_strict(self):
        result = sanitize_context_record({
            'light': {'value': True, 'status': 'available',
                      'sources': ['light.a', 'INVALID', 'light.a'],
                      'timing': 'at_or_before_event', 'private': 'CANARY'},
            'illuminance': {'value': float('nan'), 'status': 'available',
                            'sources': ['sensor.lux'], 'timing': 'invented'},
            'captured_at': '2026-09-27T06:00:00Z', 'private': 'CANARY',
        })
        self.assertEqual(True, result['light']['value'])
        self.assertEqual(['light.a'], result['light']['sources'])
        self.assertIsNone(result['illuminance']['value'])
        self.assertEqual('unknown', result['illuminance']['status'])
        self.assertNotIn('timing', result['illuminance'])
        self.assertNotIn('private', json.dumps(result))
        self.assertEqual('2026-09-27T06:00:00+00:00', result['captured_at'])
        json.dumps(result, allow_nan=False)

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

    async def test_invalid_event_time_and_context_are_not_persisted(self):
        await self.configure(context_learning=True)
        self.assertFalse(await self.store.record(
            'a', 'binary_sensor.p', float('nan'), 'unknown', now=self.now,
            context=self.data,
        ))
        malformed = {'illuminance': {'value': float('nan'), 'sources': ['sensor.lux']}}
        self.assertTrue(await self.store.record(
            'a', 'binary_sensor.p', self.now, 'unknown', now=self.now,
            context=malformed,
        ))
        report = await self.store.report('a', now=self.now)
        self.assertEqual(1, report['event_count'])
        self.assertEqual([], report['context_evidence'])
        json.dumps(report, allow_nan=False)

    async def test_legacy_context_rows_are_sanitized_without_breaking_export(self):
        # Both rows deliberately belong to one two-hour bucket; wall-clock time
        # near a boundary otherwise makes this unrelated integrity test nondeterministic.
        self.now = stamp('2026-09-27T12:00:00+00:00')
        with sqlite3.connect(self.selections.path) as db:
            db.execute('INSERT INTO activity_evidence VALUES (?,?,?,?)',
                       ('a', 'binary_sensor.p', self.now, 'unknown'))
            db.execute('INSERT INTO activity_context VALUES (?,?,?)', (
                'a', self.now,
                '{"light":{"value":true,"status":"available",'
                '"sources":["light.a","INVALID"]},'
                '"illuminance":{"value":NaN,"status":"available",'
                '"sources":["sensor.lux"]},"private":"CANARY"}',
            ))
            db.execute('INSERT INTO activity_evidence VALUES (?,?,?,?)',
                       ('a', 'binary_sensor.p', self.now + 301, 'unknown'))
            db.execute('INSERT INTO activity_context VALUES (?,?,?)',
                       ('a', self.now + 301, '{broken'))
            db.execute('INSERT INTO activity_context VALUES (?,?,?)',
                       ('a', float('inf'), '{"private":"CANARY"}'))
        report = await self.store.report('a', now=self.now + 301)
        self.assertEqual(2, len(report['context_evidence']))
        first = report['context_evidence'][0]['context']
        self.assertEqual(True, first['light']['value'])
        self.assertEqual(['light.a'], first['light']['sources'])
        self.assertIsNone(first['illuminance']['value'])
        self.assertEqual('unknown', first['illuminance']['status'])
        self.assertNotIn('CANARY', json.dumps(report))
        self.assertEqual(2, report['context_windows'][0]['activations'])
        json.dumps(report, allow_nan=False)

    async def test_context_records_across_time_boundary_are_not_merged(self):
        at = stamp('2026-09-27T13:59:00+00:00')
        with sqlite3.connect(self.selections.path) as db:
            for t in (at, at + 301):
                db.execute('INSERT INTO activity_evidence VALUES (?,?,?,?)', ('a', 'binary_sensor.p', t, 'unknown'))
                db.execute('INSERT INTO activity_context VALUES (?,?,?)', ('a', t, json.dumps(self.data)))
        report = await self.store.report('a', now=at+301)
        self.assertEqual(2, len(report['context_evidence']))
        self.assertEqual([1,1], sorted(row['activations'] for row in report['context_windows']))

    async def test_retained_report_quarantines_corrupt_rows_without_rewriting(self):
        await self.configure(context_learning=True, now=self.now-2000)
        valid_import = 'a' * 32
        valid_receipt = {'id': valid_import, 'authorized_at': self.now,
                         'start': self.now-1200, 'end': self.now-900,
                         'sources': ['binary_sensor.p'], 'accepted': 1,
                         'retained_from_import': 1,
                         'basis': 'current_sources_applied_retrospectively',
                         'context_imported': False}
        future_import = 'c' * 32
        future_receipt = {**valid_receipt, 'id': future_import,
                          'authorized_at': self.now + 3600}
        with sqlite3.connect(self.selections.path) as db:
            db.executemany('INSERT INTO activity_evidence VALUES (?,?,?,?)', [
                ('a', 'binary_sensor.p', self.now-1000, 'unknown'),
                ('a', 'binary_sensor.p', self.now-700, 'private-origin'),
                ('a', 'binary_sensor.p', self.now-400, 'unknown'),
                ('a', 'INVALID', self.now-300, 'unknown'),
                ('a', 'binary_sensor.p', 'bad-time', 'unknown'),
                ('a', 'binary_sensor.p', self.now+3600, 'unknown'),
            ])
            db.executemany('INSERT INTO history_imports VALUES (?,?,?,?)', [
                (valid_import, 'a', self.now, json.dumps(valid_receipt)),
                ('bad', 'a', self.now, '{"id":"bad","accepted":NaN,"private":"CANARY"}'),
                ('b' * 32, 'a', self.now, '{broken'),
                (future_import, 'a', self.now + 3600, json.dumps(future_receipt)),
            ])
            db.executemany('INSERT INTO history_provenance VALUES (?,?,?,?)', [
                ('a', 'binary_sensor.p', self.now-1000, valid_import),
                ('a', 'binary_sensor.p', self.now-400, 'bad'),
            ])
            slot = int(self.now//300)*300
            db.executemany('INSERT INTO coverage_checks VALUES (?,?,?)', [
                ('a', slot, 'ready'), ('a', slot, 'invented'),
            ])
            db.execute('INSERT INTO pattern_feedback VALUES (?,?,?,?)',
                       ('a', 'not-a-pattern', 'execute', self.now))
            db.execute('INSERT INTO activity_context VALUES (?,?,?)',
                       ('a', 'bad-time', '{"private":"CANARY"}'))
            db.execute('INSERT INTO activity_context VALUES (?,?,?)',
                       ('a', self.now + 3600, '{"private":"FUTURE"}'))
        report = await self.store.report('a', now=self.now)
        self.assertEqual(3, report['event_count'])
        self.assertEqual(1, report['historical_event_count'])
        self.assertEqual([valid_import], [item['id'] for item in report['history_imports']])
        self.assertEqual(['ready'], [item['state'] for item in report['coverage_samples']])
        self.assertEqual('unknown', report['evidence'][1]['origin'])
        self.assertEqual('live', report['evidence'][2]['recording_source'])
        self.assertEqual('degraded', report['retained_integrity']['status'])
        self.assertEqual({
            'activity_evidence': 3, 'history_provenance': 1, 'history_imports': 3,
            'pattern_feedback': 1, 'coverage_checks': 1, 'activity_context': 2,
        }, report['retained_integrity']['excluded_rows'])
        self.assertEqual(1, report['retained_integrity']['normalized_rows']['activity_evidence'])
        encoded = json.dumps(report, allow_nan=False)
        self.assertNotIn('CANARY', encoded)
        with sqlite3.connect(self.selections.path) as db:
            self.assertEqual(6, db.execute(
                'SELECT COUNT(*) FROM activity_evidence WHERE zone_id="a"').fetchone()[0])
            self.assertEqual(4, db.execute(
                'SELECT COUNT(*) FROM history_imports WHERE zone_id="a"').fetchone()[0])

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
            self.assertEqual(8,db.execute('PRAGMA user_version').fetchone()[0])

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
