import unittest
from pilotsuite.core.logic_review import classify_logic,summarize_logic
class LogicReviewTests(unittest.TestCase):
    def test_missing_reference_beats_reuse(self):
        r=classify_logic("automation.x",["input_boolean.p","binary_sensor.m","light.old"],
          owner="input_boolean.p",raw_sources=["binary_sensor.m"],targets=["light.main"],missing=["light.old"])
        self.assertEqual("repair",r["state"]); self.assertEqual(["light.old"],r["missing"])
    def test_reuse_requires_owner_and_raw_source(self):
        self.assertEqual("reuse",classify_logic("automation.x",["input_boolean.p","binary_sensor.m"],
          owner="input_boolean.p",raw_sources=["binary_sensor.m"])["state"])
        self.assertEqual("inspect",classify_logic("automation.x",["input_boolean.p"],
          owner="input_boolean.p",raw_sources=["binary_sensor.m"])["state"])
        self.assertFalse(summarize_logic([])["execution"]["allowed"])
if __name__=="__main__": unittest.main()
