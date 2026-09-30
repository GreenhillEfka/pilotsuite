"""Primary-zone lighting adapter, no second presence session or household calls."""
from copy import deepcopy
from datetime import UTC, datetime
import unittest
from unittest.mock import AsyncMock

from pilotsuite.core import zone_lighting as light
from pilotsuite.core.context import ContextStore
from pilotsuite.core.selections import InvalidSelection
from test_presence_shadow import NOW, SOURCE, MOTION, LAMP, LUX, OVERRIDE, state
import test_zone_presence_runtime as runtime


class ZoneLightingPolicyTests(unittest.TestCase):
    def setUp(self):
        self.spec=deepcopy(light.DEFAULTS)|{'lights':[LAMP],'daylight_source':LUX,'daylight_provenance':'outdoor',
            'manual_entities':[OVERRIDE],'off_when_vacant':True,'manual_hold_seconds':60}
        self.states={LAMP:state(LAMP,'off',NOW,{'supported_color_modes':['brightness']}),
                     LUX:state(LUX,'80',NOW,{'unit_of_measurement':'lx'}),OVERRIDE:state(OVERRIDE,'off',NOW)}
        self.presence={'state':'occupied','valid':True}

    def step(self,point=None,seconds=0,**kwargs):
        return light.evaluate(self.spec,point,self.states,self.presence,now=NOW+seconds,fresh=kwargs.pop('fresh',True),**kwargs)

    def stabilized(self):
        point=None
        for second in (0,10,20,30):point,view=self.step(point,second)
        return point,view

    def test_existing_policy_limits_proposal_and_never_executes(self):
        _,view=self.stabilized()
        self.assertEqual({'on':True,'brightness_pct':15},view['lights'][0]['settings'])
        self.assertFalse(view['execution']['allowed'])

    def test_unknown_presence_never_becomes_an_off_proposal(self):
        for presence in ({'state':'vacant','valid':False},None,{'state':'unknown','valid':True}):
            self.presence=presence;self.states[LAMP]['state']='on'
            _,view=self.step();self.assertEqual({},view['lights'][0]['settings'])

    def test_missing_lux_is_not_dark_and_unconfirmed_provenance_is_not_used(self):
        for change in ('unavailable','stale','unit','provenance'):
            with self.subTest(change=change):
                self.setUp()
                if change=='unavailable':self.states[LUX]['state']='unavailable'
                if change=='stale':self.states[LUX]=state(LUX,'0',NOW-1900,{'unit_of_measurement':'lx'})
                if change=='unit':self.states[LUX]['attributes']['unit_of_measurement']='%'
                if change=='provenance':self.spec['daylight_provenance']='unconfirmed'
                _,view=self.stabilized();self.assertIsNone(view['daylight']['value']);self.assertEqual({},view['lights'][0]['settings'])

    def test_manual_change_preserves_absolute_hold_across_restart_and_duplicates(self):
        point,_=self.stabilized()
        event={'entity_id':LAMP,'old_state':deepcopy(self.states[LAMP]),'new_state':state(LAMP,'on',NOW+31,{'brightness':90})}
        point,view=self.step(point,31,event=event)
        self.assertEqual(NOW+91,view['lights'][0]['manual_until']);self.assertEqual({},view['lights'][0]['settings'])
        point,view=self.step(point,35,event=event,restart=True)
        self.assertEqual(NOW+91,view['lights'][0]['manual_until'])
        _,view=self.step(point,92);self.assertIsNone(view['lights'][0]['manual_until'])
        self.assertEqual('stabilizing',view['lights'][0]['status'])

    def test_unknown_manual_blocker_holds_even_confirmed_vacancy(self):
        self.states[LAMP]['state']='on';self.states[OVERRIDE]['state']='unavailable'
        self.presence={'state':'vacant','valid':True}
        _,view=self.step();self.assertEqual({},view['lights'][0]['settings'])

    def test_color_only_and_effect_changes_also_start_manual_hold(self):
        for key,value in [('hs_color',[120,50]),('xy_color',[0.3,0.2]),('rgbw_color',[20,30,40,50]),
                          ('rgbww_color',[20,30,40,50,60]),('effect','colorloop'),('color_temp',300)]:
            with self.subTest(attribute=key):
                old=state(LAMP,'on',NOW,{'brightness':100})
                new=state(LAMP,'on',NOW+1,{'brightness':100,key:value})
                _,view=self.step(seconds=1,event={'entity_id':LAMP,'old_state':old,'new_state':new})
                self.assertEqual(NOW+61,view['lights'][0]['manual_until'])

    def test_gap_or_restart_requires_new_stabilization(self):
        point,_=self.step()
        for kwargs in ({'seconds':31},{'seconds':10,'restart':True}):
            _,view=self.step(point,**kwargs);self.assertEqual('stabilizing',view['lights'][0]['status'])

    def test_transient_gap_preserves_cooldown(self):
        point,_=self.stabilized()
        point,_=self.step(point,31,fresh=False)
        for second in (32,42,52,62):point,view=self.step(point,second)
        self.assertEqual('rate_limited',view['lights'][0]['status'])

    def test_restart_preserves_cooldown_without_preserving_stability(self):
        point,_=self.stabilized();point,view=self.step(point,31,restart=True)
        self.assertEqual('stabilizing',view['lights'][0]['status'])
        for second in (41,51,61):point,view=self.step(point,second)
        self.assertEqual('rate_limited',view['lights'][0]['status'])

    def test_unavailable_light_hides_settings_then_restarts_stabilization(self):
        point,_=self.stabilized();self.states[LAMP]['state']='unavailable'
        point,view=self.step(point,31);self.assertEqual({},view['lights'][0]['settings'])
        self.states[LAMP]['state']='off';_,view=self.step(point,32)
        self.assertEqual('stabilizing',view['lights'][0]['status'])


class ZoneLightingRuntimeTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=runtime.ZonePresenceRuntimeTests.asyncSetUp
    asyncTearDown=runtime.ZonePresenceRuntimeTests.asyncTearDown
    tick=runtime.ZonePresenceRuntimeTests.tick

    async def configure(self,**changes):
        inv=await self.service.selection_inventory('room')
        spec=deepcopy(light.DEFAULTS)|{'lights':[LAMP],'daylight_source':LUX,'daylight_provenance':'outdoor','manual_entities':[OVERRIDE]}|changes
        response=await self.http.put('/api/v1/zones/room/lighting',json={'revision':inv['revision'],'mode':'compare','spec':spec})
        body=await response.json();self.assertEqual(200,response.status,body);return body

    async def test_configuration_preserves_primary_presence_deadline_and_other_context(self):
        await self.tick(1,{SOURCE:'on'});before=await self.tick(1,{SOURCE:'off'})
        cfg=await self.service.context.get('room')
        result=await self.configure()
        self.assertEqual(before['current']['deadline'],result['current']['deadline'])
        after=await self.service.context.get('room');self.assertEqual(cfg,{k:v for k,v in after.items() if k!=light.KEY})
        self.assertNotIn('presence_shadow',after)
        for _ in range(3):result=await self.tick(10)
        self.assertEqual('vacant',result['current']['state']);self.assertFalse(result['lighting']['execution']['allowed'])
        self.service.client.zone_output_service.assert_not_awaited()

    async def test_get_is_read_only_identical_save_retains_revision_and_checkpoint(self):
        await self.tick(1,{SOURCE:'on'});result=await self.configure();point=await self.service.context.zone_operational('room')
        for _ in range(2):
            response=await self.http.get('/api/v1/zones/room/presence');self.assertEqual(200,response.status)
        self.assertEqual(point,await self.service.context.zone_operational('room'))
        again=await self.configure();self.assertEqual(result['revision'],again['revision'])
        self.assertEqual(point,await self.service.context.zone_operational('room'))

    async def test_pause_and_stale_transport_hide_actionable_proposals(self):
        await self.tick(1,{SOURCE:'on'});await self.configure()
        for _ in range(3):result=await self.tick(10)
        self.assertTrue(result['lighting']['current']['lights'][0]['settings'])
        self.service._stream_connected=False
        stale=await self.service.zone_presence_view('room');self.assertIsNone(stale['lighting']['current'])
        self.service._stream_connected=True
        response=await self.http.put('/api/v1/zones/room/lighting',json={'revision':result['revision'],'mode':'paused','spec':result['lighting']['spec']})
        paused=await response.json();self.assertEqual('paused',paused['lighting']['status']);self.assertIsNone(paused['lighting']['current'])

    async def test_stale_revision_and_active_mode_rejected(self):
        result=await self.configure()
        for payload in ({'revision':result['revision']-1,'mode':'compare'}, {'revision':result['revision'],'mode':'active'}):
            response=await self.http.put('/api/v1/zones/room/lighting',json={**payload,'spec':result['lighting']['spec']})
            self.assertIn(response.status,(400,409))
        self.service.client.zone_output_service.assert_not_awaited()

    async def test_identity_replacement_cannot_reuse_saved_lighting_configuration(self):
        await self.tick(1,{SOURCE:'on'});await self.configure()
        next(r for r in self.world['entities'] if r['entity_id']==LAMP)['unique_id']='replacement'
        result=await self.tick(1)
        self.assertEqual('basis_changed',result['lighting']['status']);self.assertIsNone(result['lighting']['current'])

    async def test_temporary_identity_conflict_stays_suspended_until_explicit_save(self):
        await self.tick(1,{SOURCE:'on'});await self.configure()
        entity=next(r for r in self.world['entities'] if r['entity_id']==LAMP);old=entity['unique_id']
        entity['unique_id']='replacement';await self.tick(1)
        entity['unique_id']=old;result=await self.tick(1)
        self.assertEqual('basis_changed',result['lighting']['status'])
        result=await self.configure();self.assertEqual('current',result['lighting']['status'])
        self.assertEqual('stabilizing',result['lighting']['current']['lights'][0]['status'])

    async def test_relevance_and_derived_daylight_are_not_silently_authorized(self):
        catalog=await self.service.world.organization_catalog()
        spec=deepcopy(light.DEFAULTS)|{'lights':[LAMP],'daylight_source':LUX,'daylight_provenance':'outdoor'}
        for allowed in ({LAMP},{LUX}):
            with self.assertRaises(InvalidSelection):light.validate_spec(spec,catalog,allowed)
        next(r for r in catalog if r['entity_id']==LUX)['derived']=True
        with self.assertRaises(InvalidSelection):light.validate_spec(spec,catalog,{LAMP,LUX})
