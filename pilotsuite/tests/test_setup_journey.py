import unittest
from pilotsuite.core.setup_journey import setup_journey

class SetupJourneyTests(unittest.TestCase):
    def test_pending_tag_is_the_next_step_without_claiming_execution(self):
        result=setup_journey({}, config={'zone_structure':{'label_id':None,'label_name':'Room','members':{}}})
        self.assertEqual('labels',result['next_step']['action'])
        self.assertFalse(result['execution']['allowed'])
        self.assertEqual('planned',result['steps'][-1]['state'])

    def test_optional_modules_do_not_block_saved_presence_and_manual_status(self):
        foundation={'organization':{'assignments':{'presence_output':[{'entity_id':'binary_sensor.room','disabled':False}]}},
                    'modules':{'lighting':{'lights':['light.room']},'climate':{'state':'needs_sources'},'media':{'state':'needs_sources'}}}
        config={'zone_structure':{'label_id':'room','members':{}},'zone_presence_v2':{'spec':{'sources':[{}]},'mode':'compare'}}
        result=setup_journey(foundation, config=config, inventory={'enabled':True})
        self.assertEqual(['configured','configured','configured','planned','planned'],[s['state'] for s in result['steps']])
        self.assertEqual('lightmodule',result['next_step']['action'])
        self.assertNotIn('active',str(result))

    def test_missing_bound_identity_does_not_suggest_replacement(self):
        f={'organization':{'assignments':{'presence_output':[{'entity_id':None,'saved_entity_id':'binary_sensor.old'}]}}}
        result=setup_journey(f)
        self.assertEqual('attention',result['steps'][2]['state'])
        self.assertIn('keinen Ersatz',result['steps'][2]['summary'])

    def test_own_package_and_paused_presence_remain_distinct_from_live_acceptance(self):
        cfg={'zone_presence_v2':{'spec':{'sources':[{}]},'mode':'compare','package':{'plan_id':'known'}}}
        result=setup_journey({},config=cfg,inventory={'enabled':False})
        self.assertEqual('paused',result['steps'][1]['state'])
        self.assertEqual('configured',result['steps'][2]['state'])
        self.assertIn('Veröffentlichung ist aus',result['steps'][2]['summary'])
