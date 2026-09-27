import unittest
from pilotsuite.core.presence_adoption import classify_inspection,adoption_plan,validate_automation_ids
from pilotsuite.ha.client import HomeAssistantError

class PresenceAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.runtime={"owner":"input_boolean.room_presence","raw_sources":["binary_sensor.motion","binary_sensor.occupancy"],
                      "timer":"timer.pilotsuite_room_anwesenheitsnachlauf"}
    def inspection(self,actions=None,limitations=None):
        return {"entity_id":"automation.old_presence","config_fingerprint":"a"*64,"limitations":limitations or [],
          "sections":{"triggers":[{"source_references":["binary_sensor.motion"]}],
                      "actions":actions or [],"conditions":[]}}
    def test_existing_writer_is_conflict_not_takeover_ready(self):
        row=classify_inspection(self.inspection([{"target_references":["input_boolean.room_presence"]}]),self.runtime)
        self.assertEqual("conflict",row["classification"]);self.assertFalse(row["takeover_ready"])
    def test_templates_block_automatic_takeover(self):
        row=classify_inspection(self.inspection(limitations=["templates_not_evaluated"]),self.runtime)
        self.assertIn("templates_not_evaluated",row["blockers"]);self.assertFalse(row["takeover_ready"])
    def test_clean_related_reader_can_be_planned_but_plan_never_executes(self):
        plan=adoption_plan("room",7,self.runtime,[self.inspection()])
        self.assertEqual("ready_for_separate_takeover_approval",plan["recommendation"])
        self.assertFalse(plan["execution"]["allowed"]);self.assertEqual([],plan["execution"]["actions"])
        self.assertEqual(64,len(plan["fingerprint"]))
    def test_disabled_or_dynamic_references_do_not_create_confirmed_overlap(self):
        for state,limitation in (("unavailable","disabled_step"),("unknown","dynamic_enablement")):
            report=self.inspection([{"target_references":["input_boolean.room_presence"],"availability":state}],
                                   [limitation])
            report["sections"]["triggers"][0]["availability"]=state
            row=classify_inspection(report,self.runtime)
            self.assertEqual("unrelated",row["classification"])
            self.assertFalse(row["overlap"]);self.assertFalse(row["takeover_ready"])
            self.assertIn(limitation,row["blockers"])
            self.assertIn("no_direct_presence_source_trigger",row["blockers"])
    def test_new_alignment_contract_is_the_confirmed_owner(self):
        report=self.inspection([{"target_references":["input_boolean.room_presence"]}])
        report["alignment"]={"source_trigger_references":[],"target_action_references":[]}
        row=classify_inspection(report,self.runtime)
        self.assertEqual("unrelated",row["classification"])
        self.assertFalse(row["overlap"])
    def test_ids_are_bounded_and_canonical(self):
        self.assertEqual(["automation.a"],validate_automation_ids(["automation.a","automation.a"]))
        with self.assertRaises(HomeAssistantError): validate_automation_ids(["script.a"])

if __name__=="__main__": unittest.main()
