import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from datetime import datetime, UTC, timedelta
from pilotsuite.core.selections import SelectionStore, InvalidSelection, SelectionConflict
from pilotsuite.core.zones import ZoneStore
from pilotsuite.core.context import ContextStore
from pilotsuite.domain.context import context_summary
from pilotsuite.domain.models import Neuron


def sensor(e, kind, value, quality='good'):
    return Neuron(e, 'test', kind, value, '°C' if kind=='temperature' else '%', quality, None, e)

class RoleGroupTests(unittest.TestCase):
    def test_climate_requires_roles_and_reference_never_enters_median(self):
        ns = [sensor('sensor.a','temperature',20), sensor('sensor.b','temperature',22), sensor('sensor.out','temperature',90)]
        summary, _ = context_summary(ns,{})
        self.assertEqual('ambiguous',summary['temperature']['status'])
        summary, climate = context_summary(ns, {'temperature':['sensor.a','sensor.b'], 'reference_temperature':['sensor.out']})
        self.assertEqual(21,summary['temperature']['value'])
        self.assertEqual(2,summary['temperature']['spread'])
        self.assertEqual(21,climate[0].value)
        self.assertEqual(90,summary['reference_temperature'][0]['value'])

    def test_missing_and_invalid_sources_do_not_claim_absence_or_zero(self):
        summary, _ = context_summary([sensor('sensor.a','temperature',20),sensor('binary_sensor.p','motion',False)],
          {'temperature':['sensor.a','sensor.missing'], 'presence':['binary_sensor.p','binary_sensor.missing']})
        self.assertEqual('partial',summary['temperature']['status'])
        self.assertEqual(20,summary['temperature']['value'])
        self.assertEqual(2,summary['temperature']['total_count'])
        self.assertEqual(1,summary['temperature']['valid_count'])
        self.assertIsNone(summary['presence']['active'])
        summary, _ = context_summary([sensor('binary_sensor.p','motion',True)], {'presence':['binary_sensor.p','binary_sensor.missing']})
        self.assertTrue(summary['presence']['active'])

    def test_virtual_reference_and_empty_main_group(self):
        ns = [sensor('sensor.a', 'temperature', 20), sensor('sensor.b', 'temperature', 24)]
        summary, _ = context_summary(ns, {'temperature': ['sensor.a', 'sensor.b']})
        ref = summary['temperature']['reference']
        self.assertTrue(ref['virtual'])
        self.assertEqual(22, ref['value'])
        self.assertEqual(['sensor.a', 'sensor.b'], ref['sources'])
        summary, _ = context_summary(ns[:1], {'temperature': []})
        self.assertIsNone(summary['temperature']['reference']['value'])
        self.assertEqual('not_selected', summary['temperature']['status'])

    def test_presence_never_falls_back_to_other_relevant_sensors(self):
        ns = [sensor('binary_sensor.a', 'motion', False), sensor('binary_sensor.b', 'occupancy', True)]
        summary, _ = context_summary(ns, {'presence': ['binary_sensor.a']})
        self.assertFalse(summary['presence']['reference']['value'])
        self.assertEqual(['binary_sensor.a'], summary['presence']['reference']['sources'])
        for roles in ({}, {'presence': []}):
            summary, _ = context_summary(ns, roles)
            self.assertIsNone(summary['presence']['active'])
            self.assertEqual('not_selected', summary['presence']['status'])

    def test_illuminance_normalization_and_reference(self):
        from pilotsuite.domain.neurons import build_neurons
        ns = build_neurons({'entities': [
            {'entity_id': 'sensor.'+str(i), 'area_id': 'a', 'state': {'state': value,
             'attributes': {'device_class': 'illuminance', 'unit_of_measurement': unit}}}
            for i, (value, unit) in enumerate([('100','lx'), ('300','lux'), ('-1','lx'), ('50','%'), ('bright','lx')])
        ]})
        summary, climate = context_summary(ns, {'illuminance': [n.entity_id for n in ns]})
        info = summary['illuminance']
        self.assertEqual(200, info['reference']['value'])
        self.assertEqual('lx', info['reference']['unit'])
        self.assertEqual('partial', info['status'])
        self.assertEqual(2, info['valid_count'])
        self.assertEqual([], climate)

class LearningTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.selections=SelectionStore(Path(self.temp.name)); await self.selections.initialize()
        self.zones=ZoneStore(self.selections); await self.zones.bootstrap(('a',))
        await self.selections.patch('a',0,{'binary_sensor.a':'relevant','binary_sensor.b':'relevant'})
        self.store=ContextStore(self.selections)
        self.now=time.time()
        self.roles={'presence':['binary_sensor.a','binary_sensor.b']}

    async def consent(self):
        revision=(await self.selections.get('a'))['revision']
        await self.store.configure('a',revision,self.roles,True,now=self.now-10*86400)

    async def seed(self):
        await self.consent()
        day=datetime.fromtimestamp(self.now,UTC).replace(hour=8,minute=0,second=0,microsecond=0)
        for d in (4,3,2):
            for minute in (0,10):
                t=(day-timedelta(days=d)+timedelta(minutes=minute)).timestamp()
                self.assertTrue(await self.store.record('a','binary_sensor.a',t,'unknown',now=t))
                # Second detector seeing the same activity must not double-count it.
                self.assertFalse(await self.store.record('a','binary_sensor.b',t+2,'unknown',now=t+2))

    async def test_progress_empty_and_retention_expiry(self):
        report = await self.store.report('a', now=self.now)
        self.assertEqual([], report['progress']['windows'])
        self.assertIsNone(report['progress']['first_evidence_at'])
        await self.seed()
        report = await self.store.report('a', now=self.now)
        window = report['progress']['windows'][0]
        self.assertEqual((6, 3, 0, 0), (window['events'], window['days'], window['missing_events'], window['missing_days']))
        self.assertIsNotNone(report['progress']['first_evidence_at'])
        report = await self.store.report('a', now=self.now+15*86400)
        self.assertEqual([], report['progress']['windows'])
        self.assertIsNone(report['progress']['last_evidence_at'])

    async def test_progress_never_pools_different_time_windows(self):
        await self.consent()
        day = datetime.fromtimestamp(self.now, UTC).replace(hour=8, minute=0, second=0, microsecond=0)
        for d in (4, 3, 2):
            for hour in (0, 4):
                t = (day-timedelta(days=d)+timedelta(hours=hour)).timestamp()
                await self.store.record('a', 'binary_sensor.a', t, 'unknown', now=t)
        report = await self.store.report('a', now=self.now)
        self.assertEqual(6, report['event_count'])
        self.assertEqual([], report['patterns'])
        self.assertEqual([2, 2], [w['missing_events'] for w in report['progress']['windows']])
        self.assertEqual([0, 0], [w['missing_days'] for w in report['progress']['windows']])

    async def test_no_consent_no_events_duplicate_and_stale_rejection(self):
        self.assertFalse(await self.store.record('a','binary_sensor.a',self.now,'unknown',now=self.now))
        await self.consent()
        self.assertTrue(await self.store.record('a','binary_sensor.a',self.now,'unknown',now=self.now))
        self.assertFalse(await self.store.record('a','binary_sensor.a',self.now,'unknown',now=self.now))
        self.assertFalse(await self.store.record('a','binary_sensor.b',self.now-180,'unknown',now=self.now))
        self.assertFalse(await self.store.record('a','binary_sensor.b',self.now+60,'unknown',now=self.now))

    async def test_pattern_feedback_is_separate_and_survives_restart(self):
        await self.seed()
        report=await self.store.report('a',now=self.now)
        self.assertEqual(6,report['event_count']); self.assertEqual(1,len(report['patterns']))
        pattern=report['patterns'][0]
        self.assertEqual(3,len(pattern['days'])); self.assertIsNone(pattern['confidence'])
        await self.store.feedback('a',pattern['id'],'accepted')
        restored=ContextStore(self.selections)
        after=await restored.report('a',now=self.now)
        self.assertEqual(report['evidence'],after['evidence'])
        self.assertEqual('accepted',after['patterns'][0]['feedback'])
        self.assertEqual(pattern['id'],after['patterns'][0]['id'])
        self.assertEqual(0,(await restored.report('other',now=self.now))['event_count'])

    async def test_revoke_reset_and_group_change_preserve_selections(self):
        await self.seed()
        rev=(await self.selections.get('a'))['revision']
        await self.store.configure('a',rev,self.roles,False)
        self.assertFalse(await self.store.record('a','binary_sensor.a',self.now,'unknown',now=self.now))
        self.assertEqual(6,(await self.store.report('a',now=self.now))['event_count'])
        await self.store.configure('a',rev+1,self.roles,False,reset=True)
        report=await self.store.report('a',now=self.now)
        self.assertEqual(0,report['event_count']); self.assertFalse(report['config']['learning'])
        self.assertEqual('relevant',(await self.selections.get('a'))['decisions']['binary_sensor.a'])
        with self.assertRaises(SelectionConflict): await self.store.configure('a',rev,self.roles,True)
        with self.assertRaises(InvalidSelection): await self.store.configure('a',rev+2,{},True)

    async def test_retention_and_cap_are_enforced_even_without_events(self):
        await self.consent()
        with sqlite3.connect(self.store.path) as db:
            db.executemany('INSERT INTO activity_evidence VALUES (?,?,?,?)', [('a','binary_sensor.a',self.now-i,'unknown') for i in range(5002)])
            db.execute('INSERT INTO activity_evidence VALUES (?,?,?,?)',('a','binary_sensor.a',self.now-15*86400,'unknown'))
        await self.store.maintain()
        report=await self.store.report('a',now=self.now)
        self.assertEqual(5000,report['event_count'])
        self.assertEqual(0,(await self.store.report('a',now=self.now+15*86400))['event_count'])

    async def test_schema_three_backup_preserves_choices_and_no_inferred_consent(self):
        with sqlite3.connect(self.store.path) as db:
            for table in ('zone_context','activity_evidence','pattern_feedback'): db.execute(f'DROP TABLE {table}')
            db.execute('PRAGMA user_version=3')
            db.execute("INSERT INTO selection_modes VALUES ('a',0)")
        await self.selections.initialize()
        self.assertTrue((await self.selections.get('a'))['active'])
        self.assertFalse((await self.store.get('a'))['learning'])
        backups=list(Path(self.temp.name).glob('selections.v3.*.bak'));self.assertEqual(1,len(backups))
        with sqlite3.connect(backups[0]) as db:
            self.assertEqual(3,db.execute('PRAGMA user_version').fetchone()[0])
            self.assertEqual(0,db.execute("SELECT active FROM selection_modes WHERE zone_id='a'").fetchone()[0])


class CollectionStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_collection_status_explains_each_blocker(self):
        from types import SimpleNamespace
        from unittest.mock import AsyncMock
        from pilotsuite.app import _context_payload
        for learning, enabled, ready, sources, expected in [
            (False, True, True, [], 'off'),
            (True, False, True, [], 'paused'),
            (True, True, False, ['binary_sensor.a'], 'disconnected'),
            (True, True, True, [], 'no_source'),
            (True, True, True, ['binary_sensor.a'], 'collecting'),
        ]:
            service = SimpleNamespace(
                selection_inventory=AsyncMock(return_value={'revision': 1, 'enabled': enabled, 'items': []}),
                context=SimpleNamespace(report=AsyncMock(return_value={'config': {'learning': learning, 'roles': {}}, 'evidence': []})),
                status=AsyncMock(return_value={'ready': ready}),
                _learning_sources={'a': sources} if sources else {})
            report = await _context_payload(service, 'a')
            self.assertEqual(expected, report['collection_state'])
            self.assertNotIn('evidence', report)
