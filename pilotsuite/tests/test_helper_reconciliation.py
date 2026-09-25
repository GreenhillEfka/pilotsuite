import unittest
from pilotsuite.core.helper_reconciliation import reconcile_helpers
class HelperReconciliationTests(unittest.TestCase):
    def test_exact_id_reuses_but_name_never_silently_reuses(self):
        f={"helper_plan":[{"domain":"timer","key":"pilotsuite_room_anwesenheitsnachlauf","name":"Room timer"},
                          {"domain":"input_select","key":"pilotsuite_room_atmosphaere","name":"Mood"}]}
        r=reconcile_helpers(f,[{"entity_id":"timer.pilotsuite_room_anwesenheitsnachlauf","name":"Anything"},
                               {"entity_id":"input_select.old_mood","name":"Mood"}])
        self.assertEqual(["reuse","conflict"],[x["state"] for x in r["items"]])
        self.assertFalse(r["execution"]["allowed"])
    def test_missing_exact_helper_is_create(self):
        r=reconcile_helpers({"helper_plan":[{"domain":"timer","key":"pilotsuite_x"}]},[])
        self.assertEqual(1,r["counts"]["create"])
if __name__=="__main__": unittest.main()
