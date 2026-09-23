import asyncio
import unittest
from unittest.mock import AsyncMock, patch
from aiohttp import ClientConnectionError
from pilotsuite.ha.client import HomeAssistantClient, HomeAssistantError
from test_ha_client import _Socket, _Session


class AutomationReferenceClientTests(unittest.IsolatedAsyncioTestCase):
    def client(self, results):
        socket = _Socket([{'type':'auth_required'},{'type':'auth_ok'}] + [
            {'id':i,'success':True,'result':r} for i,r in enumerate(results,1)])
        client = HomeAssistantClient('ws://synthetic','test-token')
        client._session = _Session(socket)
        return client, socket

    async def test_only_read_commands_and_no_unrelated_data(self):
        client, socket = self.client([{'automation':['automation.a','automation.a'],'person':['person.private']},{}])
        result=await client.related_automations(['light.b','light.a','light.a'])
        self.assertEqual({'light.a':['automation.a'],'light.b':[]},result)
        self.assertEqual([{'id':1,'type':'search/related','item_type':'entity','item_id':'light.a'},
                          {'id':2,'type':'search/related','item_type':'entity','item_id':'light.b'}],socket.sent[1:])
        self.assertEqual(1024*1024,client._session.kwargs['max_msg_size'])

    async def test_malformed_and_overlarge_results_fail_closed(self):
        for value in [None,[],{'automation':None},{'automation':'automation.a'},
                      {'automation':['light.a']},{'automation':[True]},
                      {'automation':['automation.a']*201}]:
            with self.subTest(value=value):
                client,_=self.client([{'automation':['automation.valid']},value])
                with self.assertRaises(HomeAssistantError): await client.related_automations(['light.a','light.b'])

    async def test_invalid_scope_never_connects(self):
        client,_=self.client([])
        client.start=AsyncMock()
        for entities in [[],['light.a']*41,[True],['bad'],['light.a;secret'],None]:
            with self.assertRaises(HomeAssistantError): await client.related_automations(entities)
        client.start.assert_not_awaited()

    async def test_total_match_limit_does_not_truncate_to_false_clean_result(self):
        client,_=self.client([{'automation':[f'automation.a{i}' for i in range(200)]},
                             {'automation':['automation.extra']}])
        with self.assertRaisesRegex(HomeAssistantError,'exceeds 200'):
            await client.related_automations(['light.a','light.b'])

    async def test_unauthorized_result_discards_partial_success(self):
        client,socket=self.client([{'automation':['automation.a']}])
        socket.messages.append({'id':2,'success':False,'error':{'code':'unauthorized'}})
        with self.assertRaisesRegex(HomeAssistantError,'unauthorized'):
            await client.related_automations(['light.a','light.b'])

    async def test_transport_timeout_and_cancellation(self):
        for error in [ClientConnectionError('offline'),TimeoutError()]:
            client,_=self.client([]);client._authenticate=AsyncMock(side_effect=error)
            with self.assertRaises(HomeAssistantError): await client.related_automations(['light.a'])
        client,_=self.client([]);client._authenticate=AsyncMock(side_effect=asyncio.CancelledError())
        with self.assertRaises(asyncio.CancelledError): await client.related_automations(['light.a'])

    async def test_overall_deadline_bounds_many_reads(self):
        client,_=self.client([])
        async def slow(*args): await asyncio.Event().wait()
        client._command=slow
        real_timeout=asyncio.timeout
        with patch('pilotsuite.ha.client.asyncio.timeout',side_effect=lambda _:real_timeout(0.01)):
            with self.assertRaisesRegex(HomeAssistantError,'timed out'):
                await client.related_automations(['light.a'])
