import copy
import json
import unittest
from unittest.mock import AsyncMock
from aiohttp import ClientConnectionError
from pilotsuite.domain.automation_inspection import inspect_automation
from pilotsuite.ha.client import HomeAssistantClient, HomeAssistantError
from test_ha_client import _Socket, _Session

DRAFT={'fields':{'target_ids':['light.synthetic']},'current_pattern':{'sources':['binary_sensor.synthetic']}}
CONFIG={'triggers':[{'trigger':'state','entity_id':'binary_sensor.synthetic','to':'on'}],
        'conditions':[{'condition':'state','entity_id':'sensor.private','state':'secret'}],
        'actions':[{'action':'light.turn_on','target':{'entity_id':'light.synthetic'},'data':{'brightness':100}}]}


class InspectionTests(unittest.TestCase):
    def inspect(self, config=None, previous=None):
        return inspect_automation(config if config is not None else CONFIG,DRAFT,'automation.synthetic',previous)

    def test_sections_alignment_and_no_raw_private_values(self):
        config=copy.deepcopy(CONFIG);config.update(alias='private alias',description='secret message')
        config['actions'][0]['data']['token']='private-token'
        report=self.inspect(config);encoded=json.dumps(report)
        for private in ('private alias','secret message','private-token','sensor.private','brightness'):
            self.assertNotIn(private,encoded)
        self.assertEqual(['light.synthetic'],report['alignment']['target_action_references'])
        self.assertEqual(['binary_sensor.synthetic'],report['alignment']['source_trigger_references'])
        self.assertEqual(1,report['sections']['conditions'][0]['other_reference_count'])
        self.assertFalse(report['execution']['allowed']);self.assertEqual('not_determined',report['alignment']['semantic_equivalence'])
        self.assertTrue(all(x['state']=='open' for x in report['checklist']))

    def test_legacy_section_service_and_data_target(self):
        report=self.inspect({'trigger':{'platform':'state','entity_id':['binary_sensor.synthetic']},
            'action':{'service':'light.turn_off','data':{'entity_id':'light.synthetic'}}})
        self.assertEqual('state',report['sections']['triggers'][0]['kind'])
        self.assertEqual(['light.synthetic'],report['alignment']['target_action_references'])

    def test_nested_choose_repeat_parallel_if_and_conditions(self):
        action={'action':'light.turn_off','target':{'entity_id':'light.synthetic'}}
        config={'actions':[{'choose':[{'conditions':[{'condition':'and','conditions':[{'condition':'state','entity_id':'binary_sensor.synthetic'}]}],
                                      'sequence':[{'repeat':{'count':2,'sequence':[action]}}]}],
                            'default':[{'parallel':[{'sequence':[action]}]}]},
                           {'if':[{'condition':'template','value_template':'{{ private }}'}],'then':[action],'else':[{'stop':'private reason'}]}]}
        report=self.inspect(config)
        self.assertEqual(3,sum(x['kind']=='service_call' for x in report['sections']['actions']))
        self.assertTrue(report['sections']['conditions']);self.assertIn('templates_not_evaluated',report['limitations'])
        self.assertNotIn('private',json.dumps(report))

    def test_unknown_templates_blueprints_and_indirect_targets_stay_unknown(self):
        report=self.inspect({'use_blueprint':{'path':'private.yaml'},'actions':[
            {'action':'{{ service }}','target':{'entity_id':'{{ target }}','area_id':'private_room'}},
            {'action':'script.private_script'}, {'unrecognized':'private'}]})
        for warning in ('blueprint_not_expanded','templates_not_evaluated','indirect_target_not_resolved','indirect_call_not_expanded','unsupported_step'):
            self.assertIn(warning,report['limitations'])
        self.assertEqual('not_assessed',report['risk'])
        self.assertIn('target_gap',[x['id'] for x in report['checklist']])
        self.assertNotIn('private_script',json.dumps(report))

    def test_partial_source_alignment_keeps_missing_source_review_open(self):
        draft=copy.deepcopy(DRAFT);draft['current_pattern']['sources'].append('binary_sensor.second')
        report=inspect_automation(CONFIG,draft,'automation.synthetic')
        self.assertEqual(['binary_sensor.second'],report['alignment']['sources_without_direct_trigger_reference'])
        self.assertIn('source_gap',[x['id'] for x in report['checklist']])

    def test_action_condition_is_not_a_service_target(self):
        report=self.inspect({'actions':[{'condition':'state','entity_id':'light.synthetic','state':'on'}]})
        self.assertEqual([],report['alignment']['target_action_references'])

    def test_disabled_and_dynamic_steps_are_not_claimed_executed(self):
        report=self.inspect({'actions':[{'action':'light.turn_on','enabled':False}, {'action':'light.turn_off','enabled':'{{ enabled }}'}]})
        self.assertIn('disabled_step',report['limitations']);self.assertIn('dynamic_enablement',report['limitations'])
        self.assertIn('enabled',[x['id'] for x in report['checklist']])

    def test_fingerprint_changes_without_exposing_config(self):
        original=copy.deepcopy(CONFIG)
        first=self.inspect();same=self.inspect(dict(reversed(list(CONFIG.items()))),first['config_fingerprint'])
        self.assertEqual('first_read',first['change_status']);self.assertEqual('unchanged',same['change_status'])
        changed=copy.deepcopy(CONFIG);changed['actions'][0]['data']['brightness']=50
        self.assertEqual('changed',self.inspect(changed,first['config_fingerprint'])['change_status'])
        self.assertEqual(original,CONFIG)

    def test_size_depth_step_and_node_limits(self):
        deep={};cursor=deep
        for _ in range(18): cursor['sequence']={};cursor=cursor['sequence']
        for config in [deep,{'alias':'x'*123000},{'actions':[{'delay':1}]*201},{'x':[0]*2001}]:
            with self.assertRaises(HomeAssistantError):self.inspect(config)

    def test_invalid_structure_does_not_disappear_as_complete(self):
        report=self.inspect({'triggers':['not understood'],'actions':[None,{'repeat':'invalid'},{'if':42}],'trigger':[]})
        self.assertIn('unsupported_structure',report['limitations'])
        self.assertIn('ambiguous_section_aliases',report['limitations'])


