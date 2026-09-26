import copy
import json
import unittest

from pilotsuite.core.presence_lifecycle import inspect_presence_lifecycle as inspect


CATALOG = [
    {"entity_id": "binary_sensor.synthetic_door", "device_class": "door"},
    {"entity_id": "binary_sensor.synthetic_motion", "device_class": "motion"},
]


def lifecycle_config():
    return {
        "triggers": [
            {"trigger": "state", "entity_id": "binary_sensor.synthetic_door", "from": "on", "to": "off", "id": "door_closed"},
            {"trigger": "state", "entity_id": "binary_sensor.synthetic_motion", "from": "off", "to": "on", "id": "motion_started"},
            {"trigger": "event", "event_type": "timer.finished", "id": "private_timeout_token"},
        ],
        "actions": [{"choose": [
            {"conditions": [{"condition": "trigger", "id": "motion_started"}], "sequence": [
                {"action": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.synthetic_presence"}},
                {"action": "timer.start", "target": {"entity_id": "timer.synthetic_presence"}},
            ]},
            {"conditions": [{"condition": "trigger", "id": ["door_closed", "private_timeout_token"]}], "sequence": [
                {"action": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.synthetic_presence"}},
            ]},
        ]}],
    }


class PresenceLifecycleTests(unittest.TestCase):
    def test_boundary_and_motion_timeout_questions_are_separate_and_read_only(self):
        config = lifecycle_config(); before = copy.deepcopy(config)
        report = inspect(config, CATALOG)
        self.assertEqual(["boundary_close_can_clear_presence", "activity_edge_only_refreshes_timeout"],
                         [row["id"] for row in report["findings"]])
        self.assertFalse(report["execution"]["allowed"])
        self.assertEqual([], report["execution"]["actions"])
        self.assertEqual(before, config)

    def test_authored_ids_and_household_entities_are_not_returned(self):
        encoded = json.dumps(inspect(lifecycle_config(), CATALOG))
        for secret in ("door_closed", "motion_started", "private_timeout_token", "synthetic_presence", "synthetic_door"):
            self.assertNotIn(secret, encoded)
        self.assertIn("/triggers/0", encoded)

    def test_boundary_close_without_bidirectional_status_is_not_called_presence(self):
        config = lifecycle_config()
        config["actions"][0]["choose"][0]["sequence"] = [{"action": "timer.start", "target": {"entity_id": "timer.synthetic_presence"}}]
        report = inspect(config, CATALOG)
        self.assertNotIn("boundary_close_can_clear_presence", [row["id"] for row in report["findings"]])

    def test_device_class_not_entity_name_drives_semantics(self):
        catalog = [{"entity_id": "binary_sensor.synthetic_door", "device_class": "motion"},
                   {"entity_id": "binary_sensor.synthetic_motion", "device_class": "door"}]
        self.assertEqual([], inspect(lifecycle_config(), catalog)["findings"])

    def test_disabled_or_dynamic_paths_never_become_active_findings(self):
        for field in (False, "{{ enabled }}"):
            config = lifecycle_config()
            config["actions"][0]["choose"][1]["sequence"][0]["enabled"] = field
            report = inspect(config, CATALOG)
            self.assertNotIn("boundary_close_can_clear_presence", [row["id"] for row in report["findings"]])
        self.assertIn("dynamic_enablement", report["limitations"])

    def test_dynamic_or_ambiguous_selectors_remain_unknown(self):
        config = lifecycle_config()
        config["actions"][0]["choose"][1]["conditions"][0]["id"] = "{{ private }}"
        report = inspect(config, CATALOG)
        self.assertNotIn("boundary_close_can_clear_presence", [row["id"] for row in report["findings"]])
        self.assertIn("dynamic_trigger_selector", report["limitations"])
        self.assertNotIn("private", json.dumps(report))

        config = lifecycle_config()
        config["actions"][0]["choose"][1]["conditions"] = [{"condition": "or", "conditions": [
            {"condition": "trigger", "id": "door_closed"}, {"condition": "state", "entity_id": "input_boolean.other"}]}]
        report = inspect(config, CATALOG)
        self.assertNotIn("boundary_close_can_clear_presence", [row["id"] for row in report["findings"]])
        self.assertIn("conditional_semantics_not_evaluated", report["limitations"])

    def test_legacy_root_action_with_one_trigger_is_supported(self):
        config = {"trigger": {"platform": "state", "entity_id": "binary_sensor.synthetic_motion", "to": "on"},
                  "action": [{"service": "timer.start", "target": {"entity_id": "timer.synthetic_presence"}}]}
        self.assertEqual(["activity_edge_only_refreshes_timeout"],
                         [row["id"] for row in inspect(config, CATALOG)["findings"]])

    def test_duplicate_trigger_ids_preserve_all_structural_paths(self):
        config = lifecycle_config()
        config["triggers"].insert(1, {"trigger": "state", "entity_id": "binary_sensor.synthetic_door",
                                      "from": "on", "to": "off", "id": "door_closed"})
        paths = inspect(config, CATALOG)["findings"][0]["evidence"][0]["trigger_paths"]
        self.assertEqual(["/triggers/0", "/triggers/1"], paths)

    def test_stale_transport_withholds_lifecycle_claims(self):
        report = inspect(lifecycle_config(), CATALOG, False)
        self.assertEqual([], report["findings"])
        self.assertEqual(["snapshot_stale"], report["limitations"])
