import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from aiohttp.test_utils import TestClient, TestServer

from pilotsuite.app import SERVICE_KEY, create_app
from pilotsuite.core.lighting_policy import (
    PREVIEW_SCENARIOS,
    LightingCheckpoint,
    advance_lighting_preview,
    lighting_target,
    replay_lighting_scenario,
    should_adjust,
    validate_lighting_checkpoint,
)
from pilotsuite.core.lighting_decision import build_lighting_decision
from pilotsuite.core.selections import InvalidSelection
from pilotsuite.core.settings import Settings


class LightingPolicyTests(unittest.TestCase):
    def test_daylight_reduces_target_and_mood_only_offsets_bounds(self):
        dark=lighting_target(outdoor_lux=50,occupied=True)
        bright=lighting_target(outdoor_lux=12000,occupied=True)
        self.assertGreater(dark["target"],bright["target"])
        self.assertFalse(dark["execution"]["allowed"])
        self.assertGreater(lighting_target(outdoor_lux=1000,occupied=True,atmosphere="focus")["target"],
                           lighting_target(outdoor_lux=1000,occupied=True,atmosphere="relax")["target"])
    def test_absence_or_bad_daylight_means_no_change(self):
        self.assertIsNone(lighting_target(outdoor_lux=50,occupied=False)["target"])
        self.assertIsNone(lighting_target(outdoor_lux=-1,occupied=True)["target"])
        self.assertIsNone(lighting_target(outdoor_lux=20,occupied=True,atmosphere="invented")["target"])
        self.assertFalse(should_adjust(50,None))
        self.assertFalse(should_adjust(50,53))
        self.assertTrue(should_adjust(50,60))

    def test_stable_band_and_bounded_step_before_suggestion(self):
        first = advance_lighting_preview(None, now=0, presence_state="occupied",
                                         daylight_lux=12000, current_brightness=50)
        self.assertEqual("stabilizing", first.status)
        stable = advance_lighting_preview(first.checkpoint, now=30,
                                          presence_state="occupied", daylight_lux=12000,
                                          current_brightness=50)
        self.assertEqual("suggest", stable.status)
        self.assertEqual(15, stable.desired_brightness)
        self.assertEqual(35, stable.proposed_settings["brightness_pct"])
        self.assertFalse("service" in stable.proposed_settings)

    def test_minimum_interval_and_deadband_prevent_chatter(self):
        point = LightingCheckpoint("dark", None, None, 10, 85)
        limited = advance_lighting_preview(point, now=30, presence_state="occupied",
                                           daylight_lux=50, current_brightness=20)
        self.assertEqual("rate_limited", limited.status)
        quiet = advance_lighting_preview(LightingCheckpoint("dark"), now=100,
                                         presence_state="occupied", daylight_lux=50,
                                         current_brightness=83)
        self.assertEqual("within_deadband", quiet.status)
        chatter = replay_lighting_scenario("threshold_chatter")
        self.assertTrue(all(not row["proposed_settings"] for row in chatter["steps"]))

    def test_return_to_current_band_clears_old_candidate_window(self):
        point = LightingCheckpoint("dim", "daylight", 10, None, None)
        returned = advance_lighting_preview(point, now=20, presence_state="occupied",
                                            daylight_lux=900, current_brightness=60)
        self.assertIsNone(returned.checkpoint.candidate_band)
        changed = advance_lighting_preview(returned.checkpoint, now=100,
                                           presence_state="occupied", daylight_lux=1100,
                                           current_brightness=60)
        self.assertEqual(100, changed.checkpoint.candidate_since)
        self.assertEqual("stabilizing", changed.status)

    def test_manual_unknown_and_missing_lux_hold(self):
        base = {"now": 0, "presence_state": "occupied", "daylight_lux": 10}
        self.assertEqual("hold", advance_lighting_preview(None, **base, manual_override=True).status)
        self.assertEqual("hold", advance_lighting_preview(None, **dict(base, presence_state="unknown")).status)
        self.assertEqual("hold", advance_lighting_preview(None, **dict(base, daylight_lux=None),
                                                           daylight_available=False).status)
        missing = advance_lighting_preview(None, **base, current_brightness=None)
        self.assertEqual("input_unavailable", missing.status)
        self.assertEqual({}, missing.proposed_settings)

    def test_night_vacancy_and_capabilities_remain_settings_only(self):
        vacant = advance_lighting_preview(None, now=0, presence_state="vacant",
                                          daylight_lux=0, night=True, current_on=True)
        self.assertEqual({"on": False}, vacant.proposed_settings)
        scenario = replay_lighting_scenario("capability_limits")
        self.assertEqual({"color_temp_kelvin": 2700}, scenario["steps"][-1]["proposed_settings"])
        self.assertNotIn("brightness_pct", scenario["steps"][-1]["proposed_settings"])
        point = LightingCheckpoint("dark")
        bounded = advance_lighting_preview(point, now=100, presence_state="occupied",
            daylight_lux=50, atmosphere="relax", supports_color_temp=True,
            minimum_kelvin=3000, current_brightness=50)
        self.assertEqual(3000, bounded.proposed_settings["color_temp_kelvin"])

    def test_invalid_checkpoint_and_inputs_are_rejected(self):
        for value in ({"band": "dark"}, {"band": "other", "candidate_band": None,
                      "candidate_since": None, "last_proposal_at": None, "last_target": None},
                      LightingCheckpoint("dark", "dim", None),
                      LightingCheckpoint("dark", None, 1),
                      LightingCheckpoint("dark", "dark", 1)):
            with self.subTest(value=value), self.assertRaises(InvalidSelection):
                validate_lighting_checkpoint(value)
        with self.assertRaises(InvalidSelection):
            advance_lighting_preview(None, now=float("nan"), presence_state="occupied",
                                     daylight_lux=10)
        with self.assertRaises(InvalidSelection):
            advance_lighting_preview(None, now=0, presence_state="occupied",
                                     daylight_lux=10, current_brightness=True)
        with self.assertRaises(InvalidSelection):
            advance_lighting_preview(LightingCheckpoint("dark", "dim", 10), now=9,
                                     presence_state="occupied", daylight_lux=500)
        with self.assertRaises(InvalidSelection):
            advance_lighting_preview(LightingCheckpoint("dark", None, None, 10, 80), now=9,
                                     presence_state="occupied", daylight_lux=10)

    def test_all_scenarios_are_bounded_non_executable_data(self):
        self.assertEqual(7, len(PREVIEW_SCENARIOS))
        for name in PREVIEW_SCENARIOS:
            with self.subTest(name=name):
                report = replay_lighting_scenario(name)
                self.assertEqual(name, report["id"])
                self.assertLessEqual(len(report["steps"]), 6)
                self.assertTrue(all(set(row["proposed_settings"]) <= {
                    "on", "brightness_pct", "color_temp_kelvin"} for row in report["steps"]))
                self.assertTrue(any("nicht ausgeführt" in text for text in report["limitations"]))


