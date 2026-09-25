import unittest
from pilotsuite.core.automation_diff import semantic_diff,takeover_transaction
class AutomationDiffTests(unittest.TestCase):
 def test_unknown_fields_are_preserved_and_diff_is_semantic(self):
  s={"entity_id":"automation.x","source":{"fingerprint":"abc","config":{"alias":"X","mode":"single","actions":[1],"future":{"x":1}}}}
  d=semantic_diff(s,{"actions":[2]})
  self.assertEqual(["future"],d["preserved_unknown_fields"])
  self.assertEqual(["actions"],[x["field"] for x in d["changes"]])
  self.assertFalse(d["execution"]["allowed"])
  t=takeover_transaction(s,d,approve=True)
  self.assertEqual("ready_for_external_executor",t["state"]); self.assertFalse(t["execution"]["allowed"])
 def test_no_change_or_no_approval_blocks(self):
  s={"entity_id":"automation.x","source":{"fingerprint":"abc","config":{}}}
  d=semantic_diff(s,{})
  self.assertIn("no_change",takeover_transaction(s,d,approve=True)["blockers"])
  self.assertIn("explicit_approval_required",takeover_transaction(s,{"source_fingerprint":"abc","changes":[1]})["blockers"])
if __name__=="__main__": unittest.main()
