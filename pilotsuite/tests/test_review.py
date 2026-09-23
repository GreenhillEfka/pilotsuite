import copy
import unittest
from pilotsuite.core.review import review_brief


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.pattern = dict(id='synthetic', title='<script>test</script>', algorithm='activity-v1',
                            sources=['binary_sensor.synthetic'], parameters={'min_events':5},
                            statistics={'activation_count':6,'distinct_day_count':3,
                                        'window_local':{'start_hour':8,'end_hour':10},'day_group':'weekday'},
                            rule_strength={'event_ratio':1.2}, confidence=None, preference=None)
        self.report = {'config':{'learning':True},'coverage':{},'context_windows':[]}

    def test_preference_never_changes_evidence_or_authorizes_execution(self):
        baseline = review_brief(self.pattern, self.report)
        for preference, state in [(None,'unreviewed'),('accepted','review_requested'),
                                  ('rejected','dismissed'),('later','deferred')]:
            self.pattern['preference'] = preference
            result = review_brief(self.pattern, self.report)
            self.assertEqual(state, result['state'])
            for field in ('statistics','rule_strength','confidence'):
                self.assertEqual(baseline[field], result[field])
            self.assertFalse(result['execution']['allowed'])
            self.assertEqual([], result['execution']['actions'])

    def test_context_must_match_day_group_and_local_window(self):
        wrong_day = {'start_hour':8,'day_group':'weekend','light_on':4}
        wrong_time = {'start_hour':10,'day_group':'weekday','light_on':3}
        self.report['context_windows'] = [wrong_day, wrong_time]
        self.assertIsNone(review_brief(self.pattern,self.report)['context'])
        match = {'start_hour':8,'day_group':'weekday','light_on':2}
        self.report['context_windows'].append(match)
        self.assertEqual(match, review_brief(self.pattern,self.report)['context'])

    def test_graph_edges_reference_existing_nodes_and_sources(self):
        graph = review_brief(self.pattern,self.report)['evidence_graph']
        ids = {n['id'] for n in graph['nodes']}
        for edge in graph['edges']:
            self.assertIn(edge['from'], ids)
            self.assertIn(edge['to'], ids)
        self.assertEqual(self.pattern['sources'], [n['label'] for n in graph['nodes'] if n['kind']=='source'])

    def test_review_is_detached_and_does_not_mutate_canonical_report(self):
        before = copy.deepcopy(self.pattern)
        result = review_brief(self.pattern,self.report)
        result['statistics']['activation_count'] = 999
        result['sources'].append('fake')
        self.assertEqual(before,self.pattern)

    def test_revoked_consent_and_zone_coverage_remain_explicit(self):
        self.report['config']['learning'] = False
        self.report['coverage'] = {'sampled_slots':3,'impaired_slots':1}
        result = review_brief(self.pattern,self.report)
        self.assertTrue(any('Lernfreigabe' in w for w in result['warnings']))
        self.assertTrue(any('unbeobachtete' in w for w in result['warnings']))
        self.assertEqual('whole_zone_retention_window',result['coverage_scope'])
        self.assertIsNone(result['confidence'])
