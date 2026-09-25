import unittest
from pilotsuite.core.migration import new_record,transition
class MigrationTests(unittest.TestCase):
 def test_staged_migration_cannot_skip_review(self):
  r=new_record("automation.x","z","abc")
  r=transition(r,"imported"); r=transition(r,"reviewed"); r=transition(r,"approved")
  self.assertEqual(3,r["revision"]); self.assertFalse(r["execution"]["allowed"])
  with self.assertRaises(ValueError): transition(new_record("automation.x","z","abc"),"applied")
 def test_verified_can_be_rolled_back(self):
  r=new_record("automation.x","z","abc")
  for s in ("imported","reviewed","approved","applied","verified"): r=transition(r,s)
  self.assertEqual("rolled_back",transition(r,"rolled_back")["state"])
if __name__=="__main__": unittest.main()
