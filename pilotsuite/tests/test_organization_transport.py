import unittest
from pilotsuite.ha.client import HomeAssistantClient,HomeAssistantError
from test_ha_client import _Socket,_Session

class OrganizationTransportTests(unittest.IsolatedAsyncioTestCase):
    def setup_client(self,result):
        self.socket=_Socket([{'type':'auth_required'},{'type':'auth_ok'},{'id':1,'success':True,'result':result}])
        c=HomeAssistantClient('ws://example.invalid/api/websocket','synthetic');c._session=_Session(self.socket)
        return c
    async def test_get_filters_sensitive_registry_options(self):
        c=self.setup_client({'entity_id':'timer.demo','platform':'timer','unique_id':'stable','name':'Demo',
            'options':{'secret_canary':'NEVER_RETURN'},'disabled_by':None})
        result=await c.organization_registry('timer.demo')
        self.assertNotIn('options',result)
        self.assertEqual({'id':1,'type':'config/entity_registry/get','entity_id':'timer.demo'},self.socket.sent[-1])
    async def test_update_sets_only_display_name_with_numeric_request_id(self):
        c=self.setup_client({'entity_entry':{'entity_id':'timer.demo'}})
        await c.organization_set_name('timer.demo','Demo · Nachlauftimer')
        self.assertEqual({'id':1,'type':'config/entity_registry/update','entity_id':'timer.demo','name':'Demo · Nachlauftimer'},self.socket.sent[-1])
    async def test_nullable_name_restores_original_override(self):
        c=self.setup_client({'entity_entry':{'entity_id':'timer.demo'}})
        await c.organization_set_name('timer.demo',None);self.assertIsNone(self.socket.sent[-1]['name'])
    async def test_invalid_payload_never_reaches_transport(self):
        c=self.setup_client(None)
        for eid,name in [('timer.bad-id','Name'),('timer.demo',{'new_entity_id':'timer.other'}),('timer.demo','x\ny'),('timer.demo','x'*256)]:
            with self.assertRaises(HomeAssistantError):await c.organization_set_name(eid,name)
        self.assertEqual([],self.socket.sent)
    async def test_mismatched_write_reply_is_unknown(self):
        c=self.setup_client({'entity_entry':{'entity_id':'timer.other'}})
        with self.assertRaises(HomeAssistantError):await c.organization_set_name('timer.demo','New')
    async def test_mismatched_read_identity_rejected(self):
        c=self.setup_client({'entity_id':'timer.other'})
        with self.assertRaises(HomeAssistantError):await c.organization_registry('timer.demo')
