import unittest
from pilotsuite.core.automation_import import import_automation,adoption_plan
class AutomationImportTests(unittest.TestCase):
 def test_import_preserves_source_and_separates_external_refs(self):
  cfg={"alias":"Room light","triggers":[{"trigger":"state","entity_id":"binary_sensor.motion","to":"on"}],
       "actions":[{"action":"light.turn_on","target":{"entity_id":"light.room"}}],"custom_future_field":{"x":1}}
  s=import_automation("automation.room_light",cfg,zone_id="z",zone_revision=3,
      inventory_ids={"binary_sensor.motion","light.room"})
  self.assertEqual("execution_owner",s["ownership"]["home_assistant"])
  self.assertEqual(["custom_future_field"],s["source"]["unknown_root_fields"])
  self.assertEqual([],s["projection"]["external_references"])
  self.assertFalse(s["execution"]["allowed"])
 def test_takeover_requires_fresh_source_revision_and_approval(self):
  s=import_automation("automation.x",{"alias":"x"},zone_id="z",zone_revision=1,inventory_ids=set())
  fp=s["source"]["fingerprint"]
  self.assertEqual("needs_approval",adoption_plan(s,current_fingerprint=fp,zone_revision=1)["state"])
  self.assertEqual("blocked",adoption_plan(s,current_fingerprint="0"*64,zone_revision=1,approve=True)["state"])
  p=adoption_plan(s,current_fingerprint=fp,zone_revision=1,approve=True)
  self.assertEqual("ready_for_reviewed_takeover",p["state"]); self.assertFalse(p["execution"]["allowed"])
if __name__=="__main__": unittest.main()
