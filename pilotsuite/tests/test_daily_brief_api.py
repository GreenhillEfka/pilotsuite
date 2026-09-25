"""Actual HTTP/context/store integration; all household data is synthetic."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from aiohttp.test_utils import TestClient, TestServer
from pilotsuite.app import SERVICE_KEY, create_app
from pilotsuite.core.settings import Settings
from fixtures.daily_brief import NOW, WORLD, database_snapshot, seed


class DailyBriefAPITests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        app = create_app(Settings(root, root/'options.json', golden_zone_area_ids=('a', 'b'),
            supervisor_token='', refresh_interval_seconds=3600, ingress_allowed_peers=('127.0.0.1',)))
        self.client = TestClient(TestServer(app)); await self.client.start_server()
        self.addAsyncCleanup(self.client.close)
        clock = patch('time.time', return_value=NOW); clock.start(); self.addCleanup(clock.stop)
        self.service = app[SERVICE_KEY]
        self.info = await seed(self.service)
        self.url = '/api/v1/zones/a/context'

    async def report(self, suffix=''):
        response = await self.client.get(self.url+suffix)
        self.assertEqual(200, response.status, await response.text())
        return await response.json()

    async def test_get_head_and_export_share_actual_projection_without_writes(self):
        before = database_snapshot(self.service)
        first = await self.report(); second = await self.report('/export')
        self.assertEqual(first['daily_brief'], second['daily_brief'])
        self.assertEqual(self.info['pattern_id'], first['daily_brief']['candidate']['pattern_id'])
        self.assertEqual({'zone_id': 'a', 'revision': first['revision']}, first['daily_brief']['candidate']['basis'])
        head = await self.client.head(self.url)
        self.assertEqual(200, head.status); self.assertEqual(b'', await head.read())
        self.assertEqual(before, database_snapshot(self.service))
        self.service.client.related_automations.assert_not_awaited()
        self.service.client.automation_config.assert_not_awaited()
        self.assertEqual({'allowed': False, 'actions': []}, first['daily_brief']['execution'])

    async def test_missing_coverage_withholds_without_losing_retained_pattern(self):
        from contextlib import closing
        import sqlite3
        with closing(sqlite3.connect(self.service.selections.path)) as db, db:
            db.execute('DELETE FROM coverage_checks WHERE zone_id=?', ('a',))
        result = await self.report()
        self.assertIsNone(result['daily_brief']['candidate'])
        self.assertEqual(1, len(result['patterns']))
        self.assertEqual('unknown', result['daily_brief']['coverage_state'])

    async def test_feedback_excludes_candidate_without_changing_observation_counts(self):
        before = await self.report()
        for decision, key in (('rejected', 'dismissed'), ('later', 'deferred')):
            response = await self.client.post('/api/v1/zones/a/feedback',
                json={'pattern_id': self.info['pattern_id'], 'decision': decision})
            self.assertEqual(200, response.status, await response.text())
            current = await response.json()
            self.assertIsNone(current['daily_brief']['candidate'])
            self.assertEqual(1, current['daily_brief']['excluded'][key])
            self.assertEqual(before['patterns'][0]['statistics'], current['patterns'][0]['statistics'])

    async def test_disconnect_and_unavailable_source_keep_retained_evidence(self):
        first = await self.report()
        self.service._stream_connected = False
        disconnected = await self.report()
        self.assertEqual('disconnected', disconnected['collection_state'])
        self.assertIsNone(disconnected['daily_brief']['candidate'])
        self.service._stream_connected = True
        world = copy.deepcopy(WORLD); world['states'][0]['state'] = 'unavailable'
        await self.service.world.replace(world); await self.service._derive()
        unavailable = await self.report()
        self.assertIsNone(unavailable['daily_brief']['candidate'])
        self.assertEqual(first['event_count'], unavailable['event_count'])

    async def test_pause_and_revoke_are_not_reenabled_by_get(self):
        first = await self.report()
        zone = next(z for z in await self.service.zones.list() if z['zone_id'] == 'a')
        definition = {k: zone[k] for k in ('name', 'area_ids', 'extra_entity_ids', 'enabled', 'profile')}
        await self.service.zones.save(dict(definition, enabled=False), 'a', first['revision'])
        await self.service._derive()
        result = await self.report()
        self.assertEqual('paused', result['collection_state']); self.assertIsNone(result['daily_brief']['candidate'])
        await self.service.context.configure('a', result['revision'], {'presence': ['binary_sensor.synthetic']}, False)
        before = database_snapshot(self.service)
        result = await self.report()
        self.assertFalse(result['config']['learning']); self.assertIsNone(result['daily_brief']['candidate'])
        self.assertEqual(before, database_snapshot(self.service))
        self.assertEqual(first['event_count'], result['event_count'])

    async def test_zone_isolation_unknown_zone_and_readonly_boundary(self):
        result = await (await self.client.get('/api/v1/zones/b/context')).json()
        self.assertEqual('b', result['daily_brief']['zone_id'])
        self.assertIsNone(result['daily_brief']['candidate']); self.assertEqual([], result['patterns'])
        self.assertEqual(400, (await self.client.get('/api/v1/zones/missing/context')).status)
        self.assertEqual(409, (await self.client.post('/api/v1/transactions/anything/apply')).status)
        self.assertEqual(405, (await self.client.post(self.url)).status)
