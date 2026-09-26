import asyncio
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
from unittest.mock import AsyncMock,patch
from aiohttp.test_utils import TestClient,TestServer
from pilotsuite.app import create_app,SERVICE_KEY
from pilotsuite.core.settings import Settings
from pilotsuite.core.context import ContextStore
from pilotsuite.core.organization import (inspect_structure,analyze,bind_request,binding_view,identity,resolve,
    validate_saved,empty,repair_preview,fingerprint)
from pilotsuite.core.selections import InvalidSelection,SelectionConflict
from pilotsuite.core.plans import PlanStore
from pilotsuite.core.helper_inspection import candidates
from pilotsuite.core.foundation import build_foundation
from pilotsuite.core.provisioning import provisioning_preview,provision_request
from pilotsuite.ha.client import HomeAssistantError
from organization_support import seed,payload,SAMPLE

class OrganizationPureTests(unittest.TestCase):
    def test_for_template_literal_and_event_data_are_not_lost(self):
        result=inspect_structure(SAMPLE)
        self.assertEqual(['existing_for','timer'],result['timing_methods'])
        refs=result['references']
        duration=next(r for r in refs if r['entity_id']=='input_number.room_timeout_old')
        self.assertEqual('presence_duration',duration['role_hint']);self.assertEqual('template_literal',duration['kind'])
        self.assertTrue(any(r['path']=='/triggers/1/event_data/entity_id' for r in refs))
        self.assertIn('template_dependency_coverage_partial',result['limitations'])
    def test_nested_conditions_are_not_writers(self):
        result=inspect_structure(SAMPLE)
        self.assertIsNone(next(r for r in result['references'] if r['entity_id']=='input_boolean.room_override')['role_hint'])
        owner=next(r for r in result['references'] if r['entity_id']=='input_boolean.legacy_presence')
        self.assertEqual('presence_status',owner['role_hint'])
    def test_disabled_branch_inheritance_and_legacy_sections(self):
        cfg={'trigger':[{'enabled':False,'trigger':'state','entity_id':'binary_sensor.x','for':5}],
             'action':[{'enabled':False,'choose':[{'conditions':[], 'sequence':[{'action':'timer.start','target':{'entity_id':'timer.x'}}]}]}]}
        result=inspect_structure(cfg)
        self.assertEqual([],result['timing_methods']);self.assertTrue(all(r['enabled'] is False for r in result['references']))
    def test_dynamic_enablement_is_not_active_evidence(self):
        r=inspect_structure({'actions':[{'enabled':'{{ enabled }}','sequence':[{'action':'timer.start','target':{'entity_id':'timer.x'}}]}]})
        self.assertTrue(all(x['enabled'] is None for x in r['references']))
    def test_dynamic_templates_not_resolved_by_partial_literal(self):
        cfg={'triggers':[{'trigger':'template','value_template':"{{ states('sensor.room_' ~ suffix) }} {# states('sensor.comment') #}"}]}
        r=inspect_structure(cfg);self.assertEqual([],r['references']);self.assertTrue(r['limitations'])
    def test_bad_and_oversized_config_rejected(self):
        x={};v=x
        for _ in range(20):v['sequence']={};v=v['sequence']
        for config in (x,{'actions':['x'*150000]},{'actions':[{'x':float('nan')}]},[] ):
            with self.assertRaises(InvalidSelection):inspect_structure(config)
    def test_identity_rename_follows_key_not_replacement_id(self):
        original={'entity_id':'timer.a','platform':'timer','unique_id':'stable'}
        other={'entity_id':'timer.a','platform':'timer','unique_id':'foreign','name':'Fake'}
        moved={**original,'entity_id':'timer.b','name':'Current'}
        self.assertEqual('timer.b',resolve(original,[other,moved])['entity_id'])
        self.assertEqual('identity_unresolved',resolve(original,[other])['status'])
    def test_ambiguous_identity_stays_unknown(self):
        i={'entity_id':'timer.a','platform':'timer','unique_id':'u'}
        self.assertIsNone(resolve(i,[i,{**i,'entity_id':'timer.b'}])['entity_id'])
    def test_name_only_similarity_never_proves_equivalence(self):
        row={'entity_id':'input_number.room_timeout_new','name':'Duration','platform':'input_number',
             'unique_id':'room_timeout_old','state':'5','unit':'min','area_id':None,'disabled':False}
        r=analyze('automation.test',SAMPLE,[row],['room'],True)
        f=next(f for f in r['findings'] if f['entity_id']=='input_number.room_timeout_old')
        self.assertEqual('missing',f['status']);self.assertTrue(f['candidates'][0]['requires_confirmation'])
        self.assertEqual('not_proven',f['candidates'][0]['semantic_equivalence'])
        self.assertIn('storage_key_matches_old_object_id',f['candidates'][0]['reasons'])
    def test_stale_snapshot_never_asserts_missing(self):
        r=analyze('automation.test',SAMPLE,[],[],False)
        self.assertTrue(all(f['status']=='snapshot_stale' and not f['candidates'] for f in r['findings']))
    def test_repair_preview_checks_fingerprint_domain_and_units(self):
        catalog=[{'entity_id':'input_number.new','name':'New','state':'5'}]
        r=repair_preview('automation.test',SAMPLE,fingerprint(SAMPLE),{'input_number.room_timeout_old':'input_number.new'},catalog)
        self.assertFalse(r['execution']['allowed']);self.assertEqual(1,len(r['edits']))
        with self.assertRaises(SelectionConflict):repair_preview('automation.test',SAMPLE,'wrong',{},catalog)
        with self.assertRaises(InvalidSelection):repair_preview('automation.test',SAMPLE,fingerprint(SAMPLE),{'input_number.room_timeout_old':'sensor.new'},catalog)
        cfg={'triggers':[{'trigger':'numeric_state','entity_id':'sensor.old'}]}
        rows=[{'entity_id':'sensor.old','state':'20','unit':'W'},{'entity_id':'sensor.new','state':'2','unit':'kWh'}]
        with self.assertRaises(InvalidSelection):repair_preview('automation.test',cfg,fingerprint(cfg),{'sensor.old':'sensor.new'},rows)
    def test_no_raw_alias_or_description_in_report(self):
        r=analyze('automation.test',SAMPLE,[],[],True)
        self.assertNotIn('PRIVATE_ALIAS',json.dumps(r));self.assertNotIn('float(5)',json.dumps(r))

class OrganizationIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp=tempfile.TemporaryDirectory();root=Path(self.temp.name)
        self.app=create_app(Settings(root,root/'options.json',golden_zone_area_ids=('room','other'),supervisor_token='',
            refresh_interval_seconds=3600,ingress_allowed_peers=('127.0.0.1',)))
        self.client=TestClient(TestServer(self.app));await self.client.start_server();self.s=self.app[SERVICE_KEY]
        self.registry=await seed(self.s);self.base='/api/v1/zones/room/organization'
    async def asyncTearDown(self):
        await self.client.close();self.temp.cleanup()
    async def revision(self):return (await self.s.selection_inventory('room'))['revision']
    async def bind(self,timing='timer'):
        rev=await self.revision();return await self.s.organization_save('room',payload(rev,timing))
    async def names(self,roles=None):
        await self.bind();return await self.s.organization_name_preview('room',{'revision':await self.revision(),'roles':roles or ['presence_status']})
    async def test_get_head_are_read_only_and_global_helpers_visible(self):
        for method in (self.client.get,self.client.head):self.assertEqual(200,(await method(self.base)).status)
        view=await (await self.client.get(self.base)).json()
        self.assertTrue(any(r['entity_id']=='timer.legacy_wait' and r['area_id'] is None for r in view['catalog']))
        self.s.client.organization_registry.assert_not_awaited();self.s.client.automation_config.assert_not_awaited()
        self.assertEqual(0,await self.revision())
    async def test_binding_persists_without_touching_roles_consent_or_evidence(self):
        await self.s.selections.patch('room',0,{'binary_sensor.room_motion':'relevant'})
        await self.s.context.configure('room',1,{'presence':['binary_sensor.room_motion']},True,now=time.time()-10)
        await self.s.context.record('room','binary_sensor.room_motion',time.time()-1,'unknown')
        before=await self.s.context.report('room');await self.bind();after=await self.s.context.report('room')
        self.assertEqual(before['event_count'],after['event_count']);self.assertEqual(before['config']['learning'],after['config']['learning'])
        self.assertEqual(before['config']['roles'],after['config']['roles'])
        reloaded=ContextStore(self.s.selections);self.assertEqual('timer',(await reloaded.get('room'))['organization']['timing'])
    async def test_existing_context_save_preserves_organization(self):
        await self.bind();before=(await self.s.context.get('room'))['organization']
        await self.s.context.configure('room',await self.revision(),{},False)
        self.assertEqual(before,(await self.s.context.get('room'))['organization'])
    async def test_stale_or_unconfirmed_mapping_has_no_effect(self):
        await self.bind();before=await self.s.context.get('room')
        with self.assertRaises(SelectionConflict):await self.s.organization_save('room',payload(0))
        p=payload(await self.revision());p['confirm']=False
        with self.assertRaises(InvalidSelection):await self.s.organization_save('room',p)
        self.assertEqual(before,await self.s.context.get('room'))
    async def test_mapping_rejects_self_evidence_and_unregistered_ids(self):
        p=payload(0);p['assignments']['presence_status']=['binary_sensor.room_motion']
        with self.assertRaises(InvalidSelection):await self.s.organization_save('room',p)
        p=payload(0);p['assignments']['presence_timer']=['timer.not_real']
        with self.assertRaises(InvalidSelection):await self.s.organization_save('room',p)
    async def test_old_for_foundation_never_forces_new_timer(self):
        p=payload(0,'existing_for');p['assignments']['presence_timer']=[]
        await self.s.organization_save('room',p)
        r=await (await self.client.get('/api/v1/zones/room/context')).json();f=r['foundation']
        self.assertFalse(any(h['domain']=='timer' for h in f['helper_plan']))
        self.assertFalse(f['provisioning']['execution']['allowed'])
        self.assertIn('input_boolean.legacy_presence',f['modules']['presence']['logical_sources'])
    async def test_bound_timer_reconciles_existing_identity_and_disallows_provision(self):
        await self.bind();r=await (await self.client.get('/api/v1/zones/room/context')).json();f=r['foundation']
        timers=[h for h in f['helper_plan'] if h['domain']=='timer']
        self.assertEqual('timer.legacy_wait',timers[0]['existing_entity_id']);self.assertFalse(f['provisioning']['execution']['allowed'])
        with self.assertRaises(InvalidSelection):
            await self.s.provision_helper('room',{'revision':await self.revision(),'helpers':[{'domain':'timer','key':'legacy_wait'}],'confirm':True})
        self.s.client.helper_create_timer.assert_not_awaited()
    async def test_bound_area_less_helper_inspection_works(self):
        await self.bind();self.s.client.helper_collection=AsyncMock(return_value=[])
        r=await self.s.inspect_existing_helpers('room',await self.revision())
        self.assertIn('timer.legacy_wait',[i['entity_id'] for i in r['items']])
    async def test_analysis_does_not_require_preconfigured_owner_or_timer(self):
        r=await self.s.organization_analyze('room',{'revision':0,'automation_ids':['automation.legacy_presence']})
        self.assertEqual(['existing_for','timer'],r['reports'][0]['timing_methods'])
        self.assertEqual({},(await self.s.context.get('room'))['roles'])
        self.s.client.organization_set_name.assert_not_awaited()
    async def test_unread_automation_is_explicit_partial(self):
        self.s.client.automation_config.side_effect=HomeAssistantError('unread')
        r=await self.s.organization_analyze('room',{'revision':0,'automation_ids':['automation.legacy_presence']})
        self.assertFalse(r['complete']);self.assertEqual(1,len(r['unread']))
    async def test_analysis_zone_change_rejected(self):
        async def change(_):
            await self.s.selections.patch('room',0,{'binary_sensor.room_motion':'relevant'})
            return SAMPLE
        self.s.client.automation_config.side_effect=change
        with self.assertRaises(SelectionConflict):await self.s.organization_analyze('room',{'revision':0,'automation_ids':['automation.legacy_presence']})
    async def test_name_plan_is_preview_until_confirmed(self):
        p=await self.names();self.s.client.organization_set_name.assert_not_awaited()
        with self.assertRaises(InvalidSelection):await self.s.organization_name_apply('room',p['id'],{'sha256':p['sha256'],'confirm':False})
        r=await self.s.organization_name_apply('room',p['id'],{'sha256':p['sha256'],'confirm':True})
        self.assertEqual('verified',r['state']);self.assertEqual('room · Raumstatus',self.registry['input_boolean.legacy_presence']['name'])
        self.assertEqual('presence-stable',self.registry['input_boolean.legacy_presence']['unique_id'])
        self.s.client.call_bounded_service.assert_not_awaited()
    async def test_duplicate_apply_returns_receipt_without_new_write(self):
        p=await self.names();args={'sha256':p['sha256'],'confirm':True}
        await self.s.organization_name_apply('room',p['id'],args);r=await self.s.organization_name_apply('room',p['id'],args)
        self.assertTrue(r['replayed']);self.s.client.organization_set_name.assert_awaited_once()
    async def test_expired_plan_blocks_every_write(self):
        p=await self.names()
        with patch('pilotsuite.core.organization_store.time.time',return_value=p['expires_at']+1):
            with self.assertRaises(SelectionConflict):await self.s.organization_name_apply('room',p['id'],{'sha256':p['sha256'],'confirm':True})
        self.s.client.organization_set_name.assert_not_awaited()
    async def test_rename_conflict_preserves_concurrent_name(self):
        p=await self.names();self.registry['input_boolean.legacy_presence']['name']='Someone else changed it'
        r=await self.s.organization_name_apply('room',p['id'],{'sha256':p['sha256'],'confirm':True})
        self.assertEqual('conflict',r['operations'][0]['outcome']);self.s.client.organization_set_name.assert_not_awaited()
    async def test_identity_replacement_blocks_change(self):
        p=await self.names();self.registry['input_boolean.legacy_presence']['unique_id']='replacement'
        r=await self.s.organization_name_apply('room',p['id'],{'sha256':p['sha256'],'confirm':True})
        self.assertEqual('attention',r['state']);self.s.client.organization_set_name.assert_not_awaited()
    async def test_lost_response_readback_does_not_infer_undo_ownership(self):
        p=await self.names()
        async def lost(eid,name):self.registry[eid]['name']=name;raise HomeAssistantError('lost')
        self.s.client.organization_set_name.side_effect=lost
        r=await self.s.organization_name_apply('room',p['id'],{'sha256':p['sha256'],'confirm':True})
        self.assertEqual('verified',r['state']);self.assertFalse(r['operations'][0]['write_response_confirmed'])
        with self.assertRaises(InvalidSelection):await self.s.organization_name_restore_preview('room',p['id'],{'revision':await self.revision()})
    async def test_unknown_write_never_replayed(self):
        p=await self.names();self.s.client.organization_set_name.side_effect=HomeAssistantError('lost')
        args={'sha256':p['sha256'],'confirm':True}
        r=await self.s.organization_name_apply('room',p['id'],args);self.assertEqual('unknown',r['operations'][0]['outcome'])
        await self.s.organization_name_apply('room',p['id'],args);self.s.client.organization_set_name.assert_awaited_once()
    async def test_restart_after_sending_does_not_replay(self):
        p=await self.names();await self.s.plans.organization_claim('room',p['id'],p['sha256'])
        await self.s.plans.organization_progress('room',p['id'],0,'sending')
        self.s.plans=PlanStore(self.s.settings.data_dir,self.s.audit,self.s.context)
        r=await self.s.organization_name_apply('room',p['id'],{'sha256':p['sha256'],'confirm':True})
        self.assertTrue(r['replayed']);self.assertEqual('sending',r['operations'][0]['outcome'])
        self.s.client.organization_set_name.assert_not_awaited()
    async def test_partial_group_preserves_verified_prefix(self):
        p=await self.names(['presence_status','presence_timer'])
        self.registry['timer.legacy_wait']['name']='Concurrent change'
        r=await self.s.organization_name_apply('room',p['id'],{'sha256':p['sha256'],'confirm':True})
        self.assertEqual(['verified','conflict'],[op['outcome'] for op in r['operations']]);self.s.client.organization_set_name.assert_awaited_once()
    async def test_undo_is_new_confirmed_plan_preserving_null_before_name(self):
        self.registry['input_boolean.legacy_presence']['name']=None
        p=await self.names();await self.s.organization_name_apply('room',p['id'],{'sha256':p['sha256'],'confirm':True})
        restore=await self.s.organization_name_restore_preview('room',p['id'],{'revision':await self.revision()})
        self.assertEqual(1,self.s.client.organization_set_name.await_count)
        await self.s.organization_name_apply('room',restore['id'],{'sha256':restore['sha256'],'confirm':True})
        self.assertIsNone(self.registry['input_boolean.legacy_presence']['name'])
    async def test_undo_refuses_changed_name(self):
        p=await self.names();await self.s.organization_name_apply('room',p['id'],{'sha256':p['sha256'],'confirm':True})
        self.registry['input_boolean.legacy_presence']['name']='New human preference'
        with self.assertRaises(SelectionConflict):await self.s.organization_name_restore_preview('room',p['id'],{'revision':await self.revision()})
    async def test_repair_plan_persists_but_cannot_execute(self):
        p=await self.s.organization_repair_preview('room',{'revision':0,'automation_id':'automation.legacy_presence',
            'fingerprint':fingerprint(SAMPLE),'replacements':{'input_number.room_timeout_old':'input_number.room_timeout_new'}})
        with self.assertRaises(InvalidSelection):await self.s.organization_name_apply('room',p['id'],{'sha256':p['sha256'],'confirm':True})
        self.s.client.organization_set_name.assert_not_awaited()
        self.assertNotIn('PRIVATE_ALIAS',json.dumps(await self.s.plans.organization_plans('room')))
    async def test_savepoint_restores_bindings_but_no_learning_or_activation(self):
        await self.bind('existing_for');point=await self.s.plans.create_savepoint('Before change')
        await self.bind('timer');preview=await self.s.plans.preview_restore(point['id'])
        await self.s.plans.restore_savepoint(point['id'],{'sha256':preview['sha256'],'basis':preview['basis'],'confirm_paused_restore':True})
        cfg=await self.s.context.get('room');self.assertEqual('existing_for',cfg['organization']['timing']);self.assertFalse(cfg['learning'])
        self.assertFalse(self.s._presence_runtime_enabled)
    async def test_no_schema_migration_and_cross_zone_plan_not_readable(self):
        p=await self.names()
        with self.assertRaises(InvalidSelection):await self.s.plans.organization_plan_get('other',p['id'])
        with sqlite3.connect(self.s.context.path) as db:self.assertEqual(8,db.execute('PRAGMA user_version').fetchone()[0])
    async def test_ingress_policy_and_asset_remain_guarded(self):
        self.assertEqual(200,(await self.client.get('/assets/organization.js')).status)
        self.s.settings=replace(self.s.settings,ingress_allowed_peers=('172.30.32.2',))
        for url in (self.base,'/assets/organization.js'):
            self.assertEqual(403,(await self.client.get(url)).status)
    async def test_runtime_takeover_remains_blocked_while_mapping_is_allowed(self):
        await self.bind()
        with self.assertRaises(InvalidSelection):await self.s.configure_presence_runtime('room',{'revision':await self.revision(),'enabled':True,'confirm':True})
        self.s.client.call_bounded_service.assert_not_awaited()
    async def test_shared_helper_prevents_unilateral_naming(self):
        await self.bind()
        await self.s.organization_save('other',payload(0))
        view=await self.s.organization_overview('room')
        self.assertTrue(all(not row['name_change_eligible'] for row in view['naming']))
        with self.assertRaises(SelectionConflict):
            await self.s.organization_name_preview('room',{'revision':await self.revision(),'roles':['presence_status']})
        self.s.client.organization_set_name.assert_not_awaited()

    async def test_http_binding_and_plan_roundtrip(self):
        result=await self.client.patch(self.base,json=payload(0));self.assertEqual(200,result.status)
        plan=await (await self.client.post(self.base+'/names',json={'revision':1,'roles':['presence_status']})).json()
        result=await self.client.post(self.base+'/plans/'+plan['id']+'/apply',json={'sha256':plan['sha256'],'confirm':True})
        self.assertEqual(200,result.status);self.assertEqual('verified',(await result.json())['state'])
