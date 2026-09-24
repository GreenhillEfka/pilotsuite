"""Stateless compass contracts; every fixture is synthetic."""
import copy
import json
import unittest
from pilotsuite.core.review_compass import build_review_compass, with_automation_review, with_saved_notes, CHECK_IDS
from pilotsuite.core.review_notes import scope_fingerprint


def fixture():
    pattern = {'id':'p','sources':['binary_sensor.synthetic'],
               'statistics':{'activation_count':6,'distinct_day_count':4,'day_group':'all',
                             'timezone':'UTC','window_local':{'start_hour':12,'end_hour':14}},
               'confidence':None,'preference':None}
    draft = {'id':'d','zone_id':'z','pattern_id':'p','revision':2,'source_revision':3,
             'source_status':'current','unavailable_targets':[], 'current_pattern':pattern,
             'fields':dict(title='Synthetic',goal='Comfort',trigger='Presence',conditions='Dark',
                           manual_override='Manual first',exceptions='',target_ids=['light.synthetic']),
             'review_notes':{'schema':'pilotsuite-review-notes-v1','revision':0,'items':[]},
             'execution':{'allowed':False,'actions':[]}}
    inventory = {'zone_id':'z','revision':3,'items':[
        {'entity_id':'binary_sensor.synthetic','decision':'relevant','suggested_role':'motion','state':'off'},
        {'entity_id':'light.synthetic','decision':'relevant','suggested_role':'light','state':'off'}]}
    report = {'config':{'roles':{'presence':['binary_sensor.synthetic']},'learning':False},
              'reobservation':{'start':100,'split_at':170,'end':200,'timezone':'UTC','basis':'retained',
                  'windows':[{'day_group':'all','start_hour':12,'training_events':5,'training_days':3,
                              'later_events':1,'later_days':1,'state':'reobserved'}]},
              'coverage':{'sampled_slots':10,'impaired_slots':2}}
    return draft, inventory, report


def automation(draft, *, detail=False):
    result={'schema':'pilotsuite-automation-reference-review-v1','zone_id':'z','draft_id':'d',
            'draft_revision':2,'zone_revision':3,'checked_at':'2026-09-24T10:00:00+00:00',
            'basis':{'source_ids':['binary_sensor.synthetic'],'target_ids':['light.synthetic']},
            'items':[{'entity_id':'automation.synthetic'}], 'execution':{'allowed':False,'actions':[]}}
    if detail: result['inspection']={'entity_id':'automation.synthetic','config_fingerprint':'a'*64}
    return result


def authored(draft, disposition='reviewed'):
    return {'automation_id':'automation.synthetic','draft_revision':2,'zone_revision':3,
            'scope_fingerprint':scope_fingerprint(draft),'config_fingerprint':'a'*64,
            'disposition':disposition,'stale':False,'text':'PRIVATE_NOTE_CANARY'}


