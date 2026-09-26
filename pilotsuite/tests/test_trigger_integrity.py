import copy
import json
import unittest
from pilotsuite.core.trigger_integrity import inspect_trigger_integrity as inspect
from pilotsuite.core.organization import analyze
from pilotsuite.core.selections import InvalidSelection
from pilotsuite.domain.automation_inspection import inspect_automation


class TriggerIntegrityTests(unittest.TestCase):
    def config(self, ids=('start',), selected='start'):
        return {'triggers':[{'trigger':'state','id':i} for i in ids],
                'actions':[{'if':[{'condition':'trigger','id':selected}],
                            'then':[{'action':'light.turn_on'}]}]}

    def row(self, config): return inspect(config)['selectors'][0]

    def test_missing_and_partial_matches_do_not_claim_branch_execution(self):
        self.assertEqual('missing',self.row(self.config(selected='absent'))['state'])
        row=self.row(self.config(selected=['start','absent']))
        self.assertEqual('partial_match',row['state']);self.assertEqual(1,row['missing_count'])
        self.assertEqual(['/triggers/0'],row['matching_trigger_paths'])
        self.assertFalse(inspect(self.config())['execution']['allowed'])

    def test_implicit_indices_integer_ids_and_legal_shared_ids(self):
        cfg=self.config(ids=('group','group'),selected='group')
        self.assertEqual(['/triggers/0','/triggers/1'],self.row(cfg)['matching_trigger_paths'])
        cfg['triggers']=[{'trigger':'state'},{'platform':'event'}]
        cfg['actions'][0]['if'][0]['id']=[0,'1']
        self.assertEqual('matched',self.row(cfg)['state'])

    def test_disabled_index_not_renumbered_and_dynamic_enablement(self):
        cfg=self.config(selected=1);cfg['triggers']=[{'trigger':'state','enabled':False},{'trigger':'state'}]
        self.assertEqual('matched',self.row(cfg)['state'])
        cfg['actions'][0]['if'][0]['id']=0
        self.assertEqual('disabled_only',self.row(cfg)['state'])
        cfg['triggers'][0]['enabled']='{{ flag }}'
        self.assertEqual('unknown',self.row(cfg)['state'])
        cfg['actions'][0]['enabled']=False
        self.assertEqual('inactive',self.row(cfg)['state'])

    def test_malformed_or_dynamic_ids_never_become_confirmed_missing(self):
        for value in (None,True,{},[],['start',{}],'{{ private }}','x'*513):
            cfg=self.config(selected=value);row=self.row(cfg)
            self.assertEqual('unknown',row['state']);self.assertIsNone(row['missing_count'])
        for value in (None,True,{},'{{ private }}'):
            cfg=self.config(ids=(value,),selected='missing')
            self.assertEqual('unknown',self.row(cfg)['state'])

    def test_incomplete_blueprint_merged_or_ambiguous_catalogues(self):
        for update in ({'use_blueprint':{}},{'triggers':[{'triggers':[]}]},
                       {'trigger':[]},{'triggers':False},{'triggers':[None]}):
            cfg=self.config(selected='absent');cfg.update(update)
            report=inspect(cfg);self.assertFalse(report['catalogue_complete'])
            self.assertEqual('unknown',report['selectors'][0]['state'])

    def test_wait_trigger_ids_and_payload_conditions_are_not_automation_triggers(self):
        cfg=self.config(selected='wait-only')
        cfg['actions'] += [{'wait_for_trigger':[{'trigger':'event','id':'wait-only'}]},
            {'action':'notify.notify','data':{'condition':'trigger','id':'payload-secret'}}]
        report=inspect(cfg)
        self.assertEqual(1,len(report['selectors']));self.assertEqual('missing',self.row(cfg)['state'])
        self.assertNotIn('payload-secret',json.dumps(report))

    def test_nested_branches_repeat_parallel_and_not_are_paths_not_truth_claims(self):
        condition={'condition':'trigger','id':'absent'}
        cfg=self.config();cfg['actions']=[{'choose':[{'conditions':[{'condition':'not','conditions':[condition]}],
          'sequence':[{'parallel':[{'sequence':[condition]}]}]}],
          'default':[{'repeat':{'while':[condition],'until':[condition],'sequence':[condition]}}]}]
        report=inspect(cfg)
        self.assertEqual(5,len(report['selectors']))
        self.assertTrue(all(r['state']=='missing' for r in report['selectors']))
        self.assertTrue(any('/conditions/0/conditions/0' in r['path'] for r in report['selectors']))

    def test_disabled_parent_never_claims_active_selector(self):
        cfg=self.config(selected='absent');cfg['actions'][0]['enabled']=False
        self.assertEqual('inactive',self.row(cfg)['state'])
        self.assertEqual(['/triggers/0'],inspect(cfg)['not_referenced_by_id'])

    def test_no_id_condition_is_not_a_defect(self):
        cfg={'trigger':{'platform':'event'},'action':{'service':'light.turn_on'}}
        report=inspect(cfg)
        self.assertEqual([],report['selectors']);self.assertEqual(['/trigger'],report['not_referenced_by_id'])

    def test_shorthand_boolean_conditions_and_legacy_sections(self):
        cfg={'trigger':{'platform':'event','id':'start'},
             'condition':{'or':[{'condition':'trigger','id':'start'}]}}
        self.assertEqual('matched',self.row(cfg)['state'])
        self.assertEqual('/condition/or/0',self.row(cfg)['path'])

    def test_privacy_nonmutation_and_opaque_names(self):
        cfg=self.config(ids=('<img src=x onerror=alert(1)>',),selected='<img src=x onerror=alert(1)>')
        cfg.update(alias='PRIVATE',description='SECRET');before=copy.deepcopy(cfg)
        report=inspect(cfg);encoded=json.dumps(report)
        for token in ('<img','PRIVATE','SECRET','alert'):self.assertNotIn(token,encoded)
        self.assertEqual(before,cfg);self.assertEqual('matched',self.row(cfg)['state'])

    def test_work_bounds_and_invalid_root(self):
        deep={};v=deep
        for _ in range(20): v['sequence']={};v=v['sequence']
        for cfg in (None,[],deep,{'actions':[0]*5001}):
            with self.assertRaises(InvalidSelection):inspect(cfg)

    def test_both_review_surfaces_use_identical_read_only_projection(self):
        cfg=self.config(selected='absent')
        inventory=analyze('automation.synthetic',cfg,[],[],True)
        draft={'fields':{'target_ids':[]},'current_pattern':{'sources':[]}}
        detail=inspect_automation(cfg,draft,'automation.synthetic')
        self.assertEqual(inventory['trigger_integrity'],detail['trigger_integrity'])
        self.assertFalse(inventory['execution']['allowed']);self.assertFalse(detail['execution']['allowed'])
        changed=copy.deepcopy(cfg);changed['triggers'][0]['id']='absent'
        fresh=analyze('automation.synthetic',changed,[],[],True)
        self.assertNotEqual(inventory['fingerprint'],fresh['fingerprint'])
        self.assertEqual('matched',fresh['trigger_integrity']['selectors'][0]['state'])
