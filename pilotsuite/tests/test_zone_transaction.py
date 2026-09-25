import unittest
from pilotsuite.core.zone_transaction import build_transaction_plan
class ZoneTransactionTests(unittest.TestCase):
 def test_conflict_blocks_and_create_is_still_non_executable(self):
  inv={"zone_id":"z","revision":2}; f={"revision":2}
  blocked=build_transaction_plan(inv,f,{"items":[{"state":"conflict","entity_id":"timer.x"}]},{"revision":2,"approve":True})
  self.assertEqual("blocked",blocked["state"]); self.assertEqual([],blocked["steps"])
  ready=build_transaction_plan(inv,f,{"items":[{"state":"create","domain":"timer","key":"pilotsuite_z_x"}]},{"revision":2,"approve":True})
  self.assertEqual("ready_for_external_executor",ready["state"]); self.assertFalse(ready["execution"]["allowed"])
  self.assertEqual("created_in_this_transaction_only",ready["steps"][-1]["scope"])
if __name__=="__main__": unittest.main()
