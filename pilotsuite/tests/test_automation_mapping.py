import unittest
from pilotsuite.core.automation_mapping import schema_mapping
class MappingTests(unittest.TestCase):
 def test_one_existing_automation_can_span_multiple_zone_modules(self):
  s={"projection":{"zone_references":["input_boolean.p","light.l","media_player.m"],"external_references":["sun.sun"]}}
  f={"modules":{"presence":{"sources":["input_boolean.p"]},"lighting":{"lights":["light.l"],"illuminance":[],"daylight_binary":[]},
                "media":{"players":["media_player.m"]},"climate":{"controllers":[],"temperature":[],"humidity":[]}}}
  r=schema_mapping(s,f)
  self.assertEqual("multi_module",r["classification"]); self.assertEqual(["sun.sun"],r["external_references"])
  self.assertFalse(r["execution"]["allowed"])
if __name__=="__main__": unittest.main()
