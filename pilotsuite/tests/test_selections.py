from __future__ import annotations

import asyncio
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from aiohttp.test_utils import TestClient, TestServer
from pilotsuite.app import SERVICE_KEY, create_app
from pilotsuite.core.settings import Settings
from pilotsuite.core.selections import InvalidSelection, SelectionConflict, SelectionStore


class SelectionStoreTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = SelectionStore(Path(self.temp.name))
        await self.store.initialize()

    async def test_persistence_isolation_and_noop(self):
        self.assertEqual(0, (await self.store.get('example'))['revision'])
        await self.store.patch('example', 0, {'sensor.temperature': 'relevant'})
        other = SelectionStore(Path(self.temp.name))
        await other.initialize()
        saved = await other.get('example')
        self.assertEqual({'sensor.temperature': 'relevant'}, saved['decisions'])
        self.assertEqual({}, (await other.get('other'))['decisions'])
        self.assertEqual(saved, await other.patch('example', 1, saved['decisions']))

    async def test_invalid_batch_is_atomic(self):
        for revision, changes in [(True, {'sensor.a': 'relevant'}),
                                  (0, {'sensor.a': 'relevant', 'sensor.b': 'bad'}),
                                  (0, {}), (0, {'invalid': 'relevant'})]:
            with self.assertRaises(InvalidSelection):
                await self.store.patch('example', revision, changes)
        self.assertEqual({}, (await self.store.get('example'))['decisions'])

    async def test_concurrent_writes_and_journal(self):
        results = await asyncio.gather(
            self.store.patch('example', 0, {'sensor.a': 'relevant'}),
            self.store.patch('example', 0, {'sensor.a': 'ignored'}),
            return_exceptions=True)
        self.assertEqual(1, sum(isinstance(r, SelectionConflict) for r in results))
        saved = await self.store.get('example')
        with sqlite3.connect(self.store.path) as db:
            rows = db.execute('SELECT revision, changes FROM selection_journal').fetchall()
        self.assertEqual(1, len(rows))
        self.assertEqual(1, rows[0][0])
        self.assertEqual({'before': 'unreviewed', 'after': saved['decisions']['sensor.a']},
                         json.loads(rows[0][1])['sensor.a'])

    async def test_future_schema_refused_without_overwrite(self):
        with sqlite3.connect(self.store.path) as db:
            db.execute('PRAGMA user_version=4')
        with self.assertRaises(RuntimeError):
            await self.store.initialize()
        with sqlite3.connect(self.store.path) as db:
            self.assertEqual(4, db.execute('PRAGMA user_version').fetchone()[0])


