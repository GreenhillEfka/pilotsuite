"""Actual store/HTTP shadow contracts. All identifiers and observations are synthetic."""
import asyncio
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from aiohttp.test_utils import TestClient, TestServer
from pilotsuite.app import SERVICE_KEY, create_app
from pilotsuite.core.context import ContextStore
from pilotsuite.core.organization import bind_request
from pilotsuite.core.presence_shadow import DEFAULTS
from pilotsuite.core.selections import SelectionConflict
from pilotsuite.core.settings import Settings

NOW = 1790500000.0
SOURCE = 'binary_sensor.demo_presence'
MOTION = 'binary_sensor.demo_motion'
OWNER = 'input_boolean.demo_status'
OVERRIDE = 'input_boolean.demo_override'
LAMP = 'light.demo'
LUX = 'sensor.demo_lux'


def state(eid, value, at, attributes=None):
    stamp = datetime.fromtimestamp(at, UTC).isoformat()
    return {'entity_id': eid, 'state': value, 'attributes': attributes or {},
            'last_changed': stamp, 'last_updated': stamp, 'last_reported': stamp}


async def seed_shadow(service, now):
    entries = [(SOURCE, 'Dauerpräsenz Demo', 'demo', {'device_class': 'occupancy'}),
               (MOTION, 'Bewegung Demo', 'demo', {'device_class': 'motion'}),
               (OWNER, 'HA Raumstatus Demo', 'input_boolean', {}),
               (OVERRIDE, 'Manueller Vorrang Demo', 'input_boolean', {}),
               (LAMP, 'Licht Demo', 'demo', {'supported_color_modes':['color_temp'],
                  'min_color_temp_kelvin':2000,'max_color_temp_kelvin':6500,'brightness':80}),
               (LUX, 'Tageslicht Demo', 'demo', {'device_class':'illuminance','unit_of_measurement':'lx'})]
    world = {'areas':[{'area_id':'room','name':'Demo Wohnbereich'}], 'devices':[],
             'entities':[{'entity_id':eid,'name':name,'platform':platform,'unique_id':eid,
                          'area_id':'room','disabled_by':None} for eid,name,platform,_ in entries],
             'states':[state(eid,'80' if eid==LUX else 'off',now,attrs) for eid,_,_,attrs in entries]}
    await service.world.replace(deepcopy(world))
    service._connected = service._stream_connected = True
    service._last_refresh_at = datetime.fromtimestamp(now,UTC).isoformat()
    await service.selections.patch('room',0,{eid:'relevant' for eid,_,_,_ in entries})
    await service.context.configure('room',1,{'presence':[SOURCE,MOTION,OWNER],
        'light':[LAMP],'illuminance':[LUX]},False)
    for name in ('call_bounded_service','helper_create_timer','helper_delete_timer',
                 'organization_set_name','automation_config','related_automations','history'):
        setattr(service.client,name,AsyncMock(side_effect=AssertionError('No HA operation in shadow tests')))
    await service._derive()
    return world


class PresenceShadowIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp=tempfile.TemporaryDirectory();root=Path(self.temp.name)
        self.clock={'now':NOW};self.time_patch=patch('time.time',side_effect=lambda:self.clock['now']);self.time_patch.start()
        self.app=create_app(Settings(root,root/'options.json',golden_zone_area_ids=('room',),
            supervisor_token='',refresh_interval_seconds=3600,ingress_allowed_peers=('127.0.0.1',)))
        self.http=TestClient(TestServer(self.app));await self.http.start_server();self.s=self.app[SERVICE_KEY]
        for task in self.s._tasks:task.cancel()
        await asyncio.gather(*self.s._tasks,return_exceptions=True);self.s._tasks=[]
        self.world=await seed_shadow(self.s,NOW)
        self.url='/api/v1/zones/room/presence-shadow'
    async def asyncTearDown(self):
        for name in ('call_bounded_service','helper_create_timer','helper_delete_timer',
                     'organization_set_name','automation_config','related_automations','history'):
            getattr(self.s.client,name).assert_not_awaited()
        await self.http.close();self.time_patch.stop();self.temp.cleanup()
    async def revision(self):return (await self.s.selection_inventory('room'))['revision']
    async def start(self,**changes):
        spec=deepcopy(DEFAULTS)|{'source_modes':{SOURCE:'continuous',MOTION:'pulse'},'grace_seconds':30}|changes
        response=await self.http.post(self.url,json={'operation':'start','revision':await self.revision(),'confirm':True,'spec':spec})
        body=await response.json();self.assertEqual(200,response.status,body);return body
    async def tick(self,seconds=0,values=None,event=None):
        self.clock['now']+=seconds
        for eid,value in (values or {}).items():
            old=next(x for x in self.world['states'] if x['entity_id']==eid)
            old.update(state(eid,value,self.clock['now'],old['attributes']))
        await self.s.world.replace(deepcopy(self.world))
        self.s._last_refresh_at=datetime.fromtimestamp(self.clock['now'],UTC).isoformat()
        async with self.s._projection_lock:await self.s._shadow_tick_locked(now=self.clock['now'],event=event)
        return await self.s.presence_shadow('room')
    async def test_get_head_do_not_start_or_change_configuration(self):
        before=deepcopy(await self.s.context.get('room'))
        for method in (self.http.get,self.http.head):self.assertEqual(200,(await method(self.url)).status)
        self.assertEqual(before,await self.s.context.get('room'))
        self.assertEqual('disabled',(await self.s.presence_shadow('room'))['state'])
    async def test_explicit_start_stop_preserves_learning_and_roles(self):
        before=await self.s.context.get('room');rev=await self.revision();body=await self.start()
        self.assertEqual(rev+1,body['revision']);self.assertFalse(body['execution']['allowed'])
        self.assertEqual([],body['execution']['actions']);self.assertFalse(body['history_collection'])
        self.assertEqual('unknown',body['current']['computed']['state'])
        response=await self.http.post(self.url,json={'operation':'stop','revision':await self.revision(),'confirm':True})
        self.assertEqual(200,response.status);self.assertEqual(before,await self.s.context.get('room'))
    async def test_continuous_presence_grace_and_expiry(self):
        await self.start();v=await self.tick(1,{SOURCE:'on'})
        self.assertEqual('occupied',v['current']['computed']['state']);self.assertEqual('different',v['current']['comparison'])
        v=await self.tick(1,{SOURCE:'off'});deadline=v['current']['computed']['deadline']
        self.assertEqual(NOW+32,deadline)
        v=await self.tick(15);self.assertEqual(deadline,v['current']['computed']['deadline'])
        v=await self.tick(16);self.assertEqual('vacant',v['current']['computed']['state'])
    async def test_owner_never_feeds_its_own_evidence(self):
        await self.tick(1,{OWNER:'on'});v=await self.start()
        self.assertEqual('on',v['current']['ha_status']['state']);self.assertEqual('unknown',v['current']['computed']['state'])
    async def test_held_owner_state_does_not_expire_as_a_physical_sample(self):
        old=next(r for r in self.world['states'] if r['entity_id']==OWNER);old.update(state(OWNER,'on',NOW-86400))
        await self.tick(0,{SOURCE:'on'});v=await self.start()
        self.assertTrue(v['current']['ha_status']['usable']);self.assertEqual('same',v['current']['comparison'])
    async def test_unknown_required_source_blocks_vacancy(self):
        await self.start();await self.tick(1,{SOURCE:'on'});await self.tick(1,{SOURCE:'off'})
        v=await self.tick(40,{MOTION:'unavailable'});self.assertEqual('unknown',v['current']['computed']['state'])
    async def test_stale_physical_report_is_not_current_presence(self):
        await self.start(max_source_age_seconds=30);await self.tick(1,{SOURCE:'on'})
        v=await self.tick(31);self.assertEqual('unknown',v['current']['computed']['state'])
    async def test_restart_and_disconnect_preserve_grace_deadline(self):
        await self.start();await self.tick(1,{SOURCE:'on'});v=await self.tick(1,{SOURCE:'off'})
        deadline=v['current']['computed']['deadline'];self.s._stream_connected=False
        await self.tick(5);self.assertIsNone((await self.s.presence_shadow('room'))['current'])
        self.s.context=ContextStore(self.s.selections);self.s._shadow_init();self.s._stream_connected=True
        v=await self.tick(5);self.assertEqual(deadline,v['current']['computed']['deadline'])
        v=await self.tick(25);self.assertEqual('vacant',v['current']['computed']['state'])
    async def test_pulse_uses_event_time_not_arrival_or_high_level(self):
        await self.start();self.clock['now']+=10
        event={'entity_id':MOTION,'old_state':state(MOTION,'off',NOW),
               'new_state':state(MOTION,'on',NOW+5,{'device_class':'motion'})}
        v=await self.tick(0,{MOTION:'on'},event=event)
        self.assertEqual(NOW+35,v['current']['computed']['deadline'])
        v=await self.tick(10);self.assertEqual(NOW+35,v['current']['computed']['deadline'])
        v=await self.tick(20);self.assertEqual('unknown',v['current']['computed']['state'])
    async def test_identity_change_is_durably_suspended_even_if_reverted(self):
        await self.start();row=self.world['entities'][0];original=row['unique_id'];row['unique_id']='replacement'
        v=await self.tick(1);self.assertEqual('basis_changed',v['state']);self.assertIsNone(v['current'])
        row['unique_id']=original;v=await self.tick(1);self.assertEqual('basis_changed',v['state'])
    async def test_shared_revision_change_suspends(self):
        await self.start();await self.s.selections.patch('room',await self.revision(),{LUX:'ignored'})
        v=await self.tick(1);self.assertEqual('basis_changed',v['state'])
    async def test_derived_sensor_is_rejected_as_independent_raw_input(self):
        self.world['entities'][0]['platform']='template';await self.tick()
        spec=deepcopy(DEFAULTS)|{'source_modes':{SOURCE:'continuous',MOTION:'pulse'}}
        response=await self.http.post(self.url,json={'operation':'start','revision':await self.revision(),'confirm':True,'spec':spec})
        self.assertEqual(400,response.status)
    async def test_bad_payload_and_stale_revision_are_not_saved(self):
        before=await self.s.context.get('room')
        for body in ({'operation':'start','revision':True,'confirm':True},
                     {'operation':'stop','revision':1,'confirm':True},
                     {'operation':'stop','revision':await self.revision(),'confirm':False}):
            self.assertIn((await self.http.post(self.url,json=body)).status,(400,409))
        self.assertEqual(before,await self.s.context.get('room'))
    async def test_savepoint_excludes_operational_shadow_state(self):
        await self.start();point=await self.s.plans.create_savepoint('synthetic')
        text=(Path(self.temp.name)/'savepoints'/f"{point['id']}.json").read_text()
        self.assertNotIn('presence_shadow',text);self.assertNotIn('shadow_lighting',text)
    async def test_outdoor_provenance_stability_and_brightness_step(self):
        await self.tick(0,{SOURCE:'on'});await self.start(lux_source=LUX,lux_provenance='outdoor')
        v=await self.tick(31);light=v['current']['lights'][0]
        self.assertEqual('suggest',light['status']);self.assertLessEqual(light['settings']['brightness_pct'],15)
        self.assertTrue(v['current']['daylight']['usable'])
    async def test_unconfirmed_lux_never_becomes_daylight(self):
        await self.tick(0,{SOURCE:'on'});await self.start(lux_source=LUX)
        v=await self.tick(40);self.assertFalse(v['current']['daylight']['usable']);self.assertEqual({},v['current']['lights'][0]['settings'])
    async def test_manual_override_holds_light_proposal(self):
        cfg=await self.s.context.get('room');cat=await self.s.world.organization_catalog()
        profile=bind_request({'revision':await self.revision(),'confirm':True,'timing':'observe',
            'assignments':{'manual_override':[OVERRIDE]}},cat,cfg)
        await self.s.context.save_organization('room',await self.revision(),profile)
        await self.tick(1,{SOURCE:'on',OVERRIDE:'on'});v=await self.start(lux_source=LUX,lux_provenance='outdoor')
        self.assertTrue(v['current']['manual_hold']);self.assertEqual({},v['current']['lights'][0]['settings'])
    async def test_ingress_guard_and_general_apply_remain_closed(self):
        self.s.settings=replace(self.s.settings,ingress_allowed_peers=('172.30.32.2',))
        self.assertEqual(403,(await self.http.get(self.url)).status)
        self.assertEqual(403,(await self.http.post(self.url,json={})).status)
    async def test_optional_storage_failure_does_not_escape_shared_tick(self):
        await self.start()
        with patch.object(self.s.context,'update_shadow_checkpoint',AsyncMock(side_effect=OSError('synthetic'))):
            await self.tick(1,{SOURCE:'on'})
        self.assertTrue(self.s._stream_connected);self.assertIsNone((await self.s.presence_shadow('room'))['current'])
    async def test_local_worker_advances_real_kernel_without_extra_reads(self):
        await self.start();await self.tick(1,{SOURCE:'on'});await self.tick(1,{SOURCE:'off'})
        self.clock['now']+=31
        with patch('pilotsuite.shadow_service.TICK_SECONDS',.02):
            task=asyncio.create_task(self.s._shadow_loop())
            try:
                for _ in range(25):
                    await asyncio.sleep(.02)
                    if self.s._shadow_views.get('room',{}).get('view',{}).get('computed',{}).get('state')=='vacant':break
                self.assertEqual('vacant',self.s._shadow_views['room']['view']['computed']['state'])
            finally:task.cancel();await asyncio.gather(task,return_exceptions=True)

if __name__=='__main__':unittest.main()
