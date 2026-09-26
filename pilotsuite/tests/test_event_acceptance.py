"""Synthetic event ordering and consented context; no HA connection or actuators."""
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock

from pilotsuite.core.settings import Settings
from pilotsuite.ha.world import WorldModel
from pilotsuite.service import PilotSuiteService


def state(eid, value, at, attrs=None):
    return {'entity_id': eid, 'state': value, 'last_updated': at.isoformat(),
            'last_changed': at.isoformat(), 'attributes': attrs or {}}


class StateAcceptanceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.now = datetime.now(UTC)
        self.world = WorldModel()
        self.current = state('sensor.synthetic', '20', self.now)
        await self.world.replace({'entities': [{'entity_id': 'sensor.synthetic'}], 'states': [self.current]})

    async def test_newer_frame_returns_true_and_is_detached(self):
        new = state('sensor.synthetic', '21', self.now + timedelta(seconds=1))
        self.assertTrue(await self.world.update_state({'entity_id': 'sensor.synthetic', 'new_state': new}))
        new['state'] = '99'
        scope = await self.world.scope((), ('sensor.synthetic',))
        self.assertEqual('21', scope['entities'][0]['state']['state'])

    async def test_old_equal_and_duplicate_frames_are_not_new_observations(self):
        for at in (self.now - timedelta(seconds=1), self.now):
            with self.subTest(at=at):
                self.assertFalse(await self.world.update_state({'entity_id': 'sensor.synthetic',
                    'new_state': state('sensor.synthetic', '99', at)}))
        self.assertFalse(await self.world.update_state({'entity_id': 'sensor.synthetic', 'new_state': self.current}))

    async def test_malformed_undated_naive_and_misaddressed_frames_rejected(self):
        bad = [None, {}, {'entity_id': 'sensor.synthetic'},
               {'entity_id': 'sensor.synthetic', 'new_state': []},
               {'entity_id': 'sensor.synthetic', 'new_state': {'state': '21'}},
               {'entity_id': 'sensor.synthetic', 'new_state': state('sensor.other', '21', self.now)},
               {'entity_id': 'sensor.synthetic', 'new_state': state('sensor.synthetic', '21', datetime.now())}]
        for event in bad:
            with self.subTest(event=event):
                self.assertFalse(await self.world.update_state(event))
        self.assertTrue(await self.world.context_at_or_before(['sensor.synthetic'], self.now))

    async def test_removal_cannot_discard_a_newer_snapshot(self):
        for old in (None, state('sensor.synthetic', '19', self.now - timedelta(seconds=1)),
                    state('sensor.other', '20', self.now)):
            self.assertFalse(await self.world.update_state({'entity_id': 'sensor.synthetic', 'old_state': old, 'new_state': None}))
        self.assertTrue(await self.world.update_state({'entity_id': 'sensor.synthetic', 'old_state': self.current, 'new_state': None}))
        self.assertFalse(await self.world.context_at_or_before(['sensor.synthetic'], self.now))

    async def test_context_requires_all_sources_with_aware_nonfuture_timestamps(self):
        self.assertTrue(await self.world.context_at_or_before(['sensor.synthetic'], self.now))
        self.assertFalse(await self.world.context_at_or_before(['sensor.synthetic'], self.now - timedelta(seconds=1)))
        self.assertFalse(await self.world.context_at_or_before(['sensor.synthetic', 'sensor.missing'], self.now))
        self.assertFalse(await self.world.context_at_or_before([], self.now))
        self.assertFalse(await self.world.context_at_or_before(['sensor.synthetic'], self.now.replace(tzinfo=None)))


class EventLearningAcceptanceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.service = PilotSuiteService(Settings(root, root/'options.json', supervisor_token=''))
        await self.service.selections.initialize()
        await self.service.zones.bootstrap(('a',))
        self.now = datetime.now(UTC)
        self.earlier = self.now - timedelta(seconds=30)
        self.snapshot = {'areas': [{'area_id': 'a'}], 'entities': [
            {'entity_id': e, 'area_id': 'a'} for e in ('binary_sensor.motion', 'light.room', 'sensor.lux')],
            'states': [state('binary_sensor.motion', 'off', self.earlier, {'device_class': 'motion'}),
                       state('light.room', 'on', self.earlier),
                       state('sensor.lux', '25', self.earlier, {'device_class': 'illuminance', 'unit_of_measurement': 'lx'})]}
        await self.service.world.replace(deepcopy(self.snapshot))
        await self.service.selections.patch('a', 0, {e['entity_id']: 'relevant' for e in self.snapshot['entities']})
        self.roles = {'presence': ['binary_sensor.motion'], 'light': ['light.room'], 'illuminance': ['sensor.lux']}
        await self.service.context.configure('a', 1, self.roles, True, context_learning=True,
                                             now=(self.earlier - timedelta(seconds=30)).timestamp())
        self.service._connected = self.service._stream_connected = True
        self.service._last_refresh_at = self.now.isoformat()
        await self.service._derive()
        for name in ('snapshot', 'call_bounded_service', 'helper_create_timer', 'helper_delete_timer'):
            setattr(self.service.client, name, AsyncMock(side_effect=AssertionError('No HA I/O in evidence tests')))

    async def asyncTearDown(self):
        for name in ('snapshot', 'call_bounded_service', 'helper_create_timer', 'helper_delete_timer'):
            getattr(self.service.client, name).assert_not_awaited()
        await self.service.client.close()
        self.tmp.cleanup()

    def event(self, at):
        return {'entity_id': 'binary_sensor.motion', 'old_state': self.snapshot['states'][0],
                'new_state': state('binary_sensor.motion', 'on', at, {'device_class': 'motion'})}

    async def test_rejected_older_frame_cannot_record_learning_or_newer_context(self):
        self.snapshot['states'][0] = state('binary_sensor.motion', 'off', self.now, {'device_class': 'motion'})
        self.snapshot['states'][2] = state('sensor.lux', '900', self.now, {'device_class': 'illuminance', 'unit_of_measurement': 'lx'})
        await self.service.world.replace(self.snapshot)
        await self.service._on_state_change(self.event(self.now - timedelta(seconds=10)))
        report = await self.service.context.report('a')
        self.assertEqual(0, report['event_count'])
        self.assertEqual([], report['context_evidence'])

    async def test_fresh_event_retains_context_and_duplicate_is_ignored(self):
        event = self.event(self.now)
        await self.service._on_state_change(event)
        await self.service._on_state_change(event)
        report = await self.service.context.report('a')
        self.assertEqual(1, report['event_count'])
        context = report['context_evidence'][0]['context']
        self.assertTrue(context['light']['value'])
        self.assertEqual(25, context['illuminance']['value'])
        self.assertEqual('at_or_before_event', context['light']['timing'])

    async def test_accepted_delay_keeps_activity_but_not_a_later_lux_value(self):
        self.snapshot['states'][2] = state('sensor.lux', '900', self.now, {'device_class': 'illuminance', 'unit_of_measurement': 'lx'})
        await self.service.world.replace(self.snapshot)
        await self.service._on_state_change(self.event(self.now - timedelta(seconds=10)))
        report = await self.service.context.report('a')
        self.assertEqual(1, report['event_count'])
        context = report['context_evidence'][0]['context']
        self.assertTrue(context['light']['value'])
        self.assertIsNone(context['illuminance']['value'])
        self.assertEqual('unknown', context['illuminance']['status'])
        self.assertEqual('unverified', context['illuminance']['timing'])

    async def test_missing_context_timestamps_do_not_become_measurements(self):
        for item in self.snapshot['states'][1:]:
            item.pop('last_updated')
        await self.service.world.replace(self.snapshot)
        await self.service._on_state_change(self.event(self.now))
        report = await self.service.context.report('a')
        self.assertEqual(1, report['event_count'])
        for kind in ('light', 'illuminance'):
            self.assertIsNone(report['context_evidence'][0]['context'][kind]['value'])

    async def test_no_context_consent_collects_no_context_or_additional_data(self):
        rev = (await self.service.selections.get('a'))['revision']
        await self.service.context.configure('a', rev, self.roles, True, context_learning=False)
        await self.service._on_state_change(self.event(self.now))
        report = await self.service.context.report('a')
        self.assertEqual(1, report['event_count'])
        self.assertEqual([], report['context_evidence'])

if __name__ == '__main__':
    unittest.main()
