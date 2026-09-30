"""Actual SQLite/service checks with synthetic sources; never contact household HA."""
import asyncio
from contextlib import closing
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from aiohttp.test_utils import TestClient, TestServer

from pilotsuite.app import SERVICE_KEY, create_app
from pilotsuite.core.context import ContextStore
from pilotsuite.core.settings import Settings
from pilotsuite.core.zone_presence_store import KEY
from pilotsuite.ha.client import HomeAssistantError
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

    async def test_relevant_zone_anchor_is_excluded_from_defaults_and_explicit_inputs(self):
        self.service.client.zone_labels=AsyncMock(return_value=[{'label_id':'room','name':'Room'},
            {'label_id':'anchor','name':'Habitus Zone'}])
        response=await self.http.post('/api/v1/zones',json={'definition':{'name':'Anchor check','area_ids':['room'],
            'extra_entity_ids':[],'enabled':True,'profile':'observe'},'setup':{'label_id':'room',
            'entity_ids':[SOURCE,MOTION],'relevant_entity_ids':[MOTION],'roles':{SOURCE:['Habitus Zone'],MOTION:[]}}})
        self.assertEqual(201,response.status,await response.text())
        zid=(await response.json())['zone_id']
        # The older selection path may mark a status relevant for read-only history.
        response=await self.http.patch('/api/v1/selections/'+zid,json={'revision':1,'changes':{SOURCE:'relevant'}})
        self.assertEqual(200,response.status,await response.text())
        await self.tick(1,{SOURCE:'on'})
        view=await self.service.zone_presence_view(zid)
        self.assertNotIn(SOURCE,{row['entity_id'] for row in view['spec']['sources']})
        self.assertEqual('unknown',view['current']['state'],'output on cannot establish an occupied or vacant zone')
        self.assertTrue(next(row for row in view['catalog'] if row['entity_id']==SOURCE)['presence_input_excluded'])
        before=await self.service.context.get(zid)
        response=await self.http.put('/api/v1/zones/'+zid+'/presence',json={
            'revision':view['revision'],'spec':self.spec,'mode':'compare'})
        self.assertEqual(400,response.status,await response.text())
        self.assertEqual(before,await self.service.context.get(zid))
        safe=deepcopy(self.spec);safe['sources']=[row for row in safe['sources'] if row['entity_id']!=SOURCE]
        safe['comparison_entity']=SOURCE
        response=await self.http.put('/api/v1/zones/'+zid+'/presence',json={
            'revision':view['revision'],'spec':safe,'mode':'compare'})
        self.assertEqual(200,response.status,await response.text())
        self.assertEqual(SOURCE,(await response.json())['spec']['comparison_entity'])
        self.service.client.zone_output_service.assert_not_awaited()

    async def test_runtime_rechecks_anchor_role_in_an_existing_legacy_source_config(self):
        from pilotsuite.core.organization import identity
        await self.tick(1,{SOURCE:'on'})
        self.assertEqual('occupied',(await self.service.zone_presence_view('room'))['current']['state'])
        zone=next(row for row in await self.service.zones.list() if row['zone_id']=='room')
        definition={k:zone[k] for k in ('name','area_ids','extra_entity_ids','enabled','profile')}
        catalog=await self.service.world.organization_catalog()
        # A persisted legacy selection may predate the editor's anchor guard.
        profile={'schema':'pilotsuite-zone-structure-v1','label_id':'legacy_fixture',
            'members':{SOURCE:{'identity':identity(next(row for row in catalog if row['entity_id']==SOURCE)),
                               'roles':['Habitus Zone']}}}
        await self.service.zones.save(definition,'room',zone['revision'],setup=profile,relevant=[SOURCE])
        for restarted in (False,True):
            if restarted:
                self.service.context=ContextStore(self.service.selections)
                self.service._zone_views.clear()
            await self.tick(1)
            view=await self.service.zone_presence_view('room')
            self.assertIsNone(view['current'])
            self.assertEqual('configuration_required',view['status'])
            self.assertIsNone(view['lighting']['current'])
        self.service.client.zone_output_service.assert_not_awaited()

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

    async def test_unchanged_configuration_preserves_grace_and_saved_basis(self):
        await self.tick(1, {SOURCE: 'on'})
        before = await self.tick(1, {SOURCE: 'off'})
        self.assertEqual('grace', before['current']['state'])
        config = await self.service.context.get('room')
        checkpoint = await self.service.context.zone_operational('room')
        with (patch.object(self.service.context, 'save_zone_presence',
                           wraps=self.service.context.save_zone_presence) as writes,
              patch.object(self.service, '_zone_presence_tick_locked',
                           wraps=self.service._zone_presence_tick_locked) as evaluations):
            for _ in range(3):
                response = await self.http.put('/api/v1/zones/room/presence', json={
                    'revision': before['revision'], 'mode': 'compare', 'spec': self.spec})
                self.assertEqual(200, response.status)
                after = await response.json()
                self.assertEqual(before['current']['deadline'], after['current']['deadline'])
                self.assertEqual(before['revision'], after['revision'])
                self.assertEqual(before['current'], after['current'])
            writes.assert_not_awaited()
            evaluations.assert_not_awaited()
        self.assertEqual(config, await self.service.context.get('room'))
        self.assertEqual(checkpoint, await self.service.context.zone_operational('room'))
        self.service.context = ContextStore(self.service.selections)
        self.service._zone_presence_init()
        after = await self.tick(5)
        self.assertEqual('grace', after['current']['state'])
        self.assertEqual(before['current']['deadline'], after['current']['deadline'])
        after = await self.tick(25)
        self.assertEqual('vacant', after['current']['state'])
        self.service.client.zone_output_service.assert_not_awaited()

    async def test_unchanged_publish_configuration_does_not_invalidate_outputs(self):
        await self.prepare_publisher()
        await self.service._zone_publish_all()
        before = await self.service.zone_presence_view('room')
        checkpoint = await self.service.context.zone_operational('room')
        calls = self.service.client.zone_output_service.await_count
        response = await self.http.put('/api/v1/zones/room/presence', json={
            'revision': before['revision'], 'mode': 'publish', 'spec': before['spec']})
        self.assertEqual(200, response.status)
        after = await response.json()
        self.assertEqual(calls, self.service.client.zone_output_service.await_count)
        self.assertEqual(before['revision'], after['revision'])
        self.assertEqual('verified', after['publication'])
        self.assertEqual(before['publication_checked_at'], after['publication_checked_at'])
        self.assertEqual(checkpoint, await self.service.context.zone_operational('room'))

    async def test_unchanged_save_does_not_freshen_stale_or_disconnected_evidence(self):
        for failure in ('age', 'disconnect'):
            with self.subTest(failure=failure):
                await self.prepare_publisher()
                await self.service._zone_publish_all()
                before = await self.service.zone_presence_view('room')
                self.assertEqual('verified', before['publication'])
                receipt = deepcopy(self.service._zone_last_published)
                checkpoint = await self.service.context.zone_operational('room')
                calls = self.service.client.zone_output_service.await_count
                if failure == 'age':
                    self.now += 21
                else:
                    self.service._stream_connected = False
                after = await self.service.zone_presence_configure('room', {
                    'revision': before['revision'], 'mode': 'publish', 'spec': self.spec})
                self.assertEqual(before['revision'], after['revision'])
                self.assertIsNone(after['current'])
                self.assertNotEqual('verified', after['publication'])
                self.assertIsNone(after['publication_checked_at'])
                self.assertEqual(receipt, self.service._zone_last_published)
                self.assertEqual(checkpoint, await self.service.context.zone_operational('room'))
                self.assertEqual(calls, self.service.client.zone_output_service.await_count)

    async def test_configuration_changes_and_suspension_recovery_still_reset_session(self):
        for change in ('timing', 'mode', 'identity', 'suspended', 'output_suspended'):
            with self.subTest(change=change):
                await self.prepare_publisher()
                before = await self.service.zone_presence_view('room')
                config = (await self.service.context.get('room'))[KEY]
                payload = {'revision': before['revision'], 'mode': 'publish', 'spec': deepcopy(self.spec)}
                if change == 'timing':
                    payload['spec']['grace_seconds'] += 1
                elif change == 'mode':
                    payload['mode'] = 'compare'
                elif change == 'identity':
                    next(row for row in self.world['entities'] if row['entity_id'] == SOURCE)['unique_id'] += '_replaced'
                    await self.service.world.replace(deepcopy(self.world))
                else:
                    checkpoint = await self.service.context.zone_operational('room')
                    await self.service.context.save_zone_operational('room', before['revision'],
                        {**checkpoint, change: 'synthetic_failure'})
                after = await self.service.zone_presence_configure('room', payload)
                saved = (await self.service.context.get('room'))[KEY]
                self.assertEqual(before['revision'] + 1, after['revision'])
                self.assertNotEqual(config['session'], saved['session'])
                self.assertEqual(payload['spec'], saved['spec'])
                self.assertEqual(payload['mode'], saved['mode'])
                self.assertFalse((await self.service.context.zone_operational('room')).get('suspended'))
                self.assertFalse((await self.service.context.zone_operational('room')).get('output_suspended'))
                self.service.client.zone_output_service.assert_awaited_once_with(
                    'input_boolean', 'turn_off', self.entities['entscheidung_gueltig'])
                if change == 'identity':
                    self.assertNotEqual(config['basis'], saved['basis'])

    async def test_identical_save_still_validates_revision_and_configuration(self):
        before = await self.service.zone_presence_view('room')
        config = await self.service.context.get('room')
        for change, status in (('revision', 409), ('invalid_spec', 400), ('disabled_source', 400)):
            with self.subTest(change=change):
                payload = {'revision': before['revision'], 'mode': 'compare', 'spec': deepcopy(self.spec)}
                if change == 'revision':
                    payload['revision'] -= 1
                elif change == 'invalid_spec':
                    payload['spec']['grace_seconds'] = -1
                else:
                    next(row for row in self.world['entities'] if row['entity_id'] == SOURCE)['disabled_by'] = 'user'
                    await self.service.world.replace(deepcopy(self.world))
                response = await self.http.put('/api/v1/zones/room/presence', json=payload)
                self.assertEqual(status, response.status)
                self.assertEqual(config, await self.service.context.get('room'))
        self.service.client.zone_output_service.assert_not_awaited()

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

    async def test_suspended_basis_remains_explainable_beside_a_reserved_writer(self):
        await self.tick(1, {SOURCE: 'on'})
        next(row for row in self.world['entities'] if row['entity_id'] == SOURCE)['unique_id'] += '_replacement'
        before = await self.tick(1)
        self.assertEqual('source_basis_changed', before['status'])
        checkpoint = await self.service.context.zone_operational('room')
        connect = sqlite3.connect

        def short_timeout(*args, **kwargs):
            return connect(*args, **dict(kwargs, timeout=0.01))

        with closing(connect(self.service.context.path)) as writer, writer:
            writer.execute('BEGIN IMMEDIATE')
            with patch('sqlite3.connect', side_effect=short_timeout):
                after = await self.tick(1)
        self.assertEqual('source_basis_changed', after['status'])
        self.assertIsNone(after['current'])
        self.assertEqual(checkpoint, await self.service.context.zone_operational('room'))
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

    async def prepare_publisher(self, fault=None):
        """Bind synthetic outputs to real local storage; every HA call stays mocked."""
        self.entities = {'anwesenheit_intern': 'input_boolean.synthetic_owner',
                         'entscheidung_gueltig': 'input_boolean.synthetic_valid',
                         'gueltig_bis': 'input_datetime.synthetic_until',
                         'nachlauf': 'timer.synthetic_grace',
                         'sensor': 'binary_sensor.synthetic_presence'}
        identities = {role: {'entity_id': eid, 'platform': eid.split('.')[0],
                             'unique_id': eid} for role, eid in self.entities.items()}
        config = (await self.service.context.get('room'))[KEY]
        revision = (await self.service.selection_inventory('room'))['revision']
        await self.service.context.save_zone_presence('room', revision,
            {**config, 'mode': 'publish',
             'package': {'entities': self.entities, 'identities': identities}})
        self.service._zone_presence_init()
        self.service._stream_connected = True
        await self.tick(1, {SOURCE: 'on', MOTION: 'off'})
        self.output_states = {eid: {'state': 'off'} for eid in self.entities.values()}
        reads = 0

        async def inject(stage):
            if fault:
                await fault(stage)

        async def registry():
            await inject('registry')
            return deepcopy(list(identities.values()))

        async def states():
            nonlocal reads
            reads += 1
            await inject('states:' + str(reads))
            return deepcopy(self.output_states)

        async def output(domain, service, eid, data=None):
            role = next(role for role, target in self.entities.items() if target == eid)
            await inject(role + ':' + service)
            value = ('on' if service == 'turn_on' else 'off' if service == 'turn_off'
                     else 'active' if service == 'start' else 'idle' if service == 'cancel'
                     else data['timestamp'])
            self.output_states[eid] = {'state': value}
            valid = self.output_states[self.entities['entscheidung_gueltig']]['state'] == 'on'
            self.output_states[self.entities['sensor']] = {'state':
                self.output_states[self.entities['anwesenheit_intern']]['state'] if valid else 'unavailable'}

        self.service.client.zone_output_registry = AsyncMock(side_effect=registry)
        self.service.client.zone_output_states = AsyncMock(side_effect=states)
        self.service.client.zone_output_service = AsyncMock(side_effect=output)

    async def test_publication_rechecks_age_after_each_awaited_io(self):
        stages = ('registry', 'states:1', 'entscheidung_gueltig:turn_off',
                  'anwesenheit_intern:turn_on', 'nachlauf:cancel', 'states:2',
                  'gueltig_bis:set_datetime', 'entscheidung_gueltig:turn_on', 'states:3')
        for stage in stages:
            with self.subTest(stage=stage):
                fired = False

                async def delay(current):
                    nonlocal fired
                    if current == stage and not fired:
                        fired = True
                        self.now += 16

                await self.prepare_publisher(delay)
                await self.service._zone_publish_all()
                self.assertTrue(fired)
                self.assertEqual('off', self.output_states[self.entities['entscheidung_gueltig']]['state'])
                self.assertNotEqual('verified', self.service._zone_views['room'].get('publication'))
                self.assertTrue((await self.service.context.zone_operational('room'))['output_suspended'])
                calls = self.service.client.zone_output_service.await_args_list
                if stage in ('registry', 'states:1', 'entscheidung_gueltig:turn_off'):
                    self.assertFalse(any(c.args[2] == self.entities['anwesenheit_intern'] for c in calls))
                count = len(calls)
                await self.service._zone_publish_all()
                self.assertEqual(count, self.service.client.zone_output_service.await_count)

    async def test_publication_rechecks_disconnect_before_owner_and_validity(self):
        for stage in ('registry', 'states:1', 'gueltig_bis:set_datetime'):
            with self.subTest(stage=stage):
                async def disconnect(current):
                    if current == stage:
                        self.service._stream_connected = False

                await self.prepare_publisher(disconnect)
                await self.service._zone_publish_all()
                self.assertEqual('off', self.output_states[self.entities['entscheidung_gueltig']]['state'])
                self.assertNotEqual('verified', self.service._zone_views['room'].get('publication'))
                self.assertFalse(any(call.args[:3] == ('input_boolean', 'turn_on',
                    self.entities['entscheidung_gueltig'])
                    for call in self.service.client.zone_output_service.await_args_list))

    async def test_publication_conflict_preserves_newer_operational_checkpoint(self):
        newer = None

        async def advance_during_read(stage):
            nonlocal newer
            if stage == 'registry' and newer is None:
                await self.tick(1, {SOURCE: 'off'})
                newer = deepcopy((await self.service.context.zone_operational('room'))['checkpoint'])

        await self.prepare_publisher(advance_during_read)
        await self.service._zone_publish_all()
        saved = await self.service.context.zone_operational('room')
        self.assertIsNotNone(newer)
        self.assertEqual(newer, saved['checkpoint'])
        self.assertTrue(saved['output_suspended'])
        self.assertEqual('off', self.output_states[self.entities['entscheidung_gueltig']]['state'])

    async def test_current_publication_and_heartbeat_throttle_still_work(self):
        await self.prepare_publisher()
        await self.service._zone_publish_all()
        self.assertEqual('verified', self.service._zone_views['room']['publication'])
        self.assertEqual('on', self.output_states[self.entities['sensor']]['state'])
        calls = self.service.client.zone_output_service.await_count
        await self.tick(5)
        await self.service._zone_publish_all()
        self.assertEqual(calls, self.service.client.zone_output_service.await_count)

    async def test_unchanged_ticks_keep_dated_publication_evidence_without_more_io(self):
        await self.prepare_publisher()
        await self.service._zone_publish_all()
        verified_at = self.now
        calls = self.service.client.zone_output_service.await_count
        reads = self.service.client.zone_output_states.await_count
        registries = self.service.client.zone_output_registry.await_count
        for _ in range(3):
            await self.tick(5)
            await self.service._zone_publish_all()
            result = await self.service.zone_presence_view('room')
            self.assertEqual('verified', result['publication'])
            self.assertEqual(verified_at, result['publication_checked_at'])
            self.assertEqual(calls, self.service.client.zone_output_service.await_count)
            self.assertEqual(reads, self.service.client.zone_output_states.await_count)
            self.assertEqual(registries, self.service.client.zone_output_registry.await_count)
            self.assertEqual('on', self.output_states[self.entities['sensor']]['state'])
        await self.tick(5)
        await self.service._zone_publish_all()
        renewed = await self.service.zone_presence_view('room')
        self.assertEqual(self.now, renewed['publication_checked_at'])
        self.assertGreater(self.service.client.zone_output_states.await_count, reads)

    async def test_expired_or_changed_decision_does_not_reuse_publication_receipt(self):
        for case in ('expired', 'unknown', 'deadline', 'revision', 'disconnected', 'clock_rollback'):
            with self.subTest(case=case):
                await self.prepare_publisher()
                await self.service._zone_publish_all()
                if case == 'expired':
                    await self.tick(20)
                elif case == 'unknown':
                    await self.tick(1, {SOURCE: 'unavailable', MOTION: 'unavailable'})
                elif case == 'deadline':
                    await self.tick(1, {SOURCE: 'off'})
                elif case == 'revision':
                    revision = (await self.service.selection_inventory('room'))['revision']
                    await self.service.selections.patch('room', revision, {'sensor.synthetic_extra': 'ignored'})
                    await self.tick(1)
                elif case == 'disconnected':
                    self.service._stream_connected = False
                else:
                    self.now -= 1
                calls = self.service.client.zone_output_service.await_count
                before = deepcopy(await self.service.context.zone_operational('room'))
                result = await self.service.zone_presence_view('room')
                self.assertNotEqual('verified', result['publication'])
                self.assertIsNone(result.get('publication_checked_at'))
                self.assertEqual(before, await self.service.context.zone_operational('room'))
                self.assertEqual(calls, self.service.client.zone_output_service.await_count)

    async def test_failed_publication_cannot_revive_a_previous_receipt(self):
        await self.prepare_publisher()
        await self.service._zone_publish_all()
        await self.tick(1, {SOURCE: 'off'})
        self.service.client.zone_output_registry.side_effect = HomeAssistantError('synthetic registry failure')
        await self.service._zone_publish_all()
        self.assertTrue((await self.service.context.zone_operational('room'))['output_suspended'])
        await self.tick(1, {SOURCE: 'on'})  # Same signature as the old successful publication.
        result = await self.service.zone_presence_view('room')
        self.assertNotEqual('verified', result['publication'])
        self.assertIsNone(result['publication_checked_at'])
        self.assertNotIn('room', self.service._zone_last_published)

    async def test_receipt_is_dated_after_readback_and_not_retained_across_restart(self):
        async def delay(stage):
            if stage == 'registry':
                self.now += 5
        await self.prepare_publisher(delay)
        started = self.now
        await self.service._zone_publish_all()
        result = await self.service.zone_presence_view('room')
        self.assertEqual(started + 5, result['publication_checked_at'])
        self.service._zone_presence_init()
        await self.tick(1)
        result = await self.service.zone_presence_view('room')
        self.assertNotEqual('verified', result['publication'])
        self.assertIsNone(result['publication_checked_at'])


if __name__ == '__main__':
    unittest.main()
