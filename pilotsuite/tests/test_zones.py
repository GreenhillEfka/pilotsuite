import tempfile
import unittest
from pathlib import Path
from aiohttp.test_utils import TestClient, TestServer
from pilotsuite.app import create_app, SERVICE_KEY
from pilotsuite.core.settings import Settings


class ZoneTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        settings = Settings(Path(self.temp.name), Path(self.temp.name) / 'options.json',
                            golden_zone_area_ids=('a',), supervisor_token='',
                            refresh_interval_seconds=3600, ingress_allowed_peers=('127.0.0.1',))
        self.app = create_app(settings)
        self.client = TestClient(TestServer(self.app))
        await self.client.start_server()
        self.addAsyncCleanup(self.client.close)
        self.service = self.app[SERVICE_KEY]
        await self.service.world.replace({'areas': [{'area_id': 'a'}, {'area_id': 'b'}],
            'entities': [{'entity_id': 'sensor.hot', 'area_id': 'a'}, {'entity_id': 'sensor.remote', 'area_id': 'b'}, {'entity_id': 'sensor.orphan'}],
            'states': [{'entity_id': 'sensor.hot', 'state': '30', 'attributes': {'device_class': 'temperature', 'unit_of_measurement': '°C'}}]})
        self.definition = {'name': 'Living space', 'area_ids': ['a', 'b'], 'extra_entity_ids': ['sensor.orphan'], 'enabled': False, 'profile': 'observe'}

    async def create(self):
        response = await self.client.post('/api/v1/zones', json={'definition': self.definition})
        self.assertEqual(201, response.status)
        return await response.json()

    async def test_create_compose_rename_conflicts_and_disable(self):
        zone = await self.create()
        zone_id = zone['zone_id']
        inventory = await (await self.client.get(f'/api/v1/selections/{zone_id}')).json()
        self.assertTrue(inventory['applied_to_inference'])
        self.assertEqual({'sensor.hot', 'sensor.remote', 'sensor.orphan'}, {i['entity_id'] for i in inventory['items']})
        self.assertTrue(all(i['decision'] == 'unreviewed' for i in inventory['items']))
        response = await self.client.patch(f'/api/v1/selections/{zone_id}', json={'revision': 1, 'changes': {'sensor.hot': 'relevant'}})
        self.assertEqual(200, response.status)
        response = await self.client.patch(f'/api/v1/zones/{zone_id}', json={'revision': 1, 'definition': self.definition})
        self.assertEqual(409, response.status)
        updated = {**self.definition, 'name': 'Renamed', 'enabled': True}
        response = await self.client.patch(f'/api/v1/zones/{zone_id}', json={'revision': 2, 'definition': updated})
        self.assertEqual(200, response.status)
        self.assertEqual(zone_id, (await response.json())['zone_id'])
        zone_result = next(z for z in self.service._zone_results if z['zone_id'] == zone_id)
        self.assertEqual(1, zone_result['evaluated_count'])
        self.assertEqual(['sensor.hot'], [n['entity_id'] for n in zone_result['neurons']])
        api = await (await self.client.get('/api/v1/zones')).json()
        scoped = next(z for z in api['results'] if z['zone_id'] == zone_id)
        self.assertEqual(['sensor.hot'], [n['entity_id'] for n in scoped['neurons']])
        self.assertIsNone(next(m['score'] for m in zone_result['moods'] if m['name'] == 'temperature_high'))
        self.assertFalse(any(s.scope == (zone_id,) for s in self.service._suggestions))
        # Overlapping sensor is counted only once across both zones.
        self.assertEqual(1, len(self.service._neurons))
        response = await self.client.patch(f'/api/v1/zones/{zone_id}', json={'revision': 3, 'definition': {**updated, 'enabled': False}})
        self.assertEqual(200, response.status)
        self.assertFalse(any(z['zone_id'] == zone_id for z in self.service._zone_results))
        self.assertEqual('relevant', (await self.service.selections.get(zone_id))['decisions']['sensor.hot'])

    async def test_removed_source_retains_decision_and_reappears(self):
        zone = await self.create()
        zone_id = zone['zone_id']
        await self.service.selections.patch(zone_id, 1, {'sensor.hot': 'relevant'})
        await self.service.zones.save({**self.definition, 'area_ids': []}, zone_id, 2)
        inventory = await self.service.selection_inventory(zone_id)
        self.assertIn({'entity_id': 'sensor.hot', 'decision': 'relevant'}, inventory['missing'])
        await self.service.zones.save(self.definition, zone_id, 3)
        inventory = await self.service.selection_inventory(zone_id)
        self.assertEqual('relevant', next(i['decision'] for i in inventory['items'] if i['entity_id'] == 'sensor.hot'))

    async def test_unknown_references_and_extra_fields_rejected(self):
        for change in [{'area_ids': ['unknown']}, {'extra_entity_ids': ['sensor.unknown']}, {'profile': 'magic'}, {'enabled': 1}]:
            response = await self.client.post('/api/v1/zones', json={'definition': {**self.definition, **change}})
            self.assertEqual(400, response.status)
        self.assertEqual(400, (await self.client.post('/api/v1/zones', data='{')).status)
        self.assertEqual(1, len(await self.service.zones.list()))

    async def test_bootstrap_once_preserves_existing_zone(self):
        await self.service.selections.patch('a', 0, {'sensor.hot': 'ignored'}, True)
        await self.service.zones.bootstrap(('changed_options',))
        zones = await self.service.zones.list()
        self.assertEqual(['a'], [z['zone_id'] for z in zones])
        self.assertEqual(1, zones[0]['revision'])
        self.assertTrue((await self.service.selections.get('a'))['active'])

    async def test_ingress_guard_on_zone_mutation(self):
        from dataclasses import replace
        self.service.settings = replace(self.service.settings, ingress_allowed_peers=('172.30.32.2',))
        self.assertEqual(403, (await self.client.post('/api/v1/zones', json={'definition': self.definition})).status)

    async def test_export_and_bounded_journal(self):
        import sqlite3
        self.service.selections.journal_limit = 2
        zone = await self.create()
        for revision, decision in [(1, 'relevant'), (2, 'ignored'), (3, 'relevant')]:
            await self.service.selections.patch(zone['zone_id'], revision, {'sensor.hot': decision})
        with sqlite3.connect(self.service.selections.path) as db:
            self.assertEqual(2, db.execute('SELECT count(*) FROM selection_journal').fetchone()[0])
        response = await self.client.get('/api/v1/zones/export')
        self.assertEqual(200, response.status)
        export = await response.json()
        saved = next(z for z in export['items'] if z['zone_id'] == zone['zone_id'])
        self.assertEqual('relevant', saved['selection']['decisions']['sensor.hot'])
        self.assertNotIn('states', saved)

    async def test_schema_two_migration_preserves_selection_mode(self):
        import sqlite3
        await self.service.selections.patch('a', 0, {'sensor.hot': 'relevant'}, True)
        with sqlite3.connect(self.service.selections.path) as db:
            db.execute('DROP TABLE habitus_zones')
            db.execute('DROP TABLE zone_meta')
            db.execute('DROP TABLE zone_context')
            db.execute('DROP TABLE activity_evidence')
            db.execute('DROP TABLE pattern_feedback')
            db.execute('PRAGMA user_version=2')
        await self.service.selections.initialize()
        await self.service.zones.bootstrap(('a',))
        saved = await self.service.selections.get('a')
        self.assertTrue(saved['active'])
        self.assertEqual(1, saved['revision'])
        self.assertEqual('relevant', saved['decisions']['sensor.hot'])
        self.assertEqual(1, len(list(Path(self.temp.name).glob('selections.v2.*.bak'))))

    async def test_context_roles_consent_events_and_export_through_api(self):
        from datetime import datetime, UTC, timedelta
        now = datetime.now(UTC)
        entities = [{'entity_id': 'binary_sensor.p', 'area_id':'a'}, {'entity_id':'binary_sensor.q','area_id':'a'}]
        await self.service.world.replace({'areas':[{'area_id':'a'}], 'entities':entities,
          'states':[{'entity_id':e['entity_id'],'state':'off','last_updated':now.isoformat(),'attributes':{'device_class':'motion'}} for e in entities]})
        path='/api/v1/zones/a/context'
        bad=await self.client.patch(path,json={'revision':0,'roles':{'presence':['binary_sensor.p']},'learning':True})
        self.assertEqual(400,bad.status)  # Unreviewed is not permission to learn.
        await self.service.selections.patch('a',0,{e['entity_id']:'relevant' for e in entities})
        result=await self.client.patch(path,json={'revision':1,'roles':{'presence':['binary_sensor.p','binary_sensor.q']},'learning':True})
        self.assertEqual(200,result.status)
        self.service._connected=self.service._stream_connected=True
        self.service._last_refresh_at=now.isoformat()
        event_time=datetime.now(UTC)
        event={'entity_id':'binary_sensor.p','old_state':{'state':'off'},'new_state':{'entity_id':'binary_sensor.p','state':'on','last_changed':event_time.isoformat(),'last_updated':event_time.isoformat(),'attributes':{'device_class':'motion'},'context':{'user_id':'secret-user-id'}}}
        await self.service._on_state_change(event)
        await self.service._on_state_change(event)
        report=await (await self.client.get(path)).json()
        self.assertEqual(1,report['event_count'])
        self.assertNotIn('evidence',report)
        export=await (await self.client.get(path+'/export')).json()
        self.assertEqual('user_context',export['evidence'][0]['origin'])
        self.assertNotIn('secret-user-id',str(export))
        # Revoke: subsequent live events are not retained.
        result=await self.client.patch(path,json={'revision':2,'roles':{'presence':['binary_sensor.p','binary_sensor.q']},'learning':False,'reset':True})
        self.assertEqual(200,result.status)
        self.assertEqual(0,(await result.json())['event_count'])
        self.assertEqual('relevant',(await self.service.selections.get('a'))['decisions']['binary_sensor.p'])
        self.assertEqual(409,(await self.client.patch(path,json={'revision':1,'roles':{},'learning':False})).status)
        self.assertEqual(400,(await self.client.post('/api/v1/zones/a/feedback',json={'pattern_id':'unknown','decision':'accepted'})).status)

    async def test_learning_context_ingress_and_type_guards(self):
        from dataclasses import replace
        self.assertEqual(400,(await self.client.patch('/api/v1/zones/a/context',data='{')).status)
        self.assertEqual(400,(await self.client.patch('/api/v1/zones/a/context',json={'revision':0,'roles':{'temperature':['sensor.hot']},'learning':True})).status)
        self.service.settings=replace(self.service.settings,ingress_allowed_peers=('172.30.32.2',))
        self.assertEqual(403,(await self.client.get('/api/v1/zones/a/context/export')).status)
        self.assertEqual(403,(await self.client.patch('/api/v1/zones/a/context',json={'revision':0,'roles':{},'learning':False})).status)