class LightingDecisionTests(unittest.TestCase):
    def fixture(self, *, ready=True, light_state="on", lux_state="30"):
        roles = {"light": ["light.room"], "illuminance": ["sensor.lux"],
                 "daylight_binary": [], "presence": ["binary_sensor.motion"]}
        inventory = {"items": [
            {"entity_id": "light.room", "decision": "relevant", "suggested_role": "light",
             "state": light_state},
            {"entity_id": "sensor.lux", "decision": "relevant", "suggested_role": "illuminance",
             "state": lux_state},
            {"entity_id": "binary_sensor.motion", "decision": "relevant", "suggested_role": "motion",
             "state": "off"},
        ]}
        summary = {"illuminance": {"status": "available", "value": 30, "unit": "lx",
                                    "aggregation": "median"},
                   "daylight_binary": {"status": "not_present", "active": None},
                   "light": {"status": "available", "active": True}}
        inspection = {"entity_id": "automation.room_light", "config_fingerprint": "a" * 64,
                      "limitations": [], "alignment": {
                          "source_trigger_references": ["binary_sensor.motion"],
                          "target_action_references": ["light.room"]}}
        return build_lighting_decision(zone_id="room", revision=3, roles=roles,
            inventory=inventory, summary=summary, transport_ready=ready,
            inspections=[inspection], checked_at="2026-09-27T00:00:00+00:00")

    def test_current_indoor_value_never_becomes_outdoor_daylight_proof(self):
        result = self.fixture()
        self.assertEqual("withheld", result["state"])
        self.assertEqual(30, result["current_zone_observation"]["illuminance"]["value"])
        self.assertEqual("not_determined",
                         result["current_zone_observation"]["physical_measurement_current"])
        self.assertFalse(result["daylight_basis"]["outdoor_daylight_confirmed"])
        self.assertEqual("direct_path", result["automation_review"]["items"][0]["state"])
        self.assertEqual("not_determined",
                         result["automation_review"]["items"][0]["duplicate_assessment"])
        self.assertEqual("run_synthetic_preview", result["next_step"]["id"])
        self.assertFalse(result["execution"]["allowed"])

    def test_missing_sources_and_transport_have_one_prioritized_next_step(self):
        disconnected = self.fixture(ready=False)
        self.assertEqual("reload_zone", disconnected["next_step"]["id"])
        no_light = self.fixture(light_state="unavailable")
        self.assertEqual("configure_sources", no_light["next_step"]["id"])
        no_lux = self.fixture(lux_state="unknown")
        self.assertEqual("configure_sources", no_lux["next_step"]["id"])
        for result in (disconnected, no_light, no_lux):
            self.assertEqual({"id", "label"}, set(result["next_step"]))
            self.assertFalse(result["persisted"])


class LightingPreviewApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.app = create_app(Settings(root, root / "options.json",
            golden_zone_area_ids=("room",), supervisor_token="",
            refresh_interval_seconds=3600, ingress_allowed_peers=("127.0.0.1",)))
        self.client = TestClient(TestServer(self.app))
        await self.client.start_server()
        self.service = self.app[SERVICE_KEY]
        await self.service.world.replace({"areas": [{"area_id": "room", "name": "Synthetic"}],
            "entities": [{"entity_id": "light.room", "area_id": "room", "platform": "demo",
                          "unique_id": "light", "disabled_by": None},
                         {"entity_id": "sensor.lux", "area_id": "room", "platform": "demo",
                          "unique_id": "lux", "disabled_by": None}],
            "states": [{"entity_id": "light.room", "state": "on", "attributes": {}},
                       {"entity_id": "sensor.lux", "state": "30", "attributes": {
                           "device_class": "illuminance", "unit_of_measurement": "lx"}}],
            "devices": []})
        await self.service._derive()
        await self.service.selections.patch("room", 0,
            {"light.room": "relevant", "sensor.lux": "relevant"})
        await self.service.context.configure("room", 1,
            {"light": ["light.room"], "illuminance": ["sensor.lux"]}, False)
        await self.service._derive()

    async def asyncTearDown(self):
        await self.client.close()
        self.temp.cleanup()

    async def test_preview_is_explicit_revision_bound_and_non_persistent(self):
        before = copy.deepcopy(await self.service.context.get("room"))
        response = await self.client.post("/api/v1/zones/room/lighting-preview",
            json={"revision": 2, "scenario": "daylight_transition"})
        self.assertEqual(200, response.status)
        body = await response.json()
        self.assertEqual("pilotsuite-lighting-preview-v1", body["schema"])
        self.assertEqual(1, body["configured_target_count"])
        self.assertEqual(1, body["configured_reference_count"])
        self.assertEqual({"configured": 1, "currently_usable": 1}, body["zone_inputs"]["light"])
        self.assertEqual({"configured": 1, "currently_usable": 1}, body["zone_inputs"]["illuminance"])
        self.assertEqual({"configured": 0, "currently_usable": 0}, body["zone_inputs"]["daylight_binary"])
        self.assertEqual({"kind": "synthetic_outdoor_lux", "household_measurements_used": False,
                          "configured_daylight_reference_confirmed": False,
                          "reason": "no_explicit_outdoor_daylight_provenance"},
                         body["daylight_basis"])
        self.assertFalse(body["persisted"])
        self.assertEqual({"allowed": False, "reason": "synthetic_preview_only", "actions": []},
                         body["execution"])
        self.assertEqual(before, await self.service.context.get("room"))

    async def test_preview_rejects_stale_unknown_and_malformed_requests(self):
        for payload, status in [({"revision": 1, "scenario": "manual_override"}, 409),
                                ({"revision": 2, "scenario": "from-data"}, 400),
                                ({"revision": True, "scenario": "manual_override"}, 400),
                                ([], 400)]:
            with self.subTest(payload=payload):
                response = await self.client.post("/api/v1/zones/room/lighting-preview", json=payload)
                self.assertEqual(status, response.status)
        malformed = await self.client.post("/api/v1/zones/room/lighting-preview", data="{broken")
        self.assertEqual(400, malformed.status)

    async def test_live_decision_is_explicit_transient_and_structurally_reads_automations(self):
        self.service._connected = self.service._stream_connected = True
        from datetime import UTC, datetime
        self.service._last_refresh_at = datetime.now(UTC).isoformat()
        self.service.client.related_automations = AsyncMock(return_value={
            "sensor.lux": ["automation.room_light"], "light.room": ["automation.room_light"]})
        self.service.client.automation_config = AsyncMock(return_value={
            "triggers": [{"trigger": "numeric_state", "entity_id": "sensor.lux"}],
            "actions": [{"action": "light.turn_on", "target": {"entity_id": "light.room"}}]})
        inventory = await self.service.selection_inventory("room")
        before = copy.deepcopy(await self.service.context.get("room"))
        response = await self.client.post("/api/v1/zones/room/lighting-decision",
                                          json={"revision": inventory["revision"]})
        self.assertEqual(200, response.status)
        body = await response.json()
        self.assertEqual("pilotsuite-lighting-decision-v1", body["schema"])
        self.assertEqual("withheld", body["state"])
        self.assertEqual(30.0, body["current_zone_observation"]["illuminance"]["value"])
        self.assertFalse(body["daylight_basis"]["outdoor_daylight_confirmed"])
        self.assertEqual("direct_path", body["automation_review"]["items"][0]["state"])
        self.assertFalse(body["persisted"])
        self.assertEqual([], body["execution"]["actions"])
        self.assertEqual(before, await self.service.context.get("room"))
        self.service.client.related_automations.assert_awaited_once()
        self.service.client.automation_config.assert_awaited_once_with("automation.room_light")

    async def test_live_decision_rejects_stale_or_malformed_requests_before_ha_reads(self):
        self.service.client.related_automations = AsyncMock()
        inventory = await self.service.selection_inventory("room")
        for payload, status in [({"revision": inventory["revision"] + 1}, 409),
                                ({"revision": True}, 400),
                                ({"revision": inventory["revision"], "url": "https://example.invalid"}, 400),
                                ([], 400)]:
            with self.subTest(payload=payload):
                response = await self.client.post("/api/v1/zones/room/lighting-decision", json=payload)
                self.assertEqual(status, response.status)
        self.service.client.related_automations.assert_not_awaited()

    async def test_live_decision_rejects_roles_changed_during_automation_read(self):
        self.service._connected = self.service._stream_connected = True
        from datetime import UTC, datetime
        self.service._last_refresh_at = datetime.now(UTC).isoformat()
        self.service.client.related_automations = AsyncMock(return_value={
            "sensor.lux": ["automation.room_light"]})

        async def change_roles(_automation_id):
            current = await self.service.selection_inventory("room")
            await self.service.context.configure(
                "room", current["revision"],
                {"light": ["light.room"], "illuminance": []}, False)
            return {"triggers": [], "actions": []}

        self.service.client.automation_config = AsyncMock(side_effect=change_roles)
        inventory = await self.service.selection_inventory("room")
        response = await self.client.post(
            "/api/v1/zones/room/lighting-decision",
            json={"revision": inventory["revision"]})
        self.assertEqual(409, response.status)


if __name__=="__main__": unittest.main()
