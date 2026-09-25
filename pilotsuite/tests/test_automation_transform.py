import unittest
from pilotsuite.core.automation_transform import transformed_config,verify_takeover
class TransformTests(unittest.TestCase):
 def test_future_fields_and_legacy_singular_shape_survive(self):
  s={"entity_id":"automation.x","source":{"config":{"alias":"X","trigger":[1],"action":[2],"future":{"x":1}}}}
  out=transformed_config(s,{"triggers":[3],"actions":[4]})
  self.assertEqual([3],out["trigger"]); self.assertEqual([4],out["action"]); self.assertEqual({"x":1},out["future"])
 def test_identity_change_rejected_and_mismatch_requires_rollback(self):
  s={"entity_id":"automation.x","source":{"config":{"alias":"X","actions":[]}}}
  with self.assertRaises(ValueError): transformed_config(s,{"alias":"Y"})
  v=verify_takeover(s,{"entity_id":"automation.x","alias":"X","actions":[9]},{"actions":[]})
  self.assertFalse(v["verified"]); self.assertTrue(v["rollback_required"])
if __name__=="__main__": unittest.main()
