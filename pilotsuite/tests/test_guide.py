from copy import deepcopy
import unittest
from pilotsuite.core.guide import zone_guide


class GuideTests(unittest.TestCase):
    def setUp(self):
        self.inventory = dict(resolved=True, enabled=True, items=[dict(decision='relevant')], missing=[])
        self.report = dict(config=dict(roles={'presence':['binary_sensor.p']}, learning=True),
                           collection_state='collecting', patterns=[], progress={'windows':[]}, time_basis='Europe/Berlin')
        self.summary = {'presence': {'status':'available', 'valid':1}}

    def guide(self):
        return zone_guide(self.inventory, self.report, {'ready':True}, self.summary)

    def test_observation_without_consent_is_valid_and_does_not_recommend_enabling(self):
        self.report['config'].update(roles={}, learning=False)
        result = self.guide()
        self.assertEqual('optional', result['next_step']['state'])
        self.assertTrue(result['learning_optional'])
        self.assertFalse(result['execution_allowed'])
        self.assertEqual([], self.report['patterns'])

    def test_missing_sources_are_not_complete_even_when_some_are_relevant(self):
        self.inventory['missing'] = [{'decision':'relevant'}]
        result = self.guide()
        self.assertEqual('selection', result['next_step']['id'])
        self.assertEqual(1, result['selection']['missing_relevant'])

    def test_unreviewed_inventory_does_not_count_as_confirmed(self):
        self.inventory['items'] = [{'decision':'unreviewed'}, {'decision':'ignored'}]
        self.assertEqual('selection', self.guide()['next_step']['id'])
        self.assertEqual(0, self.guide()['selection']['relevant'])

    def test_pause_and_partial_presence_remain_explicit(self):
        self.inventory['enabled'] = False
        self.assertEqual('evaluation', self.guide()['next_step']['id'])
        self.inventory['enabled'] = True
        self.summary['presence'] = {'status':'partial', 'valid':1}
        self.report['config']['roles']['presence'].append('binary_sensor.q')
        self.assertEqual('presence', self.guide()['next_step']['id'])
        self.assertIn('1 von 2', self.guide()['next_step']['detail'])

    def test_readiness_precedes_waiting_and_never_claims_collection(self):
        self.report['collection_state'] = 'disconnected'
        result = zone_guide(self.inventory, self.report, {'ready':False}, self.summary)
        self.assertEqual('connection', result['next_step']['id'])
        self.assertEqual('attention', result['steps'][-1]['state'])

    def test_nearest_window_never_pools_days_events_or_changes_evidence(self):
        self.report['progress']['windows'] = [
            dict(start_hour=8,end_hour=10,day_group='weekday',events=4,days=3,missing_days=0,missing_events=1),
            dict(start_hour=18,end_hour=20,day_group='weekday',events=9,days=1,missing_days=2,missing_events=0)]
        before = deepcopy(self.report)
        result = self.guide()
        self.assertEqual(8, result['nearest_window']['start_hour'])
        self.assertIn('1 Aktivierungen und 0', result['next_step']['detail'])
        self.assertEqual('waiting', result['next_step']['state'])
        result['nearest_window']['events'] = 100
        self.assertEqual(before, self.report)

    def test_retained_patterns_with_revoked_consent_are_review_only(self):
        self.report['config']['learning'] = False
        self.report['patterns'] = [{'preference':'accepted'}]
        result = self.guide()
        self.assertEqual('review', result['next_step']['state'])
        self.assertIn('aufbewahrten', result['next_step']['detail'])
        self.assertFalse(result['execution_allowed'])
