"""Existing household control stays read-only; all identities below are synthetic."""
import asyncio
from copy import deepcopy
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import AsyncMock
from aiohttp.test_utils import TestClient, TestServer
from pilotsuite.app import create_app, SERVICE_KEY
from pilotsuite.core.context import ContextStore
from pilotsuite.core.organization import bind_request
from pilotsuite.core.presence_adoption import existing_presence_view
from pilotsuite.core.selections import InvalidSelection, SelectionConflict
from pilotsuite.core.settings import Settings
from pilotsuite.core.zone_presence_store import KEY
from pilotsuite.ha.client import HomeAssistantError
from organization_support import seed, payload

OWNER = 'input_boolean.legacy_presence'
TIMER = 'timer.legacy_wait'
SENSOR = 'binary_sensor.room_derived'
SOURCE = 'binary_sensor.room_motion'


class ExistingPresenceProjectionTests(unittest.TestCase):
    def setUp(self):
        self.catalog = [{'entity_id': eid, 'name': eid, 'platform': eid.split('.')[0],
            'unique_id': eid, 'in_registry': True, 'disabled': False, 'device_class': 'occupancy'}
            for eid in (OWNER, TIMER, SENSOR)]
        self.config = {'organization': bind_request({'revision': 0, 'confirm': True,
            'timing': 'timer', 'assignments': {'presence_status': [OWNER],
            'presence_timer': [TIMER], 'presence_output': [SENSOR]}}, self.catalog, {})}
        self.observations = {OWNER: {'state': 'on'}, SENSOR: {'state': 'on'},
            TIMER: {'state': 'active', 'attributes': {'finishes_at': '2026-01-01T00:02:00+00:00'}}}
        self.now = 1767225600

    def view(self, **kwargs):
        return existing_presence_view(self.config, self.catalog, self.observations,
            kwargs.pop('current', {'occupied': True, 'valid': True}),
            fresh=kwargs.pop('fresh', True), now=self.now, **kwargs)

    def test_chain_and_timer_are_observed_not_actuated(self):
        view = self.view()
        self.assertEqual('existing_automations', view['authority'])
        self.assertFalse(view['control_enabled'])
        self.assertEqual('same', view['comparison'])
        self.assertEqual(120, view['timer']['remaining_seconds'])
        self.observations[TIMER]['state'] = 'idle'
        self.assertIsNone(self.view()['timer']['remaining_seconds'])
        self.assertEqual('on', self.view()['sensor']['state'], 'Idle never implies vacancy')

    def test_missing_stale_invalid_or_owned_output_cannot_confirm_comparison(self):
        for value in ('unknown', 'unavailable', None, 'unexpected'):
            self.observations[SENSOR]['state'] = value
            view = self.view()
            self.assertEqual('unknown', view['sensor']['state'])
            self.assertEqual('unassessable', view['comparison'], 'Do not fall back to Boolean')
        self.observations[SENSOR]['state'] = 'on'
        for params in ({'fresh': False}, {'current': None}, {'current': {'occupied': False, 'valid': False}},
                       {'owned': [SENSOR]}):
            self.assertEqual('unassessable', self.view(**params)['comparison'])
        self.assertEqual('unknown', self.view(fresh=False)['owner']['state'])

    def test_mismatch_is_visible_and_identity_replacement_is_not_adopted(self):
        self.observations[SENSOR]['state'] = 'off'
        self.assertEqual('different', self.view()['comparison'])
        self.assertEqual('different', self.view()['chain_consistency'])
        self.catalog[-1]['unique_id'] = 'replacement'
        self.assertEqual('identity_unresolved', self.view()['sensor']['binding_status'])
        self.assertEqual('unknown', self.view()['sensor']['state'])

    def test_renamed_stable_identity_resolves_without_changing_saved_binding(self):
        renamed = 'binary_sensor.renamed'
        self.catalog[-1]['entity_id'] = renamed
        self.observations[renamed] = self.observations.pop(SENSOR)
        view = self.view()
        self.assertEqual(renamed, view['sensor']['entity_id'])
        self.assertEqual(SENSOR, view['sensor']['saved_entity_id'])
        self.assertEqual('same', view['comparison'])

    def test_timer_without_deadline_and_partial_chain_remain_explicit(self):
        for value in ('paused', 'idle', 'unavailable'):
            self.observations[TIMER]['state'] = value
            self.assertIsNone(self.view()['timer']['finishes_at'])
        del self.config['organization']['assignments']['presence_output']
        self.assertIsNone(self.view()['sensor'])
        self.assertEqual('owner', self.view()['comparison_reference'])
        self.assertEqual('unassessable', self.view()['chain_consistency'])

    def test_changed_public_sensor_semantics_are_not_silently_accepted(self):
        self.catalog[-1]['device_class'] = 'door'
        self.assertEqual('unknown', self.view()['sensor']['state'])
        self.assertEqual('unassessable', self.view()['comparison'])


class ExistingPresenceIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.app = create_app(Settings(root, root/'options.json', golden_zone_area_ids=('room', 'other'),
            supervisor_token='', refresh_interval_seconds=3600, ingress_allowed_peers=('127.0.0.1',)))
        self.http = TestClient(TestServer(self.app))
        await self.http.start_server()
        self.s = self.app[SERVICE_KEY]
        for task in self.s._tasks:
            task.cancel()
        await asyncio.gather(*self.s._tasks, return_exceptions=True)
        self.s._tasks = []
        await seed(self.s)
        self.s.client.related_automations = AsyncMock(return_value={SENSOR: ['automation.audit_01']})
        self.s.client.zone_output_service = AsyncMock(side_effect=AssertionError('No output control'))
        self.s.client.zone_create_storage_helper = AsyncMock(side_effect=AssertionError('No helper create'))
        self.s.client.zone_create_binary_sensor = AsyncMock(side_effect=AssertionError('No sensor create'))
        self.s.client.zone_set_metadata = AsyncMock(side_effect=AssertionError('No rename'))
        self.spec = {'grace_seconds': 30, 'clear_seconds': 0, 'support_limit_seconds': 60,
            'comparison_entity': None, 'sources': [{'entity_id': SOURCE, 'kind': 'pulse',
                'required': True, 'max_age': 0, 'group': SOURCE, 'can_start': True, 'active_states': ['on']}]}
        await self.s.selections.patch('room', 0, {SOURCE: 'relevant', SENSOR: 'relevant'})
        await self.s.zone_presence_configure('room', {'revision': await self.revision(),
            'spec': self.spec, 'mode': 'compare'})
        self.base = '/api/v1/zones/room/'

    async def asyncTearDown(self):
        for name in ('call_bounded_service', 'organization_set_name', 'helper_create_timer',
                     'zone_output_service', 'zone_create_storage_helper', 'zone_create_binary_sensor', 'zone_set_metadata'):
            getattr(self.s.client, name).assert_not_awaited()
        await self.http.close()
        self.temp.cleanup()

    async def revision(self):
        return (await self.s.selection_inventory('room'))['revision']

    async def bind(self):
        body = payload(await self.revision())
        body['assignments']['presence_output'] = [SENSOR]
        body['assignments']['presence_automations'].append('automation.audit_02')
        result = await self.http.patch(self.base+'organization', json=body)
        self.assertEqual(200, result.status, await result.text())

    async def test_saved_binding_survives_restart_and_preserves_behavior_roles_and_other_zone(self):
        before = await self.s.context.get('room')
        other = await self.s.context.get('other')
        await self.bind()
        self.s.context = ContextStore(self.s.selections)
        after = await self.s.context.get('room')
        for key in (KEY, 'roles', 'learning'):
            self.assertEqual(before[key], after[key])
        self.assertEqual(other, await self.s.context.get('other'))
        result = await self.http.get(self.base+'presence')
        self.assertEqual(200, result.status)
        existing = (await result.json())['existing']
        self.assertEqual(SENSOR, existing['sensor']['entity_id'])
        self.assertEqual('off', existing['sensor']['state'])
        self.s.client.automation_config.assert_not_awaited()
        self.s.client.related_automations.assert_not_awaited()

    async def test_review_without_legacy_runtime_includes_writer_consumer_and_selected_unmatched(self):
        await self.bind()
        async def config(eid):
            if eid == 'automation.legacy_presence':
                return {'triggers': [{'trigger': 'state', 'entity_id': SOURCE, 'to': 'on'}],
                    'actions': [{'action': 'input_boolean.turn_on', 'target': {'entity_id': OWNER}},
                                {'action': 'timer.start', 'target': {'entity_id': TIMER}}]}
            if eid == 'automation.audit_01':
                return {'conditions': [{'condition': 'state', 'entity_id': SENSOR, 'state': 'on'}],
                    'actions': [{'action': 'light.turn_on', 'target': {'entity_id': 'light.synthetic'}}]}
            return {'triggers': [{'trigger': 'time', 'at': '08:00:00'}], 'actions': []}
        self.s.client.automation_config.side_effect = config
        before = await self.s.context.get('room')
        result = await self.http.post(self.base+'presence-adoption/review', json={'revision': await self.revision()})
        self.assertEqual(200, result.status, await result.text())
        report = await result.json()
        self.assertEqual('existing_control', report['mode'])
        self.assertFalse(report['execution']['allowed'])
        self.assertFalse(report['persisted'])
        self.assertEqual({'writer', 'consumer', 'unrelated'}, {r['usage'] for r in report['automations']})
        self.assertTrue(all(r['observed_enabled'] is True for r in report['automations']))
        self.assertEqual(before, await self.s.context.get('room'))
        self.assertEqual({}, before['roles'])
        self.assertIn(SENSOR, self.s.client.related_automations.await_args.args[0])

    async def test_revision_or_disconnect_during_review_discards_result(self):
        await self.bind()
        async def config(_):
            self.s._stream_connected = False
            return {'triggers': [], 'actions': []}
        self.s.client.automation_config.side_effect = config
        with self.assertRaises(SelectionConflict):
            await self.s.presence_adoption_review('room', {'revision': await self.revision()})
        self.s._stream_connected = True
        async def changed(_):
            await self.s.context.configure('room', await self.revision(), {}, False)
            return {'triggers': [], 'actions': []}
        self.s.client.automation_config.side_effect = changed
        with self.assertRaises(SelectionConflict):
            await self.s.presence_adoption_review('room', {'revision': await self.revision()})

    async def test_unread_automation_never_yields_a_clean_partial_review(self):
        await self.bind()
        self.s.client.automation_config.side_effect = HomeAssistantError('unread')
        with self.assertRaises(HomeAssistantError):
            await self.s.presence_adoption_review('room', {'revision': await self.revision()})

    async def test_configuring_a_bound_output_as_an_input_is_rejected(self):
        await self.bind()
        spec = deepcopy(self.spec)
        spec['sources'].append({**spec['sources'][0], 'entity_id': SENSOR,
            'kind': 'support', 'required': False, 'group': SENSOR})
        with self.assertRaises(InvalidSelection):
            await self.s.zone_presence_configure('room', {'revision': await self.revision(),
                'spec': spec, 'mode': 'compare'})

    async def test_binding_an_existing_input_as_output_is_rejected(self):
        spec = deepcopy(self.spec)
        spec['sources'].append({**spec['sources'][0], 'entity_id': SENSOR,
            'kind': 'support', 'required': False, 'group': SENSOR})
        await self.s.zone_presence_configure('room', {'revision': await self.revision(), 'spec': spec, 'mode': 'compare'})
        body = payload(await self.revision())
        body['assignments']['presence_output'] = [SENSOR]
        with self.assertRaises(InvalidSelection):
            await self.s.organization_save('room', body)

    async def test_disconnected_projection_keeps_unknown_not_free(self):
        await self.bind()
        self.s._stream_connected = False
        result = (await self.s.zone_presence_view('room'))['existing']
        self.assertEqual('unknown', result['owner']['state'])
        self.assertEqual('unknown', result['sensor']['state'])
        self.assertEqual('unassessable', result['comparison'])
