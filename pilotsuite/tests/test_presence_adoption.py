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
    def test_clean_structure_is_reviewable_not_takeover_ready(self):
        plan=adoption_plan("room",7,self.runtime,[self.inspection()])
        self.assertEqual("review_existing_control",plan["recommendation"])
        self.assertFalse(plan["automations"][0]["takeover_ready"])
        self.assertFalse(plan["execution"]["allowed"]);self.assertEqual([],plan["execution"]["actions"])
        self.assertEqual(64,len(plan["fingerprint"]))

    def test_empty_or_unresolved_review_never_claims_readiness(self):
        for reports in ([], [self.inspection(limitations=['templates_not_evaluated'])]):
            with self.subTest(reports=reports):
                if reports:
                    reports[0]['sections']['triggers'] = []
                plan = adoption_plan('room', 7, self.runtime, reports, include_unrelated=True)
                self.assertEqual('inspect_missing_relationships', plan['recommendation'])
                if reports:
                    self.assertIn('templates_not_evaluated', plan['blockers'])

    def test_reuse_review_keeps_controllers_and_consumers_without_executable_changes(self):
        from copy import deepcopy
        reports = [self.inspection([{'kind': 'service_call', 'availability': 'available',
            'service': 'input_boolean.turn_on', 'target_references': [self.runtime['owner']]}])]
        before = deepcopy(reports)
        plan = adoption_plan('room', 7, self.runtime, reports)
        row = plan['automations'][0]
        self.assertEqual('retain_controller', row['reuse_disposition'])
        self.assertEqual(['binary_sensor.motion', self.runtime['owner']], row['affected_entities'])
        review = plan['reuse_review']
        self.assertEqual('existing_automations', review['controller_before'])
        self.assertEqual(review['controller_before'], review['controller_after'])
        self.assertEqual([], review['proposed_changes'])
        self.assertFalse(review['apply_implemented'])
        self.assertEqual({'timing', 'unknown_inputs', 'manual_override', 'dependencies',
            'single_writer', 'backup_recovery'}, {c['id'] for c in review['checks']})
        self.assertTrue(all(c['state'] == 'open' for c in review['checks']))
        self.assertEqual(before, reports)

    def test_unresolved_inspection_change_invalidates_review_fingerprint(self):
        report = self.inspection(limitations=['dynamic_enablement'])
        report['sections']['triggers'][0]['availability'] = 'unknown'
        before = adoption_plan('room', 7, self.runtime, [report])
        report['config_fingerprint'] = 'b' * 64
        after = adoption_plan('room', 7, self.runtime, [report])
        self.assertNotEqual(before['fingerprint'], after['fingerprint'])
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

    def test_existing_status_consumer_is_not_discarded_as_unrelated(self):
        from pilotsuite.domain.automation_inspection import inspect_automation
        runtime = {**self.runtime, "sensor": "binary_sensor.room_presence"}
        draft = {"current_pattern": {"sources": runtime["raw_sources"] + [
            runtime["owner"], runtime["sensor"], runtime["timer"]]},
            "fields": {"target_ids": [runtime["owner"], runtime["timer"], runtime["sensor"]]}}
        for section in ("triggers", "conditions"):
            with self.subTest(section=section):
                config = {section: [{"trigger" if section == "triggers" else "condition":
                    "state", "entity_id": runtime["sensor"], "state": "on", "to": "on"}],
                    "actions": [{"action": "light.turn_on", "target": {"entity_id": "light.room"}}]}
                inspected = inspect_automation(config, draft, "automation.light")
                row = classify_inspection(inspected, runtime)
                self.assertTrue(row["overlap"], "A downstream consumer belongs in the existing presence chain")
                self.assertEqual("consumer", row["usage"])
                self.assertEqual("retain_consumer", row["reuse_disposition"])
                self.assertEqual([runtime["sensor"]], row["reads_status"])
                self.assertFalse(row["writes_owner"])

    def test_writer_with_other_actions_is_not_described_as_only_presence_control(self):
        from pilotsuite.domain.automation_inspection import inspect_automation
        draft = {"current_pattern": {"sources": self.runtime["raw_sources"]},
                 "fields": {"target_ids": [self.runtime["owner"], self.runtime["timer"]]}}
        inspected = inspect_automation({"triggers": [{"trigger": "state",
            "entity_id": "binary_sensor.motion", "to": "on"}], "actions": [
            {"action": "input_boolean.turn_on", "target": {"entity_id": self.runtime["owner"]}},
            {"action": "light.turn_on", "target": {"entity_id": "light.room"}}]},
            draft, "automation.mixed")
        row = classify_inspection(inspected, self.runtime)
        self.assertEqual("mixed_writer", row.get("usage"))
        self.assertEqual("review_mixed_controller", row["reuse_disposition"])
        self.assertTrue(row["writes_owner"])
        self.assertFalse(row["takeover_ready"])

    def test_update_entity_is_not_mislabeled_as_boolean_control(self):
        from pilotsuite.domain.automation_inspection import inspect_automation
        draft = {"current_pattern": {"sources": self.runtime["raw_sources"]},
                 "fields": {"target_ids": [self.runtime["owner"]]}}
        inspected = inspect_automation({"triggers": [], "actions": [
            {"action": "homeassistant.update_entity", "target": {"entity_id": self.runtime["owner"]}}]},
            draft, "automation.refresh")
        row = classify_inspection(inspected, self.runtime)
        self.assertFalse(row["writes_owner"])

if __name__=="__main__": unittest.main()
