import unittest
from pilotsuite.core.setup_journey import setup_journey
class SetupJourneyTests(unittest.TestCase):
 def test_conflict_is_visible_and_apply_stays_locked(self):
  f={"modules":{"presence":{"state":"ready"}},"helper_reconciliation":{"counts":{"conflict":1,"create":0}}}
  r=setup_journey(f)
  self.assertEqual("attention",r["steps"][1]["state"])
  self.assertEqual("locked",r["steps"][-1]["state"])
  self.assertFalse(r["execution"]["allowed"])
if __name__=="__main__": unittest.main()
