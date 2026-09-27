import copy
import tempfile
import unittest
from pathlib import Path

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
                      "candidate_since": None, "last_proposal_at": None, "last_target": None}):
            with self.subTest(value=value), self.assertRaises(InvalidSelection):
                validate_lighting_checkpoint(value)
        with self.assertRaises(InvalidSelection):
            advance_lighting_preview(None, now=float("nan"), presence_state="occupied",
                                     daylight_lux=10)
        with self.assertRaises(InvalidSelection):
            advance_lighting_preview(None, now=0, presence_state="occupied",
                                     daylight_lux=10, current_brightness=True)

    def test_all_scenarios_are_bounded_non_executable_data(self):
        self.assertEqual(6, len(PREVIEW_SCENARIOS))
        for name in PREVIEW_SCENARIOS:
            with self.subTest(name=name):
                report = replay_lighting_scenario(name)
                self.assertEqual(name, report["id"])
                self.assertLessEqual(len(report["steps"]), 6)
                self.assertTrue(all(set(row["proposed_settings"]) <= {
                    "on", "brightness_pct", "color_temp_kelvin"} for row in report["steps"]))
                self.assertTrue(any("nicht ausgeführt" in text for text in report["limitations"]))


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


if __name__=="__main__": unittest.main()
