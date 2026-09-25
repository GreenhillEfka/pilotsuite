import unittest
from pilotsuite.core.responsibility import responsibility_conflicts
class ResponsibilityTests(unittest.TestCase):
 def test_multiple_existing_owners_block_takeover(self):
  snaps=[{"entity_id":"automation.a","mapping":{"modules":{"lighting":{"state":"matched"}}}},
         {"entity_id":"automation.b","mapping":{"modules":{"lighting":{"state":"matched"}}}}]
  r=responsibility_conflicts(snaps,["lighting","media"])
  self.assertTrue(r["blocked"]); self.assertEqual("conflict",r["items"][0]["state"])
  self.assertEqual("free",r["items"][1]["state"]); self.assertFalse(r["execution"]["allowed"])
if __name__=="__main__": unittest.main()