class InspectionClientTests(unittest.IsolatedAsyncioTestCase):
    def client(self,result):
        socket=_Socket([{'type':'auth_required'},{'type':'auth_ok'},{'id':1,'success':True,'result':result}])
        client=HomeAssistantClient('ws://synthetic','test-token');client._session=_Session(socket)
        return client,socket

    async def test_exact_read_command_and_frame_bound(self):
        client,socket=self.client({'config':CONFIG})
        self.assertEqual(CONFIG,await client.automation_config('automation.synthetic'))
        self.assertEqual({'id':1,'type':'automation/config','entity_id':'automation.synthetic'},socket.sent[-1])
        self.assertEqual(128*1024,client._session.kwargs['max_msg_size'])

    async def test_invalid_inputs_and_malformed_responses(self):
        for result in ([],None,{}, {'config':[]},{'config':None}):
            client,_=self.client(result)
            with self.assertRaises(HomeAssistantError):await client.automation_config('automation.synthetic')
        client,_=self.client({});client.start=AsyncMock()
        for entity in ('light.synthetic','automation.x/../y',False):
            with self.assertRaises(HomeAssistantError):await client.automation_config(entity)
        client.start.assert_not_awaited()

    async def test_permission_transport_and_timeout_errors(self):
        client,socket=self.client({});socket.messages[-1]={'id':1,'success':False,'error':{'code':'unauthorized'}}
        with self.assertRaises(HomeAssistantError):await client.automation_config('automation.synthetic')
        for error in (TimeoutError(),ClientConnectionError('private'),RecursionError()):
            client,_=self.client({});client._authenticate=AsyncMock(side_effect=error)
            with self.assertRaises(HomeAssistantError):await client.automation_config('automation.synthetic')
