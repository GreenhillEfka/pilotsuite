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
            db.execute('PRAGMA user_version=2')
        with self.assertRaises(RuntimeError):
            await self.store.initialize()
        with sqlite3.connect(self.store.path) as db:
            self.assertEqual(2, db.execute('PRAGMA user_version').fetchone()[0])


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

    async def test_ingress_guard_covers_selection_writes(self):
        from dataclasses import replace
        service = self.app[SERVICE_KEY]
        service.settings = replace(service.settings, ingress_allowed_peers=('172.30.32.2',))
        response = await self.client.patch(self.url, json={'revision': 0, 'changes': {'sensor.temperature': 'relevant'}})
        self.assertEqual(403, response.status)
        self.assertEqual(0, (await service.selections.get('example'))['revision'])