class SelectionAPITests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        settings = Settings(data_dir=Path(self.temp.name),
                            options_path=Path(self.temp.name) / 'options.json',
                            golden_zone_area_ids=('example',), supervisor_token='',
                            refresh_interval_seconds=3600, ingress_allowed_peers=('127.0.0.1',))
        self.app = create_app(settings)
        self.client = TestClient(TestServer(self.app))
        await self.client.start_server()
        self.addAsyncCleanup(self.client.close)
        self.entities = [
            {'entity_id': 'sensor.temperature', 'registry': {}, 'state': {'state': '20', 'attributes': {'device_class': 'temperature'}}},
            {'entity_id': 'button.identify', 'registry': {}, 'state': {}},
            {'entity_id': 'sensor.diagnostic', 'registry': {'entity_category': 'diagnostic'}, 'state': {}}]
        self.scope = AsyncMock(return_value={'entities': self.entities, 'resolved_area_ids': ['example']})
        for entity in self.entities:
            entity['area_id'] = 'example'
        self.app[SERVICE_KEY].world.scope = self.scope
        self.url = '/api/v1/selections/example'

    async def test_inventory_and_missing_reappearance(self):
        body = await (await self.client.get(self.url)).json()
        self.assertFalse(body['applied_to_inference'])
        self.assertEqual([True, False, False], [x['recommended'] for x in body['items']])
        self.assertTrue(all(x['decision'] == 'unreviewed' for x in body['items']))
        response = await self.client.patch(self.url, json={'revision': 0, 'changes': {'sensor.temperature': 'relevant'}})
        self.assertEqual(200, response.status)
        self.scope.return_value = {'entities': [], 'resolved_area_ids': ['example']}
        body = await (await self.client.get(self.url)).json()
        self.assertEqual([{'entity_id': 'sensor.temperature', 'decision': 'relevant'}], body['missing'])
        self.scope.return_value = {'entities': self.entities, 'resolved_area_ids': ['example']}
        body = await (await self.client.get(self.url)).json()
        self.assertEqual('relevant', body['items'][0]['decision'])

    async def test_validation_and_conflict(self):
        payload = {'revision': 0, 'changes': {'sensor.temperature': 'relevant'}}
        self.assertEqual(200, (await self.client.patch(self.url, json=payload)).status)
        self.assertEqual(409, (await self.client.patch(self.url, json=payload)).status)
        self.assertEqual(400, (await self.client.patch(self.url, json={'revision': 1, 'changes': {'sensor.foreign': 'relevant'}})).status)
        self.assertEqual(400, (await self.client.patch(self.url, data='{')).status)
        self.assertEqual(400, (await self.client.get('/api/v1/selections/other')).status)

    async def test_activation_filters_inference_and_can_be_reversed(self):
        service = self.app[SERVICE_KEY]
        from datetime import datetime, UTC
        service._connected = service._stream_connected = True
        service._last_refresh_at = datetime.now(UTC).isoformat()
        await service._derive()
        self.assertEqual(3, len(service._neurons))
        response = await self.client.patch(self.url, json={'revision': 0, 'changes': {'sensor.temperature': 'relevant'}, 'active': True})
        self.assertEqual(200, response.status)
        self.assertTrue((await response.json())['applied_to_inference'])
        self.assertEqual(['sensor.temperature'], [n.entity_id for n in service._neurons])
        self.assertEqual(3, len(service._scope['entities']))
        response = await self.client.patch(self.url, json={'revision': 1, 'changes': {'sensor.temperature': 'ignored'}})
        self.assertEqual(200, response.status)
        self.assertEqual([], service._neurons)
        self.assertTrue((await service.status())['ready'])
        self.assertEqual(0, (await service.status())['selection']['evaluated_count'])
        response = await self.client.patch(self.url, json={'revision': 2, 'changes': {}, 'active': False})
        self.assertEqual(200, response.status)
        self.assertEqual(3, len(service._neurons))
        self.assertEqual(400, (await self.client.patch(self.url, json={'revision': 3, 'changes': {}, 'active': None})).status)

    async def test_activation_persists_with_revision_conflict(self):
        store = self.app[SERVICE_KEY].selections
        await store.patch('example', 0, {}, True)
        restored = SelectionStore(Path(self.temp.name))
        await restored.initialize()
        self.assertTrue((await restored.get('example'))['active'])
        with self.assertRaises(SelectionConflict):
            await restored.patch('example', 0, {}, False)

    async def test_zone_isolation_new_entities_and_state_events(self):
        from dataclasses import replace
        service = self.app[SERVICE_KEY]
        service.settings = replace(service.settings, golden_zone_area_ids=('example', 'other'))
        # Use the real world model for this integration test, not inventory mocks.
        from pilotsuite.ha.world import WorldModel
        service.world = WorldModel()
        snapshot = {'areas': [{'area_id': 'example'}, {'area_id': 'other'}],
                    'entities': [{'entity_id': 'sensor.a', 'area_id': 'example'},
                                 {'entity_id': 'sensor.b', 'area_id': 'other'},
                                 {'entity_id': 'sensor.new', 'area_id': 'example'}],
                    'states': [{'entity_id': 'sensor.a', 'state': '20', 'attributes': {'device_class': 'temperature', 'unit_of_measurement': '°C'}}]}
        await service.world.replace(snapshot)
        other = await service.zones.save({'name': 'Other', 'area_ids': ['other'], 'extra_entity_ids': [], 'enabled': True, 'profile': 'observe'})
        await service.selections.patch(other['zone_id'], 1, {'sensor.b': 'relevant'})
        await service.selections.patch('example', 0, {'sensor.a': 'relevant'}, True)
        await service._derive()
        self.assertEqual({'sensor.a', 'sensor.b'}, {n.entity_id for n in service._neurons})
        await service._on_state_change({'entity_id': 'sensor.a', 'new_state': {'entity_id': 'sensor.a', 'state': '22', 'attributes': {'device_class': 'temperature', 'unit_of_measurement': '°C'}}})
        self.assertEqual(22, next(n.value for n in service._neurons if n.entity_id == 'sensor.a'))
        self.assertEqual({'example', other['zone_id']}, set((await service.status())['selection']['active_area_ids']))

    async def test_schema_migration_keeps_backup_and_decisions(self):
        store = self.app[SERVICE_KEY].selections
        await store.patch('example', 0, {'sensor.temperature': 'relevant'})
        with sqlite3.connect(store.path) as db:
            db.execute('DROP TABLE selection_modes')
            db.execute('DROP TABLE habitus_zones')
            db.execute('DROP TABLE zone_meta')
            db.execute('PRAGMA user_version=1')
        await store.initialize()
        saved = await store.get('example')
        self.assertFalse(saved['active'])
        self.assertEqual(1, saved['revision'])
        self.assertEqual('relevant', saved['decisions']['sensor.temperature'])
        backups = list(Path(self.temp.name).glob('selections.v1.*.bak'))
        self.assertEqual(1, len(backups))
        with sqlite3.connect(backups[0]) as db:
            self.assertEqual(1, db.execute('PRAGMA user_version').fetchone()[0])

    async def test_ingress_guard_covers_selection_writes(self):
        from dataclasses import replace
        service = self.app[SERVICE_KEY]
        service.settings = replace(service.settings, ingress_allowed_peers=('172.30.32.2',))
        response = await self.client.patch(self.url, json={'revision': 0, 'changes': {'sensor.temperature': 'relevant'}})
        self.assertEqual(403, response.status)
        self.assertEqual(0, (await service.selections.get('example'))['revision'])
