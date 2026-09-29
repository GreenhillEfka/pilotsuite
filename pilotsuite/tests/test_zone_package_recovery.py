from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock

from aiohttp.test_utils import TestClient, TestServer

from pilotsuite.app import SERVICE_KEY, create_app
from pilotsuite.core.plans import PlanStore
from pilotsuite.core.settings import Settings
from pilotsuite.core.selections import InvalidSelection, SelectionConflict
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
        next(row for row in self.rows if row['entity_id'] == entity_id)['name'] = name

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
