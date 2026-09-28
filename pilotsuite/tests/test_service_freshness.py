"""Deterministic snapshot-age contracts; no household connection or data."""
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

import test_zone_presence_runtime as runtime_fixture

from pilotsuite.core.settings import Settings
from pilotsuite.core import presence_kernel, presence_shadow, zone_presence
from pilotsuite.service import PilotSuiteService


class SnapshotFreshnessTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.service = PilotSuiteService(Settings(root, root / 'options.json',
            supervisor_token='', refresh_interval_seconds=30))
        self.service._connected = self.service._stream_connected = True
        self.now = datetime(2026, 9, 28, 6, tzinfo=UTC)
        self.datetime_patch = patch('pilotsuite.service.datetime', wraps=datetime)
        self.clock = self.datetime_patch.start()
        self.clock.now.return_value = self.now
        self.addCleanup(self.datetime_patch.stop)

    async def assert_fresh(self, expected):
        status = await self.service.status()
        self.assertIs(expected, status['home_assistant']['snapshot_fresh'])
        self.assertIs(expected, status['ready'])
        self.assertIs(expected, self.service._shadow_fresh(self.now.timestamp()))

    async def test_future_snapshot_never_reports_ready(self):
        for seconds in (0.001, 1, 60, 86400):
            with self.subTest(seconds=seconds):
                self.service._last_refresh_at = (self.now + timedelta(seconds=seconds)).isoformat()
                await self.assert_fresh(False)

    async def test_invalid_snapshot_degrades_without_status_exception(self):
        for stamp in (None, '', 'not-a-time', self.now.replace(tzinfo=None).isoformat(),
                      123, True, {}, self.now):
            with self.subTest(stamp=stamp):
                self.service._last_refresh_at = stamp
                await self.assert_fresh(False)

    async def test_existing_age_boundaries_match_presence_for_refresh_settings(self):
        for interval in (5, 30, 120, 3600):
            self.service.settings = replace(self.service.settings, refresh_interval_seconds=interval)
            limit = max(60, interval * 2)
            for age, expected in ((0, True), (1, True), (limit, True), (limit + 0.001, False)):
                with self.subTest(interval=interval, age=age):
                    self.service._last_refresh_at = (self.now - timedelta(seconds=age)).isoformat()
                    await self.assert_fresh(expected)

    async def test_explicit_offsets_describe_the_same_instant(self):
        for offset in (-7, 0, 2, 5.75):
            with self.subTest(offset=offset):
                self.service._last_refresh_at = (self.now - timedelta(seconds=30)).astimezone(
                    timezone(timedelta(hours=offset))).isoformat()
                await self.assert_fresh(True)

    async def test_transport_is_separate_from_snapshot_age(self):
        self.service._last_refresh_at = self.now.isoformat()
        for connected, stream in ((False, False), (False, True), (True, False), (True, True)):
            with self.subTest(connected=connected, stream=stream):
                self.service._connected, self.service._stream_connected = connected, stream
                status = await self.service.status()
                self.assertTrue(status['home_assistant']['snapshot_fresh'])
                self.assertIs(connected and stream, status['ready'])
                self.assertIs(connected and stream, self.service._shadow_fresh(self.now.timestamp()))

    def test_timestamp_parser_is_shared_without_changing_legacy_imports(self):
        self.assertIs(presence_kernel.timestamp, presence_shadow.timestamp)
        self.assertIs(presence_kernel.timestamp, zone_presence.timestamp)
        for value in (None, True, 123, {}, '', 'broken', '2026-02-29T00:00:00Z',
                      '2026-09-28', '2026-09-28T06:00:00'):
            with self.subTest(value=value):
                self.assertIsNone(presence_kernel.timestamp(value))
        for value in ('1970-01-01T00:00:00Z', '2024-02-29T00:00:00Z',
                      '2026-09-28T08:00:00+02:00', '2026-09-28T06:00:00.123456Z'):
            with self.subTest(value=value):
                self.assertEqual(datetime.fromisoformat(value).timestamp(), presence_kernel.timestamp(value))
        self.service._last_refresh_at = self.now.isoformat()
        for now in (None, True, 'broken', float('nan'), float('inf'), float('-inf')):
            with self.subTest(now=now):
                self.assertFalse(self.service._shadow_fresh(now))


class FreshnessIntegrationTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = runtime_fixture.ZonePresenceRuntimeTests.asyncSetUp
    asyncTearDown = runtime_fixture.ZonePresenceRuntimeTests.asyncTearDown
    tick = runtime_fixture.ZonePresenceRuntimeTests.tick
    prepare_publisher = runtime_fixture.ZonePresenceRuntimeTests.prepare_publisher

    async def test_zone_evaluation_view_and_publisher_do_not_depend_on_shadow_method(self):
        with patch.object(self.service, '_shadow_fresh', side_effect=AssertionError('Legacy shadow dependency')):
            await self.prepare_publisher()
            result = await self.service.zone_presence_view('room')
            self.assertEqual('occupied', result['current']['state'])
            await self.service._zone_publish_all()
            self.assertEqual('verified', self.service._zone_views['room']['publication'])
            self.assertEqual('on', self.output_states[self.entities['sensor']]['state'])

    async def test_http_readiness_and_status_degrade_for_invalid_time(self):
        now = datetime.fromtimestamp(self.now, UTC)
        with patch('pilotsuite.service.datetime', wraps=datetime) as clock:
            clock.now.return_value = now
            for stamp in ((now + timedelta(seconds=60)).isoformat(), 'broken',
                          now.replace(tzinfo=None).isoformat(), now):
                with self.subTest(stamp=stamp):
                    self.service._last_refresh_at = stamp
                    response = await self.http.get('/health/ready')
                    self.assertEqual(503, response.status, await response.text())
                    response = await self.http.get('/api/v1/status')
                    self.assertEqual(200, response.status, await response.text())
                    status = await response.json()
                    self.assertFalse(status['ready'])
                    self.assertEqual(stamp if isinstance(stamp, str) else None,
                                     status['home_assistant']['last_refresh_at'])

    async def test_bad_snapshot_blocks_legacy_evidence_not_event_processing(self):
        cfg = await self.service.context.get('room')
        revision = (await self.service.selection_inventory('room'))['revision']
        # Only this disposable database receives explicit legacy consent.
        await self.service.context.configure('room', revision, cfg['roles'], True)
        self.service.context.record = AsyncMock()
        with patch('pilotsuite.service.datetime', wraps=datetime) as clock:
            for label in ('future', 'malformed', 'naive', 'missing', 'current'):
                with self.subTest(label=label):
                    self.now += 1
                    now = datetime.fromtimestamp(self.now, UTC)
                    clock.now.return_value = now
                    self.service._last_refresh_at = {
                        'future': (now + timedelta(seconds=60)).isoformat(),
                        'malformed': 'broken', 'naive': now.replace(tzinfo=None).isoformat(),
                        'missing': None, 'current': now.isoformat()}[label]
                    await self.service.world.replace(deepcopy(self.world))
                    eid = runtime_fixture.MOTION
                    event = {'entity_id': eid,
                        'old_state': runtime_fixture.state(eid, 'off', self.now - 1),
                        'new_state': runtime_fixture.state(eid, 'on', self.now, {'device_class': 'motion'})}
                    self.service.context.record.reset_mock()
                    await self.service._on_state_change(event)
                    if label == 'current':
                        self.service.context.record.assert_awaited_once()
                    else:
                        self.service.context.record.assert_not_awaited()
                    scope = await self.service.world.scope((), (eid,))
                    self.assertEqual('on', scope['entities'][0]['state']['state'])
        self.service.client.zone_output_service.assert_not_awaited()


if __name__ == '__main__':
    unittest.main()
