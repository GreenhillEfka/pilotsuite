"""Label import uses the real app and SQLite; HA registry is synthetic."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock
from aiohttp.test_utils import TestClient, TestServer
from pilotsuite.app import create_app, SERVICE_KEY
from pilotsuite.core.settings import Settings
from pilotsuite.core.zone_structure import KEY


class ZoneStructureTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        app = create_app(Settings(root, root / 'options.json', golden_zone_area_ids=('a',),
            supervisor_token='', refresh_interval_seconds=3600, ingress_allowed_peers=('127.0.0.1',)))
        self.http = TestClient(TestServer(app))
        self.addAsyncCleanup(self.http.close)
        await self.http.start_server()
        self.s = app[SERVICE_KEY]
        for task in self.s._tasks:
            task.cancel()
        import asyncio
        await asyncio.gather(*self.s._tasks, return_exceptions=True)
        self.s._tasks = []
        self.labels = [{'label_id':'unrelated','name':'Unrelated'}, {'label_id': 'room', 'name': 'Room'}, {'label_id': 'overview', 'name': 'Habitus Übersicht'},
                       {'label_id': 'anchor', 'name': 'Habitus Zone'}]
        self.world = {'areas': [{'area_id': 'a'}, {'area_id': 'b'}],
            'devices': [{'id': 'device', 'area_id': 'b', 'labels': ['room']}],
            'entities': [self.entity('sensor.temperature', ['room', 'overview']),
                         self.entity('light.group', [], device_id='device'),
                         self.entity('binary_sensor.anchor', ['room', 'anchor'], device_class='occupancy'),
                         self.entity('sensor.disabled', ['room'], disabled_by='user')],
            'states': []}
        await self.s.world.replace(deepcopy(self.world))
        self.s.client.zone_label_devices = AsyncMock(side_effect=lambda: {r['id']: r.get('labels',[]) for r in self.world['devices']})
        self.s.client.zone_labels = AsyncMock(side_effect=lambda: deepcopy(self.labels))
        self.s.client.zone_set_metadata = AsyncMock()
        self.registry = {row['entity_id']: deepcopy(row) for row in self.world['entities']}
        self.s.client.zone_output_registry = AsyncMock(side_effect=lambda: deepcopy(list(self.registry.values())))
        self.s.client.zone_registry_entry = AsyncMock(side_effect=lambda eid: deepcopy(self.registry[eid]))
        async def metadata(eid, **fields):
            self.registry[eid].update(fields)
        self.s.client.zone_set_metadata = AsyncMock(side_effect=metadata)
        self.definition = {'name': 'Room', 'area_ids': ['a'], 'extra_entity_ids': [], 'enabled': False, 'profile': 'observe'}
        self.setup = {'label_id': 'room', 'entity_ids': ['sensor.temperature', 'light.group', 'binary_sensor.anchor'],
                      'relevant_entity_ids': ['sensor.temperature']}

    def entity(self, eid, labels, **kw):
        return {'entity_id': eid, 'labels': labels, 'platform': 'synthetic', 'unique_id': eid,
                'area_id': None, 'disabled_by': None, **kw}

    async def save(self, setup=None, *, zid=None, revision=None):
        body = {'definition': self.definition, 'setup': self.setup if setup is None else setup}
        if zid:
            body['revision'] = revision
        return await self.http.request('PATCH' if zid else 'POST', '/api/v1/zones' + ('/' + zid if zid else ''), json=body)

    async def test_device_membership_roles_and_disabled_rows_visible_without_writes(self):
        before = await self.s.zones.list()
        result = await (await self.http.get('/api/v1/zone-labels/room')).json()
        members = {row['entity_id']: row for row in result['members']}
        self.assertEqual('device', members['light.group']['membership_source'])
        self.assertEqual(['Habitus Übersicht'], members['sensor.temperature']['habitus_roles'])
        self.assertTrue(members['sensor.disabled']['disabled'])
        self.assertEqual(before, await self.s.zones.list())
        self.s.client.zone_set_metadata.assert_not_awaited()

    async def test_single_save_persists_definition_structure_and_relevance_without_learning(self):
        response = await self.save()
        self.assertEqual(201, response.status, await response.text())
        zone = await response.json()
        cfg = await self.s.context.get(zone['zone_id'])
        self.assertEqual('room', cfg[KEY]['label_id'])
        self.assertEqual(['Habitus Zone'], cfg[KEY]['members']['binary_sensor.anchor']['roles'])
        self.assertFalse(cfg['learning'])
        self.assertNotIn('zone_presence_v2', cfg)
        self.assertEqual(set(self.setup['entity_ids']), set(zone['extra_entity_ids']))
        decisions = await self.s.selections.get(zone['zone_id'])
        self.assertEqual({'sensor.temperature': 'relevant', 'light.group': 'ignored', 'binary_sensor.anchor': 'ignored'}, decisions['decisions'])
        self.assertEqual(1, decisions['revision'])
        self.s.client.zone_set_metadata.assert_not_awaited()
        self.definition = {key: zone[key] for key in self.definition}
        response = await self.save(zid=zone['zone_id'], revision=1)
        self.assertEqual(1, (await response.json())['revision'], 'unchanged save preserves revision')

    async def test_stale_revision_and_duplicate_label_leave_all_stores_unchanged(self):
        first = await (await self.save()).json()
        before = await self.s.context.get(first['zone_id'])
        self.assertEqual(409, (await self.save(zid=first['zone_id'], revision=0)).status)
        self.assertEqual(409, (await self.save()).status)
        self.assertEqual(before, await self.s.context.get(first['zone_id']))
        self.assertEqual(2, len(await self.s.zones.list()), 'failed create must roll back its zone')

    async def test_invalid_label_identity_disabled_member_and_feedback_source_rejected(self):
        variants = [dict(self.setup, label_id='missing'), dict(self.setup, label_id='overview'),
                    dict(self.setup, entity_ids=['sensor.disabled']),
                    dict(self.setup, relevant_entity_ids=['binary_sensor.anchor']),
                    dict(self.setup, entity_ids=['sensor.unknown'])]
        for payload in variants:
            with self.subTest(payload=payload):
                self.assertEqual(400, (await self.save(payload)).status)
        self.assertEqual(1, len(await self.s.zones.list()))

    async def test_old_zone_edit_preserves_profile_and_context(self):
        zone = await (await self.save()).json()
        before = await self.s.context.get(zone['zone_id'])
        response = await self.http.patch('/api/v1/zones/' + zone['zone_id'], json={
            'revision': zone['revision'], 'definition': dict(self.definition, name='Renamed')})
        self.assertEqual(200, response.status)
        self.assertEqual(before, await self.s.context.get(zone['zone_id']))
        profile = await (await self.http.get('/api/v1/zones/' + zone['zone_id'] + '/structure')).json()
        self.assertEqual(before[KEY], profile['profile'])

    async def test_replaced_identity_is_not_adopted_and_removed_member_stops_analysis(self):
        zone = await (await self.save()).json()
        self.world['entities'][0]['unique_id'] = 'replacement'
        await self.s.world.replace(self.world)
        self.assertEqual(409, (await self.save(zid=zone['zone_id'], revision=1)).status)
        self.world['entities'][0]['unique_id'] = 'sensor.temperature'
        await self.s.world.replace(self.world)
        setup = dict(self.setup, entity_ids=['light.group', 'binary_sensor.anchor'], relevant_entity_ids=[])
        self.assertEqual(200, (await self.save(setup, zid=zone['zone_id'], revision=1)).status)
        self.assertEqual('ignored', (await self.s.selections.get(zone['zone_id']))['decisions']['sensor.temperature'])

    async def test_batch_label_preview_apply_readback_and_rollback_preserve_foreign_metadata(self):
        self.registry['light.group']['labels'] = ['unrelated']
        zone = await (await self.save()).json()
        zid = zone['zone_id']
        plan = await self.s.structure_label_preview(zid, {'revision': 1})
        self.assertEqual('structure_labels', plan['kind'])
        self.assertEqual(1, len(plan['operations']))
        self.s.client.zone_set_metadata.assert_not_awaited()
        apply = {'sha256': plan['sha256'], 'confirm': True}
        result = await self.s.ontology_apply(zid, plan['id'], apply)
        self.assertEqual('verified', result['state'])
        self.assertEqual(['room', 'unrelated'], self.registry['light.group']['labels'])
        self.assertIsNone(self.registry['light.group']['name'])
        await self.s.ontology_apply(zid, plan['id'], apply)
        self.assertEqual(1, self.s.client.zone_set_metadata.await_count)
        restore = await self.s.ontology_restore_preview(zid, plan['id'], {'revision': 1})
        await self.s.ontology_apply(zid, restore['id'], {'sha256': restore['sha256'], 'confirm': True})
        self.assertEqual(['unrelated'], self.registry['light.group']['labels'])
        self.assertNotIn('zone_presence_v2', await self.s.context.get(zid))

    async def test_manual_change_after_preview_is_a_conflict_not_overwritten(self):
        zone = await (await self.save()).json()
        plan = await self.s.structure_label_preview(zone['zone_id'], {'revision': 1})
        self.registry['light.group']['labels'] = ['manual_change']
        result = await self.s.ontology_apply(zone['zone_id'], plan['id'], {'sha256': plan['sha256'], 'confirm': True})
        self.assertEqual('attention', result['state'])
        self.assertEqual('conflict', result['operations'][0]['outcome'])
        self.s.client.zone_set_metadata.assert_not_awaited()

    async def test_desired_roles_are_saved_without_ha_write_then_previewed(self):
        setup = dict(self.setup, roles={'light.group': ['Habitus Übersicht']})
        zone = await (await self.save(setup)).json()
        self.s.client.zone_set_metadata.assert_not_awaited()
        plan = await self.s.structure_label_preview(zone['zone_id'], {'revision': 1})
        op = next(op for op in plan['operations'] if op['entity_id'] == 'light.group')
        self.assertEqual(['overview', 'room'], op['after']['labels'])
        self.assertEqual([], op['before']['labels'])

    async def test_external_anchor_collision_blocks_plan(self):
        zone = await (await self.save()).json()
        self.registry['binary_sensor.other'] = self.entity('binary_sensor.other', ['room', 'anchor'])
        from pilotsuite.core.selections import SelectionConflict
        with self.assertRaises(SelectionConflict):
            await self.s.structure_label_preview(zone['zone_id'], {'revision': 1})

    async def test_anchor_added_after_preview_blocks_apply_without_writes(self):
        zone = await (await self.save()).json()
        plan = await self.s.structure_label_preview(zone['zone_id'], {'revision': 1})
        self.registry['binary_sensor.other'] = self.entity('binary_sensor.other', ['room', 'anchor'])
        result = await self.s.ontology_apply(zone['zone_id'], plan['id'], {'sha256': plan['sha256'], 'confirm': True})
        self.assertEqual('attention', result['state'])
        self.assertEqual('conflict', result['operations'][0]['outcome'])
        self.s.client.zone_set_metadata.assert_not_awaited()

    async def test_shared_role_changed_in_another_zone_blocks_apply(self):
        zone = await (await self.save()).json()
        plan = await self.s.structure_label_preview(zone['zone_id'], {'revision': 1})
        self.labels.append({'label_id': 'second', 'name': 'Second'})
        setup = {'label_id':'second', 'entity_ids':['light.group'], 'relevant_entity_ids':[],
                 'roles':{'light.group':['Habitus Übersicht']}}
        self.assertEqual(201, (await self.save(setup)).status)
        result = await self.s.ontology_apply(zone['zone_id'], plan['id'], {'sha256': plan['sha256'], 'confirm': True})
        self.assertEqual('attention', result['state'])
        self.s.client.zone_set_metadata.assert_not_awaited()

    async def test_conflicting_shared_roles_are_visible_even_when_no_metadata_diff_remains(self):
        from pilotsuite.core.selections import SelectionConflict
        self.registry['light.group']['labels'] = ['room']
        zone = await (await self.save()).json()
        self.labels.append({'label_id':'other','name':'Other'})
        await self.save({'label_id':'other','entity_ids':['light.group'], 'relevant_entity_ids':[],
                         'roles':{'light.group':['Habitus Übersicht']}})
        with self.assertRaises(SelectionConflict):
            await self.s.structure_label_preview(zone['zone_id'], {'revision':1})

    async def test_fresh_device_label_change_is_checked_before_apply(self):
        zone = await (await self.save()).json()
        plan = await self.s.structure_label_preview(zone['zone_id'], {'revision': 1})
        self.registry['binary_sensor.other'] = self.entity('binary_sensor.other', ['anchor'], device_id='late_device')
        self.world['devices'].append({'id':'late_device', 'labels':['room']})
        # World snapshot intentionally remains unchanged; explicit guard reads HA.
        result = await self.s.ontology_apply(zone['zone_id'], plan['id'], {'sha256': plan['sha256'], 'confirm': True})
        self.assertEqual('attention', result['state'])
        self.s.client.zone_set_metadata.assert_not_awaited()

    async def test_batch_final_readback_detects_manual_edit_of_earlier_operation(self):
        zone = await (await self.save(dict(self.setup, roles={'light.group':['Habitus Übersicht'], 'sensor.temperature':[]}))).json()
        plan = await self.s.structure_label_preview(zone['zone_id'], {'revision':1})
        async def edit_previous(eid, **fields):
            self.registry[eid].update(fields)
            if eid == plan['operations'][-1]['entity_id']:
                self.registry[plan['operations'][0]['entity_id']]['name'] = 'Manual intervening name'
        self.s.client.zone_set_metadata.side_effect = edit_previous
        result = await self.s.ontology_apply(zone['zone_id'], plan['id'], {'sha256':plan['sha256'],'confirm':True})
        self.assertEqual('attention', result['state'])
        self.assertEqual('conflict', result['operations'][0]['outcome'])

    async def test_area_and_explicit_candidate_proposal_is_read_only_and_bounded(self):
        before = await self.s.zones.list()
        response = await self.http.post('/api/v1/zone-candidates', json={'area_ids':['b'], 'entity_ids':['sensor.temperature']})
        self.assertEqual(200,response.status)
        rows = {r['entity_id']:r for r in (await response.json())['members']}
        self.assertEqual({'light.group','sensor.temperature'},set(rows))
        self.assertEqual('area',rows['light.group']['membership_source'])
        self.assertEqual(['Habitus Übersicht'],rows['sensor.temperature']['habitus_roles'])
        self.assertEqual(before, await self.s.zones.list())
        self.s.client.zone_set_metadata.assert_not_awaited()
        self.assertEqual(400,(await self.http.post('/api/v1/zone-candidates',json={'area_ids':['a']*101,'entity_ids':[]})).status)

    async def test_label_read_outage_is_503_and_zone_save_does_not_mutate(self):
        from pilotsuite.ha.client import HomeAssistantError
        self.s.client.zone_labels.side_effect = HomeAssistantError('Synthetic unavailable')
        before = await self.s.zones.list()
        self.assertEqual(503,(await self.http.get('/api/v1/zone-labels')).status)
        self.assertEqual(503,(await self.save()).status)
        self.assertEqual(before, await self.s.zones.list())

    async def test_connection_suggestions_reuse_roles_but_never_replace_existing_bindings(self):
        from pilotsuite.core.zone_structure import connection_suggestions
        zone = await (await self.save()).json()
        cfg = await self.s.context.get(zone['zone_id'])
        catalog = await self.s.world.organization_catalog()
        result = connection_suggestions(cfg,catalog,{'sensor.temperature'},fresh=True)
        self.assertEqual({'presence_output':['binary_sensor.anchor']},result['assignments'])
        cfg['organization']={'assignments':{'presence_output':[{'entity_id':'binary_sensor.missing'}]}}
        self.assertEqual({},connection_suggestions(cfg,catalog,set(),fresh=True)['assignments'])
        self.assertEqual({},connection_suggestions(cfg,catalog,set(),fresh=False)['assignments'])
        self.s.client.zone_set_metadata.assert_not_awaited()

    async def test_connection_suggestions_do_not_guess_replaced_anchor_or_own_outputs(self):
        from pilotsuite.core.zone_structure import connection_suggestions
        zone = await (await self.save()).json()
        cfg = await self.s.context.get(zone['zone_id'])
        catalog = await self.s.world.organization_catalog()
        next(row for row in catalog if row['entity_id']=='binary_sensor.anchor')['unique_id']='replacement'
        self.assertEqual({},connection_suggestions(cfg,catalog,set(),fresh=True)['assignments'])
        catalog = await self.s.world.organization_catalog()
        cfg['zone_presence_v2']={'package':{'entities':{'sensor':'binary_sensor.anchor'}}}
        self.assertEqual({},connection_suggestions(cfg,catalog,set(),fresh=True)['assignments'])

    async def pending_zone(self):
        setup = dict(self.setup, label_id=None, label_name='New Zone')
        zone = await (await self.save(setup)).json()
        async def create_label(name):
            row = {'label_id':'new_zone', 'name':name}
            self.labels.append(row)
            return deepcopy(row)
        self.s.client.zone_create_label = AsyncMock(side_effect=create_label)
        return zone

    async def test_pending_label_and_members_are_one_plan_with_durable_binding_and_restore(self):
        zone = await self.pending_zone()
        zid = zone['zone_id']
        self.s.client.zone_create_label.assert_not_awaited()
        plan = await self.s.structure_label_preview(zid, {'revision':1})
        self.assertEqual('create_zone_label', plan['operations'][0]['effect'])
        self.assertEqual(4, len(plan['operations']))
        result = await self.s.ontology_apply(zid, plan['id'], {'sha256':plan['sha256'], 'confirm':True})
        self.assertEqual('verified', result['state'])
        self.assertEqual({'label_id':'new_zone','revision':2}, result['binding'])
        self.assertEqual('new_zone', (await self.s.context.get(zid))[KEY]['label_id'])
        for eid in self.setup['entity_ids']:
            self.assertIn('new_zone', self.registry[eid]['labels'])
        await self.s.ontology_apply(zid, plan['id'], {'sha256':plan['sha256'], 'confirm':True})
        self.assertEqual(1, self.s.client.zone_create_label.await_count)
        self.assertEqual(3, self.s.client.zone_set_metadata.await_count)
        reverse = await self.s.ontology_restore_preview(zid, plan['id'], {'revision':2})
        undone = await self.s.ontology_apply(zid, reverse['id'], {'sha256':reverse['sha256'],'confirm':True})
        self.assertEqual('verified', undone['state'])
        self.assertTrue(any(row['label_id']=='new_zone' for row in self.labels), 'no implicit label deletion')
        self.assertNotIn('new_zone', self.registry['light.group']['labels'])

    async def test_lost_label_create_response_never_adopts_name_or_retries(self):
        from pilotsuite.ha.client import HomeAssistantError
        zone = await self.pending_zone()
        plan = await self.s.structure_label_preview(zone['zone_id'], {'revision':1})
        async def lost_reply(name):
            self.labels.append({'label_id':'new_zone','name':name})
            raise HomeAssistantError('Synthetic lost creation response')
        self.s.client.zone_create_label.side_effect = lost_reply
        for _ in range(2):
            result = await self.s.ontology_apply(zone['zone_id'], plan['id'], {'sha256':plan['sha256'],'confirm':True})
            self.assertEqual('unknown', result['operations'][0]['outcome'])
        self.assertEqual(1, self.s.client.zone_create_label.await_count)
        self.s.client.zone_set_metadata.assert_not_awaited()
        self.assertIsNone((await self.s.context.get(zone['zone_id']))[KEY]['label_id'])
        # User can explicitly adopt the now-existing label in the normal editor.
        self.assertEqual(200, (await self.save(dict(self.setup,label_id='new_zone'),zid=zone['zone_id'],revision=1)).status)

    async def test_label_creation_receipt_recovers_readback_without_second_create(self):
        from pilotsuite.ha.client import HomeAssistantError
        zone = await self.pending_zone()
        plan = await self.s.structure_label_preview(zone['zone_id'], {'revision':1})
        original = self.s.client.zone_create_label.side_effect
        async def outage_after_receipt(name):
            created = await original(name)
            self.s.client.zone_labels.side_effect = HomeAssistantError('Synthetic registry outage')
            return created
        self.s.client.zone_create_label.side_effect = outage_after_receipt
        result = await self.s.ontology_apply(zone['zone_id'], plan['id'], {'sha256':plan['sha256'],'confirm':True})
        self.assertEqual('unknown', result['operations'][0]['outcome'])
        self.assertIn('label', result['operations'][0]['receipt'])
        self.s.client.zone_labels.side_effect = lambda:deepcopy(self.labels)
        result = await self.s.ontology_apply(zone['zone_id'], plan['id'], {'sha256':plan['sha256'],'confirm':True})
        self.assertEqual('verified', result['state'])
        self.assertEqual(1, self.s.client.zone_create_label.await_count)

    async def test_pending_label_collisions_and_stale_preview_do_not_create(self):
        from pilotsuite.core.selections import SelectionConflict
        zone = await self.pending_zone()
        self.assertEqual(409, (await self.save(dict(self.setup,label_id=None,label_name='new zone'))).status)
        plan = await self.s.structure_label_preview(zone['zone_id'], {'revision':1})
        self.labels.append({'label_id':'external','name':'New Zone'})
        result = await self.s.ontology_apply(zone['zone_id'],plan['id'],{'sha256':plan['sha256'],'confirm':True})
        self.assertEqual('conflict',result['operations'][0]['outcome'])
        self.s.client.zone_create_label.assert_not_awaited()
        self.s.client.zone_set_metadata.assert_not_awaited()

    async def test_new_label_without_members_can_be_created_but_does_not_prove_presence(self):
        zone = await self.pending_zone()
        self.assertEqual(200,(await self.save({'label_id':None,'label_name':'New Zone','entity_ids':[],
                                             'relevant_entity_ids':[]}, zid=zone['zone_id'],revision=1)).status)
        plan = await self.s.structure_label_preview(zone['zone_id'], {'revision':2})
        result = await self.s.ontology_apply(zone['zone_id'],plan['id'],{'sha256':plan['sha256'],'confirm':True})
        self.assertEqual('verified',result['state'])
        cfg = await self.s.context.get(zone['zone_id'])
        self.assertNotIn('zone_presence_v2',cfg)
        self.s.client.zone_set_metadata.assert_not_awaited()

    async def test_saved_member_identity_view_is_read_only_and_never_rebinds(self):
        zone = await (await self.save()).json()
        zid = zone['zone_id']
        before = await self.s.context.get(zid)
        selection = await self.s.selections.get(zid)
        original = deepcopy(self.world)
        for variant, status, resolved in (
                ('same', 'bound', 'sensor.temperature'),
                ('renamed', 'renamed', 'sensor.new_name'),
                ('replaced', 'identity_unresolved', None),
                ('missing', 'identity_unresolved', None),
                ('ambiguous', 'identity_unresolved', None),
                ('disabled', 'disabled', 'sensor.temperature')):
            with self.subTest(variant=variant):
                self.world = deepcopy(original)
                row = self.world['entities'][0]
                if variant == 'renamed': row['entity_id'] = 'sensor.new_name'
                elif variant == 'replaced': row['unique_id'] = 'replacement'
                elif variant == 'missing': self.world['entities'].pop(0)
                elif variant == 'ambiguous': self.world['entities'].append({**row, 'entity_id':'sensor.duplicate'})
                elif variant == 'disabled': row['disabled_by'] = 'user'
                await self.s.world.replace(self.world)
                self.s.client.zone_labels.reset_mock()
                response = await self.http.get('/api/v1/zones/' + zid + '/structure')
                self.assertEqual(200, response.status)
                result = await response.json()
                self.assertEqual(before[KEY], result['profile'])
                self.assertEqual(selection['decisions'], result['decisions'])
                self.assertIn('member_identities', result)
                entry = next(r for r in result['member_identities'] if r['saved_entity_id']=='sensor.temperature')
                self.assertEqual(status, entry['status'])
                self.assertEqual(resolved, entry['entity_id'])
                self.assertEqual('cached_registry_not_live_state', result['identity_basis'])
                self.assertEqual(before, await self.s.context.get(zid))
                self.assertEqual(selection, await self.s.selections.get(zid))
                self.s.client.zone_labels.assert_not_awaited()
                self.s.client.zone_set_metadata.assert_not_awaited()

    async def test_saved_missing_member_can_be_retained_without_adopting_replacement(self):
        zone = await (await self.save()).json()
        self.world['entities'] = [r for r in self.world['entities'] if r['entity_id']!='sensor.temperature']
        await self.s.world.replace(self.world)
        self.definition['name'] = 'New display name'
        response = await self.save(zid=zone['zone_id'], revision=1)
        self.assertEqual(200, response.status)
        cfg = await self.s.context.get(zone['zone_id'])
        self.assertEqual('sensor.temperature', cfg[KEY]['members']['sensor.temperature']['identity']['unique_id'])