class ReviewCompassTests(unittest.TestCase):
    def setUp(self): self.draft,self.inventory,self.report=fixture()
    def build(self): return build_review_compass(self.draft,self.inventory,self.report)
    def check(self, identity): return next(c for c in self.build()['checks'] if c['id']==identity)

    def test_canonical_five_sections_and_one_navigation_step(self):
        result=self.build()
        self.assertEqual(CHECK_IDS,tuple(c['id'] for c in result['checks']))
        self.assertEqual('compare_automations',result['next_step']['id'])
        self.assertEqual('observed',self.check('sources')['state'])
        self.assertEqual('observed',self.check('evidence')['state'])
        self.assertEqual('described',self.check('intent')['state'])
        self.assertFalse(result['execution']['allowed']);self.assertEqual([],result['execution']['actions'])
        self.assertNotIn('score',result);self.assertNotIn('approved',json.dumps(result))

    def test_projection_is_pure_detached_deterministic_and_json_safe(self):
        before=copy.deepcopy((self.draft,self.inventory,self.report));one=self.build();two=self.build()
        self.assertEqual(one,two);self.assertEqual(before,(self.draft,self.inventory,self.report))
        one['basis']['source_ids'].append('binary_sensor.other')
        self.assertEqual(before,(self.draft,self.inventory,self.report))
        self.assertEqual(two,json.loads(json.dumps(two,allow_nan=False)))

    def test_unknown_and_foreign_zone_basis_is_rejected(self):
        for changes in ({'zone_id':'other'},{'revision':True},{'revision':-1},{'revision':2**54}):
            inv=dict(self.inventory,**changes)
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                build_review_compass(self.draft,inv,self.report)

    def test_missing_pattern_preserves_intent_without_inventing_sources(self):
        fields=copy.deepcopy(self.draft['fields']);self.draft['current_pattern']=None
        self.draft['source_status']='pattern_missing';result=self.build()
        self.assertEqual('review_sources',result['next_step']['id']);self.assertEqual(fields,self.draft['fields'])
        self.assertEqual('unknown',self.check('evidence')['state'])
        self.assertEqual([],result['basis']['source_ids'])

    def test_changed_sources_need_explicit_draft_review(self):
        self.draft['source_status']='zone_changed'
        self.assertEqual('stale',self.check('sources')['state'])
        self.assertEqual('edit_draft',self.build()['next_step']['id'])
        self.draft['source_status']='current';self.report['config']['roles']['presence']=[]
        self.assertEqual('stale',self.check('sources')['state'])

    def test_invalid_source_projections_are_not_live_health(self):
        original=copy.deepcopy(self.inventory['items'][0])
        for change in ({'state':None},{'state':'unknown'},{'state':'unavailable'},
                       {'state':'23'},{'decision':'unreviewed'},{'suggested_role':'temperature'}):
            self.inventory['items'][0]=dict(original,**change)
            with self.subTest(change=change):self.assertEqual('partial',self.check('sources')['state'])
        self.inventory['items'][0]=dict(original,state='on',last_updated='1990-01-01T00:00:00Z')
        self.assertEqual('observed',self.check('sources')['state'])
        self.assertIn('physischen Messfrische',json.dumps(self.check('sources'),ensure_ascii=False))

    def test_foreign_window_day_group_and_timezone_do_not_fill_evidence(self):
        base=copy.deepcopy(self.report)
        for key,value in (('start_hour',10),('day_group','weekend')):
            self.report=copy.deepcopy(base);self.report['reobservation']['windows'][0][key]=value
            with self.subTest(key=key):self.assertEqual('unknown',self.check('evidence')['state'])
        self.report=copy.deepcopy(base);self.report['reobservation']['timezone']='Europe/Vienna'
        self.assertEqual('unknown',self.check('evidence')['state'])

    def test_earlier_and_later_gaps_never_become_negative_evidence(self):
        for state in ('insufficient_earlier_evidence','insufficient_later_evidence'):
            self.report['reobservation']['windows'][0]['state']=state
            with self.subTest(state=state):
                self.assertEqual('partial',self.check('evidence')['state'])
                self.assertEqual('review_evidence',self.build()['next_step']['id'])

    def test_malformed_counts_are_unknown_not_zero_or_reobserved(self):
        for value in (None,True,-1,2**54,float('nan'),float('inf'),'6'):
            self.draft['current_pattern']['statistics']['activation_count']=value
            with self.subTest(value=value):self.assertEqual('unknown',self.check('evidence')['state'])
        self.draft['current_pattern']['statistics']['activation_count']=6
        self.report['reobservation']['windows'][0]['later_events']=-1
        self.assertEqual('unknown',self.check('evidence')['state'])

    def test_retained_learning_off_and_zone_coverage_remain_explicit(self):
        result=self.check('evidence')
        self.assertIn('Lernen aus',json.dumps(result,ensure_ascii=False))
        self.assertIn('ganze Zone',json.dumps(result,ensure_ascii=False))
        self.report['coverage']={}
        self.assertIn('Keine auswertbaren Stichproben',json.dumps(self.check('evidence'),ensure_ascii=False))

    def test_incomplete_intent_precedes_waiting_for_evidence(self):
        self.report['reobservation']['windows']=[];self.draft['fields']['goal']=' '
        self.assertEqual('edit_draft',self.build()['next_step']['id'])
        self.assertEqual('missing',self.check('intent')['state'])

    def test_unconfirmed_missing_or_unavailable_targets_remain_unresolved(self):
        for value in (None,'unknown','unavailable'):
            self.inventory['items'][1]['state']=value
            with self.subTest(value=value):self.assertEqual('partial',self.check('intent')['state'])
        self.inventory['items'][1]['state']='off';self.inventory['items'][1]['decision']='ignored'
        self.assertEqual('partial',self.check('intent')['state'])

    def test_empty_reference_review_is_limited_never_clear(self):
        report=automation(self.draft);report['items']=[]
        result=with_automation_review(self.build(),self.draft,report)
        self.assertEqual('limited',result['checks'][3]['state'])
        self.assertIn('kein Nachweis',result['checks'][3]['summary'])
        self.assertEqual('review_limits',result['next_step']['id'])

    def test_references_need_explicit_selection_not_automatic_inspection(self):
        result=with_automation_review(self.build(),self.draft,automation(self.draft))
        self.assertEqual('open_matches',result['next_step']['id'])
        self.assertEqual('partial',result['checks'][3]['state'])

    def test_selected_inspection_proposes_authored_note_not_approval(self):
        result=with_automation_review(self.build(),self.draft,automation(self.draft,detail=True))
        self.assertEqual('last_read',result['checks'][3]['state'])
        self.assertEqual('write_note',result['next_step']['id'])
        self.assertEqual('automation.synthetic',result['next_step']['automation_id'])
        self.assertFalse(result['execution']['allowed'])

    def test_wrong_report_id_revisions_scope_or_timestamp_cannot_enrich(self):
        base=self.build();original=automation(self.draft,detail=True)
        for change in ({'draft_id':'x'},{'zone_id':'x'},{'draft_revision':3},{'zone_revision':4},
                       {'checked_at':'2026-09-24T10:00:00'},{'checked_at':'bad'},
                       {'basis':{'source_ids':[],'target_ids':[]}},{'schema':'unknown'},
                       {'execution':{'allowed':True,'actions':[]}}):
            with self.subTest(change=change):
                self.assertEqual(base,with_automation_review(base,self.draft,dict(original,**change)))

    def test_unmatched_or_invalid_selected_config_is_not_accepted(self):
        base=self.build();report=automation(self.draft,detail=True)
        for change in ({'entity_id':'automation.other'},{'entity_id':'https://example.invalid'},
                       {'config_fingerprint':None},{'config_fingerprint':'z'*64}):
            changed=copy.deepcopy(report);changed['inspection'].update(change)
            with self.subTest(change=change):self.assertEqual(base,with_automation_review(base,self.draft,changed))

    def test_saved_assessment_and_freshness_are_independent(self):
        self.draft['review_notes']['items']=[authored(self.draft)]
        self.assertEqual('unknown',self.check('notes')['state'])
        self.assertEqual(1,self.check('notes')['counts']['reviewed'])
        self.assertEqual(0,self.check('notes')['counts']['matches_last_read'])
        self.assertEqual('inspect_automation',self.build()['next_step']['id'])
        result=with_automation_review(self.build(),self.draft,automation(self.draft,detail=True))
        self.assertEqual(1,result['checks'][4]['counts']['matches_last_read'])
        self.assertEqual('review_limits',result['next_step']['id'])
        self.assertNotIn('PRIVATE_NOTE_CANARY',json.dumps(result))

    def test_changed_config_preserves_text_and_needs_new_assessment(self):
        self.draft['review_notes']['items']=[authored(self.draft)]
        original=copy.deepcopy(self.draft);report=automation(self.draft,detail=True)
        report['inspection']['config_fingerprint']='b'*64
        result=with_automation_review(self.build(),self.draft,report)
        self.assertEqual(1,result['checks'][4]['counts']['config_changed'])
        self.assertEqual('write_note',result['next_step']['id']);self.assertEqual(original,self.draft)

    def test_needs_change_is_not_erased_by_matching_configuration(self):
        self.draft['review_notes']['items']=[authored(self.draft,'needs_change')]
        result=with_automation_review(self.build(),self.draft,automation(self.draft,detail=True))
        self.assertEqual(1,result['checks'][4]['counts']['needs_change'])
        self.assertEqual(1,result['checks'][4]['counts']['matches_last_read'])
        self.assertEqual('write_note',result['next_step']['id'])

    def test_save_receipt_advances_only_expected_notes_revision(self):
        report=automation(self.draft,detail=True)
        compass=with_automation_review(self.build(),self.draft,report)
        notes={'revision':1,'items':[authored(self.draft)]}
        result=with_saved_notes(compass,notes,report)
        self.assertEqual(1,result['basis']['review_revision'])
        self.assertEqual(1,result['checks'][4]['counts']['matches_last_read'])
        self.assertEqual(compass,with_saved_notes(compass,dict(notes,revision=0),report))
        self.assertEqual(compass,with_saved_notes(compass,dict(notes,revision=9),report))

    def test_all_disposition_freshness_combinations_keep_execution_closed(self):
        for disposition in ('open','needs_change','reviewed','unexpected'):
            for stale in (False,True):
                for detail in (False,True):
                    note=authored(self.draft,disposition);note['stale']=stale
                    self.draft['review_notes']['items']=[note]
                    result=with_automation_review(self.build(),self.draft,automation(self.draft,detail=detail))
                    with self.subTest(disposition=disposition,stale=stale,detail=detail):
                        self.assertFalse(result['execution']['allowed']);self.assertEqual([],result['execution']['actions'])
                        self.assertEqual(1,result['checks'][4]['counts']['total'])
                        self.assertEqual(1,sum(result['checks'][4]['counts'][s] for s in ('open','needs_change','reviewed')))

    def test_shared_frontend_fixture_matches_real_backend_projectors(self):
        from pathlib import Path
        data=json.loads((Path(__file__).parent/'fixtures'/'review_compass.json').read_text())
        draft,inventory,report=fixture()
        draft['review_compass']=build_review_compass(draft,inventory,report)
        review=automation(draft,detail=True)
        review['review_compass']=with_automation_review(draft['review_compass'],draft,review)
        self.assertEqual({'draft':draft,'comparison':review},data)
