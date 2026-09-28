"""Actual SQLite/service checks with synthetic sources; never contact household HA."""
import asyncio
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from aiohttp.test_utils import TestClient, TestServer

from pilotsuite.app import SERVICE_KEY, create_app
from pilotsuite.core.context import ContextStore
from pilotsuite.core.settings import Settings
from test_presence_shadow import MOTION, NOW, SOURCE, seed_shadow, state


class ZonePresenceRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.now = NOW
        self.clock = patch('time.time', side_effect=lambda: self.now)
        self.clock.start()
        self.app = create_app(Settings(root, root / 'options.json',
            golden_zone_area_ids=('room',), supervisor_token='',
            refresh_interval_seconds=3600, ingress_allowed_peers=('127.0.0.1',)))
        self.http = TestClient(TestServer(self.app))
        await self.http.start_server()
        self.service = self.app[SERVICE_KEY]
        for task in self.service._tasks:
            task.cancel()
        await asyncio.gather(*self.service._tasks, return_exceptions=True)
        self.service._tasks = []
        self.world = await seed_shadow(self.service, self.now)
        self.spec = {'grace_seconds': 30, 'clear_seconds': 0,
                     'support_limit_seconds': 60, 'comparison_entity': None,
                     'sources': [{'entity_id': eid, 'kind': kind, 'required': False,
                                  'max_age': 0, 'group': eid, 'can_start': True,
                                  'active_states': ['on']}
                                 for eid, kind in ((SOURCE, 'continuous'), (MOTION, 'pulse'))]}
        self.service.client.zone_output_service = AsyncMock()
        await self.service.zone_presence_configure('room',
            {'revision': 2, 'mode': 'compare', 'spec': self.spec})

    async def asyncTearDown(self):
        for name in ('history', 'call_bounded_service', 'helper_create_timer',
                     'helper_delete_timer', 'organization_set_name', 'automation_config',
                     'related_automations'):
            getattr(self.service.client, name).assert_not_awaited()
        await self.http.close()
        self.clock.stop()
        self.temp.cleanup()

    async def tick(self, seconds=0, values=None):
        self.now += seconds
        for eid, value in (values or {}).items():
            row = next(item for item in self.world['states'] if item['entity_id'] == eid)
            row.update(state(eid, value, self.now, row['attributes']))
        await self.service.world.replace(deepcopy(self.world))
        self.service._last_refresh_at = datetime.fromtimestamp(self.now, UTC).isoformat()
        async with self.service._projection_lock:
            await self.service._zone_presence_tick_locked()
        return await self.service.zone_presence_view('room')

    async def test_all_optional_outage_survives_restart_without_false_free_or_new_grace(self):
        await self.tick(1, {SOURCE: 'on'})
        result = await self.tick(1, {SOURCE: 'off'})
        deadline = result['current']['deadline']
        result = await self.tick(40, {SOURCE: 'unavailable', MOTION: 'unavailable'})
        self.assertEqual('unknown', result['current']['state'])
        self.assertFalse(result['current']['valid'])
        self.service.context = ContextStore(self.service.selections)
        self.service._zone_presence_init()
        result = await self.tick(1)
        self.assertEqual('unknown', result['current']['state'])
        self.assertEqual(deadline, result['current']['deadline'])
        saved = await self.service.context.zone_operational('room')
        self.assertEqual(deadline, saved['checkpoint']['kernel']['deadline'])
        response = await self.http.get('/api/v1/zones/room/presence')
        self.assertEqual(200, response.status)
        self.assertIsNone((await response.json())['current']['occupied'])
        result = await self.tick(1, {SOURCE: 'off'})
        self.assertEqual('vacant', result['current']['state'])
        self.service.client.zone_output_service.assert_not_awaited()

    async def test_optional_outage_invalidates_publication_without_clearing_owner(self):
        await self.tick(1, {SOURCE: 'on'})
        await self.tick(1, {SOURCE: 'off'})
        await self.tick(40, {SOURCE: 'unavailable', MOTION: 'unavailable'})
        entities = {'anwesenheit_intern': 'input_boolean.synthetic_owner',
                    'entscheidung_gueltig': 'input_boolean.synthetic_valid',
                    'gueltig_bis': 'input_datetime.synthetic_until',
                    'nachlauf': 'timer.synthetic_grace',
                    'sensor': 'binary_sensor.synthetic_presence'}
        identities = {role: {'entity_id': eid, 'platform': eid.split('.')[0],
                             'unique_id': eid} for role, eid in entities.items()}
        self.service.client.zone_output_registry = AsyncMock(return_value=list(identities.values()))
        self.service.client.zone_output_states = AsyncMock(
            side_effect=AssertionError('Unknown presence must not attempt a Boolean publication'))
        view = self.service._zone_views['room']
        await self.service._zone_publish('room',
            {'package': {'entities': entities, 'identities': identities}}, view, view['current'])
        self.service.client.zone_output_service.assert_awaited_once_with(
            'input_boolean', 'turn_off', entities['entscheidung_gueltig'])
        self.service.client.zone_output_states.assert_not_awaited()


if __name__ == '__main__':
    unittest.main()
