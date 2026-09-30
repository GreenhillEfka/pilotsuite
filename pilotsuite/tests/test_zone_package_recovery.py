from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from aiohttp.test_utils import TestClient, TestServer

from pilotsuite.app import SERVICE_KEY, create_app
from pilotsuite.core.plans import PlanStore
from pilotsuite.core.settings import Settings
from pilotsuite.core.selections import InvalidSelection, SelectionConflict
from pilotsuite.ha.client import HomeAssistantError
from organization_support import seed


class ZonePackageRecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.app = create_app(Settings(root, root / 'options.json',
            golden_zone_area_ids=('room', 'other'), supervisor_token='',
            refresh_interval_seconds=3600, ingress_allowed_peers=('127.0.0.1',)))
        self.client = TestClient(TestServer(self.app))
        await self.client.start_server()
        self.service = self.app[SERVICE_KEY]
        await seed(self.service)
        await self.service.context.save_zone_presence('room', 0, {
            'spec': {'grace_seconds': 300}, 'mode': 'compare', 'package': None})
        self.rows = []
        self.storage_calls = []
        self.template_calls = []
        self.service.client.zone_output_registry = AsyncMock(side_effect=self._registry)
        self.service.client.zone_create_storage_helper = AsyncMock(side_effect=self._create_storage)
        self.service.client.zone_create_binary_sensor = AsyncMock(side_effect=self._create_template)
        self.service.client.zone_set_metadata = AsyncMock(side_effect=self._set_metadata)
        self.service.client.zone_output_service = AsyncMock(
            side_effect=AssertionError('Package creation must not actuate outputs'))

    async def asyncTearDown(self):
        await self.client.close()
        self.temp.cleanup()

    async def _registry(self):
        return deepcopy(self.rows)

    async def _create_storage(self, domain, name, *, grace_seconds):
        self.storage_calls.append((domain, name, grace_seconds))
        row = {'entity_id': f'{domain}.{name}', 'name': name, 'platform': domain,
               'unique_id': name, 'config_entry_id': None, 'disabled_by': None, 'labels': []}
        self.rows.append(row)
        return {'id': name}

    async def _create_template(self, name, owner, valid, lease):
        self.template_calls.append((name, owner, valid, lease))
        row = {'entity_id': f'binary_sensor.{name}', 'name': name, 'platform': 'template',
               'unique_id': 'template-owned-1', 'config_entry_id': 'entry-owned-1',
               'disabled_by': None, 'labels': []}
        self.rows.append(row)
        return {'result': {'entry_id': 'entry-owned-1'}}

    async def _set_metadata(self, entity_id, *, name, labels):
        next(row for row in self.rows if row['entity_id'] == entity_id).update(name=name, labels=labels)

    async def _connect_structure(self):
        from pilotsuite.core.zone_ontology import ROLES
        zone = next(zone for zone in await self.service.zones.list() if zone['zone_id']=='room')
        definition = {key: zone[key] for key in ('name','area_ids','extra_entity_ids','enabled','profile')}
        await self.service.zones.save(definition, 'room', 1, setup={
            'schema':'pilotsuite-zone-structure-v1','label_id':'zone','members':{}}, relevant=[])
        self.service.client.zone_label_devices = AsyncMock(return_value={})
        self.service.client.zone_labels = AsyncMock(return_value=[{'label_id':'zone','name':'Room'}] +
            [{'label_id':str(i),'name':role} for i,role in enumerate(ROLES)])

    async def test_connected_zone_creates_names_labels_and_members_in_one_package(self):
        await self._connect_structure()
        plan = await self.service.zone_package_preview('room', {'revision':2})
        self.assertTrue(all('metadata' in op for op in plan['operations']))
        result = await self.service.zone_package_apply('room', plan['id'], {'sha256':plan['sha256'],'confirm':True})
        self.assertEqual('verified', result['state'])
        cfg = await self.service.context.get('room')
        self.assertEqual(5, len(cfg['zone_structure']['members']))
        for row in self.rows:
            self.assertIn('zone', row['labels'])
            self.assertFalse(row['name'].startswith('ps_'))
        self.assertEqual('compare', cfg['zone_presence_v2']['mode'])
        self.service.client.zone_output_service.assert_not_awaited()

    async def test_autolabel_lost_reply_recovers_by_readback_without_duplicate_creation(self):
        await self._connect_structure()
        plan = await self.service.zone_package_preview('room', {'revision':2,'helper_role':'presence_timer','duration_seconds':180})
        async def lost_reply(eid, **fields):
            await self._set_metadata(eid, **fields)
            raise HomeAssistantError('Synthetic lost metadata response')
        self.service.client.zone_set_metadata.side_effect = lost_reply
        result = await self._single_apply(plan)
        self.assertEqual('verified', result['state'])
        self.assertIn('zone', self.rows[0]['labels'])
        await self._single_apply(plan)
        self.assertEqual(1, len(self.storage_calls))
        self.assertEqual(1, self.service.client.zone_set_metadata.await_count)

    async def test_autolabel_outage_does_not_hide_creation_and_manual_edit_blocks_retry(self):
        await self._connect_structure()
        plan = await self.service.zone_package_preview('room', {'revision':2,'helper_role':'presence_timer','duration_seconds':180})
        self.service.client.zone_set_metadata.side_effect = HomeAssistantError('Synthetic unavailable metadata')
        result = await self._single_apply(plan)
        self.assertEqual('attention', result['state'])
        self.assertIn('metadata_before', result['operations'][0]['receipt'])
        self.rows[0]['name'] = 'Manual name'
        result = await self._single_apply(plan)
        self.assertEqual('conflict', result['operations'][0]['outcome'])
        self.assertEqual(1, len(self.storage_calls))
        self.assertEqual('Manual name', self.rows[0]['name'])

    async def test_new_package_rejects_existing_external_zone_anchor(self):
        await self._connect_structure()
        self.rows.append({'entity_id':'binary_sensor.external', 'labels':['zone','0'], 'disabled_by':None})
        with self.assertRaises(SelectionConflict):
            await self.service.zone_package_preview('room', {'revision':2})
        self.service.client.zone_create_storage_helper.assert_not_awaited()

    async def test_disabled_external_anchor_does_not_authorize_a_replacement_package(self):
        await self._connect_structure()
        self.rows.append({'entity_id':'binary_sensor.disabled_anchor', 'labels':['zone','0'], 'disabled_by':'user'})
        with self.assertRaises(SelectionConflict):
            await self.service.zone_package_preview('room', {'revision':2})
        self.service.client.zone_create_storage_helper.assert_not_awaited()

    async def test_metadata_changed_during_package_prevents_binding(self):
        await self._connect_structure()
        plan = await self.service.zone_package_preview('room', {'revision':2})
        async def change_earlier(eid, **fields):
            await self._set_metadata(eid, **fields)
            if eid.startswith('binary_sensor.'):
                self.rows[0]['name'] = 'Manually changed'
        self.service.client.zone_set_metadata.side_effect = change_earlier
        result = await self.service.zone_package_apply('room', plan['id'], {'sha256':plan['sha256'],'confirm':True})
        self.assertEqual('attention', result['state'])
        self.assertIsNone((await self.service.context.get('room'))['zone_presence_v2']['package'])
        self.assertEqual('Manually changed', self.rows[0]['name'])

    async def _preview(self):
        return await self.service.zone_package_preview('room', {'revision': 1})

    async def test_single_missing_helper_has_no_package_binding_or_control(self):
        before = await self.service.context.get('room')
        for role, domain, duration in [('presence_status', 'input_boolean', None),
                                       ('presence_timer', 'timer', 180)]:
            plan = await self.service.zone_package_preview('room', {
                'revision': 1, 'helper_role': role, 'duration_seconds': duration})
            self.assertEqual('presence_helper', plan['kind'])
            self.assertEqual(1, len(plan['operations']))
            self.assertEqual(domain, plan['operations'][0]['domain'])
            self.assertFalse(plan['details']['automation_connected'])
            result = await self.service.zone_package_apply('room', plan['id'], {
                'sha256': plan['sha256'], 'confirm': True})
            self.assertEqual('verified', result['state'])
            self.assertEqual(before, await self.service.context.get('room'))
            count = len(self.storage_calls)
            repeated = await self.service.zone_package_apply('room', plan['id'], {
                'sha256': plan['sha256'], 'confirm': True})
            self.assertFalse(repeated['write_repeated'])
            self.assertEqual(count, len(self.storage_calls))
        self.assertEqual(180, self.storage_calls[-1][2])
        self.service.client.zone_create_binary_sensor.assert_not_awaited()
        self.service.client.zone_output_service.assert_not_awaited()

    async def test_missing_helper_rejects_unresolved_binding_and_invalid_requests(self):
        profile = {'schema': 'pilotsuite-organization-v1', 'timing': 'observe',
            'assignments': {'presence_status': [{'entity_id': 'input_boolean.missing',
                'platform': 'input_boolean', 'unique_id': 'old'}]}}
        await self.service.context.save_organization('room', 1, profile)
        with self.assertRaises(SelectionConflict):
            await self.service.zone_package_preview('room', {
                'revision': 2, 'helper_role': 'presence_status', 'duration_seconds': None})
        for role, duration in [('presence_output', None), ('presence_timer', True),
                               ('presence_timer', 0), ('presence_timer', 86401),
                               ('presence_status', 180)]:
            with self.assertRaises(InvalidSelection):
                await self.service.zone_package_preview('room', {
                    'revision': 2, 'helper_role': role, 'duration_seconds': duration})
        self.service.client.zone_create_storage_helper.assert_not_awaited()

    async def test_missing_helper_collision_and_changed_revision_never_create(self):
        request = {'revision': 1, 'helper_role': 'presence_timer', 'duration_seconds': 180}
        plan = await self.service.zone_package_preview('room', request)
        self.rows.append({'entity_id': plan['operations'][0]['entity_id']})
        with self.assertRaises(SelectionConflict):
            await self.service.zone_package_preview('room', request)
        await self.service.context.save_organization('room', 1, {
            'schema': 'pilotsuite-organization-v1', 'timing': 'observe', 'assignments': {}})
        with self.assertRaises(SelectionConflict):
            await self.service.zone_package_apply('room', plan['id'], {
                'sha256': plan['sha256'], 'confirm': True})
        self.service.client.zone_create_storage_helper.assert_not_awaited()

    async def _single_preview(self):
        return await self.service.zone_package_preview('room', {
            'revision': 1, 'helper_role': 'presence_timer', 'duration_seconds': 180})

    async def _single_apply(self, plan):
        return await self.service.zone_package_apply('room', plan['id'], {
            'sha256': plan['sha256'], 'confirm': True})

    async def test_single_helper_rechecks_revision_after_registry_io(self):
        plan = await self._single_preview()
        async def changed_registry():
            await self.service.context.save_organization('room', 1, {
                'schema': 'pilotsuite-organization-v1', 'timing': 'external', 'assignments': {}})
            return []
        self.service.client.zone_output_registry.side_effect = changed_registry
        result = await self._single_apply(plan)
        self.assertEqual('conflict', result['operations'][0]['outcome'])
        self.service.client.zone_create_storage_helper.assert_not_awaited()

    async def test_single_helper_readback_outage_recovers_receipt_after_restart(self):
        plan = await self._single_preview()
        before = await self.service.context.get('room')
        async def failing_readback():
            if self.rows:
                raise HomeAssistantError('Synthetic readback outage')
            return []
        self.service.client.zone_output_registry.side_effect = failing_readback
        result = await self._single_apply(plan)
        self.assertEqual('attention', result['state'])
        self.assertIn('storage_id', result['operations'][0]['receipt'])
        self.service.plans = PlanStore(self.service.settings.data_dir, self.service.audit, self.service.context)
        self.service.client.zone_output_registry.side_effect = self._registry
        recovered = await self._single_apply(plan)
        self.assertEqual('verified', recovered['state'])
        self.assertEqual(1, len(self.storage_calls))
        self.assertEqual(before, await self.service.context.get('room'))
        self.assertIn('storage_id', recovered['operations'][0]['receipt'])
        self.assertIn('identity', recovered['operations'][0]['receipt'])

    async def test_single_helper_lost_creation_response_never_replays_or_adopts_name(self):
        plan = await self._single_preview()
        async def lost(domain, name, *, grace_seconds):
            await self._create_storage(domain, name, grace_seconds=grace_seconds)
            raise HomeAssistantError('Synthetic lost creation response')
        self.service.client.zone_create_storage_helper.side_effect = lost
        self.assertEqual('attention', (await self._single_apply(plan))['state'])
        self.service.plans = PlanStore(self.service.settings.data_dir, self.service.audit, self.service.context)
        result = await self._single_apply(plan)
        self.assertEqual('ownership_unconfirmed', result['recovery'])
        self.assertEqual(1, len(self.storage_calls))
        with self.assertRaises(SelectionConflict):
            await self._single_preview()

    async def test_single_helper_wrong_identity_is_not_confirmed(self):
        plan = await self._single_preview()
        async def wrong(domain, name, *, grace_seconds):
            await self._create_storage(domain, name, grace_seconds=grace_seconds)
            self.rows[0]['unique_id'] = 'foreign'
            return {'id': name}
        self.service.client.zone_create_storage_helper.side_effect = wrong
        self.assertEqual('attention', (await self._single_apply(plan))['state'])
        self.assertEqual('ownership_unconfirmed', (await self._single_apply(plan))['recovery'])
        self.assertEqual(1, len(self.storage_calls))

    async def test_single_helper_disabled_during_creation_is_not_verified(self):
        plan = await self._single_preview()
        async def disabled(domain, name, *, grace_seconds):
            result = await self._create_storage(domain, name, grace_seconds=grace_seconds)
            self.rows[0]['disabled_by'] = 'user'
            return result
        self.service.client.zone_create_storage_helper.side_effect = disabled
        result = await self._single_apply(plan)
        self.assertEqual('attention', result['state'])
        self.assertEqual('ownership_unconfirmed', (await self._single_apply(plan))['recovery'])
        self.assertEqual(1, len(self.storage_calls))

    async def test_single_helper_expired_preview_does_not_create(self):
        plan = await self._single_preview()
        with patch('pilotsuite.core.organization_store.time.time', return_value=plan['expires_at']+1):
            with self.assertRaises(SelectionConflict):
                await self._single_apply(plan)
        self.service.client.zone_create_storage_helper.assert_not_awaited()

    async def test_single_helper_requires_exact_confirmation_and_zone(self):
        plan = await self._single_preview()
        for payload in ({'sha256': plan['sha256'], 'confirm': False},
                        {'sha256': 'wrong', 'confirm': True}):
            with self.assertRaises((InvalidSelection, SelectionConflict)):
                await self.service.zone_package_apply('room', plan['id'], payload)
        with self.assertRaises(InvalidSelection):
            await self.service.zone_package_apply('other', plan['id'], {
                'sha256': plan['sha256'], 'confirm': True})
        self.service.client.zone_create_storage_helper.assert_not_awaited()

    async def test_single_helper_does_not_require_pilotsuite_presence_configuration(self):
        plan = await self.service.zone_package_preview('other', {
            'revision': 0, 'helper_role': 'presence_status', 'duration_seconds': None})
        before = await self.service.context.get('other')
        result = await self.service.zone_package_apply('other', plan['id'], {
            'sha256': plan['sha256'], 'confirm': True})
        self.assertEqual('verified', result['state'])
        self.assertEqual(before, await self.service.context.get('other'))
        self.service.client.zone_output_service.assert_not_awaited()

    async def test_receipts_are_merged_instead_of_losing_creation_identity(self):
        plan = await self._preview()
        await self.service.plans.organization_claim('room', plan['id'], plan['sha256'])
        await self.service.plans.organization_progress('room', plan['id'], 0, 'sending')
        await self.service.plans.organization_receipt('room', plan['id'], 0, {'storage_id': 'stable'})
        await self.service.plans.organization_receipt('room', plan['id'], 0, {
            'entity_id': plan['operations'][0]['entity_id'],
            'identity': {'entity_id': plan['operations'][0]['entity_id'],
                         'platform': 'input_boolean', 'unique_id': 'stable'}})
        saved = await self.service.plans.organization_plan_get('room', plan['id'])
        self.assertEqual('stable', saved['operations'][0]['receipt']['storage_id'])
        self.assertEqual('stable', saved['operations'][0]['receipt']['identity']['unique_id'])

    async def test_restart_reconciles_owned_prefix_then_finishes_pending_operations(self):
        plan = await self._preview()
        claimed, _ = await self.service.plans.organization_claim('room', plan['id'], plan['sha256'])
        first = claimed['operations'][0]
        await self.service.plans.organization_progress('room', plan['id'], 0, 'sending')
        self.rows.append({'entity_id': first['entity_id'], 'name': first['name'],
                          'platform': first['domain'], 'unique_id': first['name'],
                          'config_entry_id': None, 'disabled_by': None, 'labels': []})
        await self.service.plans.organization_receipt('room', plan['id'], 0, {'storage_id': first['name']})
        await self.service.plans.organization_progress('room', plan['id'], 0, 'unknown')
        self.service.plans = PlanStore(self.service.settings.data_dir, self.service.audit, self.service.context)

        result = await self.service.zone_package_apply('room', plan['id'], {
            'sha256': plan['sha256'], 'confirm': True})

        self.assertEqual('verified', result['state'])
        self.assertEqual(3, len(self.storage_calls))
        self.assertFalse(any(name == first['name'] for _, name, _ in self.storage_calls))
        self.assertEqual(1, len(self.template_calls))
        package = (await self.service.context.get('room'))['zone_presence_v2']['package']
        self.assertEqual(plan['id'], package['plan_id'])
        self.assertEqual(first['entity_id'], package['entities'][first['role']])
        self.service.client.zone_output_service.assert_not_awaited()

    async def test_name_match_without_receipt_is_never_adopted_or_replayed(self):
        plan = await self._preview()
        claimed, _ = await self.service.plans.organization_claim('room', plan['id'], plan['sha256'])
        first = claimed['operations'][0]
        await self.service.plans.organization_progress('room', plan['id'], 0, 'sending')
        self.rows.append({'entity_id': first['entity_id'], 'name': first['name'],
                          'platform': first['domain'], 'unique_id': first['name'],
                          'config_entry_id': None, 'disabled_by': None, 'labels': []})
        await self.service.plans.organization_progress('room', plan['id'], 0, 'unknown')

        result = await self.service.zone_package_apply('room', plan['id'], {
            'sha256': plan['sha256'], 'confirm': True})

        self.assertEqual('ownership_unconfirmed', result['recovery'])
        self.assertEqual('attention', result['state'])
        self.service.client.zone_create_storage_helper.assert_not_awaited()
        self.service.client.zone_create_binary_sensor.assert_not_awaited()
        self.assertIsNone((await self.service.context.get('room'))['zone_presence_v2']['package'])

    async def test_verified_outputs_can_be_bound_after_restart_without_any_replay(self):
        plan = await self._preview()
        claimed, _ = await self.service.plans.organization_claim('room', plan['id'], plan['sha256'])
        for index, op in enumerate(claimed['operations']):
            await self.service.plans.organization_progress('room', plan['id'], index, 'sending')
            if op['domain'] == 'template':
                row = {'entity_id': op['entity_id'], 'name': op['name'], 'platform': 'template',
                       'unique_id': 'template-final', 'config_entry_id': 'entry-final',
                       'disabled_by': None, 'labels': []}
                receipt = {'config_entry_id': 'entry-final'}
            else:
                row = {'entity_id': op['entity_id'], 'name': op['name'], 'platform': op['domain'],
                       'unique_id': op['name'], 'config_entry_id': None,
                       'disabled_by': None, 'labels': []}
                receipt = {'storage_id': op['name']}
            self.rows.append(row)
            await self.service.plans.organization_receipt('room', plan['id'], index, receipt)
            await self.service.plans.organization_receipt('room', plan['id'], index, {
                'entity_id': op['entity_id'],
                'identity': {'entity_id': op['entity_id'], 'platform': row['platform'],
                             'unique_id': row['unique_id']}})
            await self.service.plans.organization_progress('room', plan['id'], index, 'verified', True)
        self.service.plans = PlanStore(self.service.settings.data_dir, self.service.audit, self.service.context)

        result = await self.service.zone_package_apply('room', plan['id'], {
            'sha256': plan['sha256'], 'confirm': True})

        self.assertEqual('verified', result['state'])
        self.service.client.zone_create_storage_helper.assert_not_awaited()
        self.service.client.zone_create_binary_sensor.assert_not_awaited()
        self.service.client.zone_set_metadata.assert_not_awaited()
        self.assertEqual(plan['id'], (await self.service.context.get('room'))[
            'zone_presence_v2']['package']['plan_id'])


if __name__ == '__main__':
    unittest.main()
