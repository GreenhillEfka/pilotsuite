import unittest
from pilotsuite.core.adoption_view import adoption_summary
class AdoptionViewTests(unittest.TestCase):
 def test_summary_is_user_facing_but_non_executable(self):
  s={"title":"Licht","entity_id":"automation.light","projection":{"external_references":["sun.sun"]}}
  m={"modules":{"lighting":{"state":"matched"},"media":{"state":"not_evidenced"}}}
  d={"changes":[{"field":"conditions"}]}
  r=adoption_summary(s,m,d)
  self.assertEqual(["lighting"],r["modules"]); self.assertEqual(["conditions"],r["proposed_change_fields"])
  self.assertFalse(r["execution"]["allowed"])
if __name__=="__main__": unittest.main()
