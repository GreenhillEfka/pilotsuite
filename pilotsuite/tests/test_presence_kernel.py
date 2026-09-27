import copy
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock

from aiohttp.test_utils import TestClient, TestServer

from pilotsuite.app import SERVICE_KEY, create_app
from pilotsuite.core.context import ContextStore
from pilotsuite.core.presence_kernel import (
    PresenceCheckpoint,
    advance_presence,
    replay_scenario,
    validate_checkpoint,
)
from pilotsuite.core.selections import InvalidSelection, SelectionConflict
from pilotsuite.core.settings import Settings
from pilotsuite.core.zone_presence import evaluate


class PresenceKernelTests(unittest.TestCase):
    def test_cold_all_clear_stays_unknown_without_fabricated_deadline(self):
        result = advance_presence(None, continuous=["off"], now=100)
        self.assertEqual("unknown", result.checkpoint.state)
        self.assertIsNone(result.checkpoint.deadline)
        self.assertEqual((), result.proposed_actions)

    def test_continuous_presence_then_clear_starts_one_durable_grace(self):
        occupied = advance_presence(None, continuous=["on", "off"], now=100)
        self.assertEqual(("timer.cancel", "owner.on"), occupied.proposed_actions)
        grace = advance_presence(occupied.checkpoint, continuous=["off", "off"], now=110)
        self.assertEqual("grace", grace.checkpoint.state)
        self.assertEqual(410, grace.checkpoint.deadline)
        pending = advance_presence(grace.checkpoint, continuous=["off", "off"], now=200)
        self.assertEqual(410, pending.checkpoint.deadline)
        self.assertEqual(("owner.on",), pending.proposed_actions)

    def test_restart_preserves_deadline_and_expiry_requires_clear_sources(self):
        previous = PresenceCheckpoint("grace", 2, 410, 100, "all_clear_starts_grace")
        restarted = advance_presence(previous, continuous=["off"], now=250, restart=True)
        self.assertEqual(410, restarted.checkpoint.deadline)
        self.assertEqual("restart_preserves_deadline", restarted.checkpoint.reason)
        unknown = advance_presence(restarted.checkpoint, continuous=["unknown"], now=500)
        self.assertEqual("unknown", unknown.checkpoint.state)
        self.assertEqual((), unknown.proposed_actions)
        vacant = advance_presence(restarted.checkpoint, continuous=["off"], now=500)
        self.assertEqual("vacant", vacant.checkpoint.state)
        self.assertEqual(("owner.off",), vacant.proposed_actions)

    def test_pulse_renews_grace_but_is_not_continuous_presence(self):
        first = advance_presence(None, continuous=["off"], pulse=True, now=10)
        second = advance_presence(first.checkpoint, continuous=["off"], pulse=True, now=200)
        self.assertEqual("grace", second.checkpoint.state)
        self.assertEqual(500, second.checkpoint.deadline)
        self.assertEqual(("timer.start", "owner.on"), second.proposed_actions)

    def test_unknown_dependency_and_manual_cancel_never_claim_vacancy(self):
        previous = PresenceCheckpoint("grace", 1, 20, 0, "activity_pulse")
        dependency = advance_presence(previous, continuous=["off"],
                                      dependencies_confirmed=False, now=40)
        cancelled = advance_presence(previous, continuous=["off"],
                                     manual_cancel=True, now=40)
        self.assertEqual("unknown", dependency.checkpoint.state)
        self.assertEqual("unknown", cancelled.checkpoint.state)
        self.assertEqual((), dependency.proposed_actions)
        self.assertEqual((), cancelled.proposed_actions)

    def test_invalid_values_and_partial_checkpoint_are_rejected(self):
        for value in ({"state": "unknown"}, {"state": "other", "generation": 0,
                      "deadline": None, "last_activity_at": None, "reason": "x"}):
            with self.subTest(value=value), self.assertRaises(InvalidSelection):
                validate_checkpoint(value)
        with self.assertRaises(InvalidSelection):
            advance_presence(None, continuous=[], now=0)
        with self.assertRaises(InvalidSelection):
            advance_presence(None, continuous=["off"], now=True)
        with self.assertRaises(InvalidSelection):
            advance_presence(None, continuous=["off"], now=float("nan"))

    def test_every_allowlisted_replay_is_bounded_and_synthetic(self):
        for name in ("continuous_then_clear", "pulse_refresh", "restart_during_grace",
                     "unknown_source", "dependency_unknown"):
            with self.subTest(name=name):
                replay = replay_scenario(name)
                self.assertEqual(name, replay["id"])
                self.assertGreaterEqual(len(replay["steps"]), 1)
                self.assertLessEqual(len(replay["steps"]), 4)
                self.assertTrue(all(step["state"] in {"occupied", "grace", "vacant", "unknown"}
                                    for step in replay["steps"]))
                self.assertTrue(any("nicht ausgeführt" in text for text in replay["limitations"]))
        restart = replay_scenario("restart_during_grace")["steps"]
        self.assertEqual(restart[1]["deadline"], restart[2]["deadline"])
        self.assertEqual("vacant", restart[-1]["state"])


class ZonePresenceCoverageTests(unittest.TestCase):
    def test_required_unknown_in_shared_group_never_proves_vacancy(self):
        def source(entity_id, required=True):
            return {"entity_id": entity_id, "kind": "continuous", "required": required,
                    "max_age": 0, "group": "shared_coverage", "can_start": True,
                    "active_states": ["on"]}

        spec = {"grace_seconds": 30, "clear_seconds": 0,
                "support_limit_seconds": 0, "comparison_entity": None,
                "sources": [source("binary_sensor.one"), source("binary_sensor.two")]}
        previous = {"kernel": {"state": "grace", "generation": 2,
                               "deadline": 120, "last_activity_at": 90,
                               "reason": "all_clear_starts_grace"}}

        for first, second, expected in (
            ("off", "unavailable", "unknown"),
            ("off", "off", "vacant"),
            ("on", "unavailable", "occupied"),
        ):
            with self.subTest(first=first, second=second):
                _, view = evaluate(spec, previous, {
                    "binary_sensor.one": {"state": first},
                    "binary_sensor.two": {"state": second},
                }, now=200, fresh=True)
                self.assertEqual(expected, view["state"])

        spec["sources"][0]["required"] = False
        _, view = evaluate(spec, previous, {
            "binary_sensor.one": {"state": "off"},
            "binary_sensor.two": {"state": "unavailable"},
        }, now=200, fresh=True)
        self.assertEqual("unknown", view["state"])

        spec["sources"][0]["required"] = True
        spec["sources"][1]["required"] = False
        _, view = evaluate(spec, previous, {
            "binary_sensor.one": {"state": "off"},
            "binary_sensor.two": {"state": "unavailable"},
        }, now=200, fresh=True)
        self.assertEqual("vacant", view["state"])


class PresenceReplayIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.app = create_app(Settings(root, root / "options.json",
            golden_zone_area_ids=("room",), supervisor_token="",
            refresh_interval_seconds=3600, ingress_allowed_peers=("127.0.0.1",)))
        self.client = TestClient(TestServer(self.app))
        await self.client.start_server()
        self.service = self.app[SERVICE_KEY]
        await self.service.world.replace({
            "areas": [{"area_id": "room", "name": "Synthetic room"}],
            "entities": [{"entity_id": "binary_sensor.motion", "area_id": "room",
                          "platform": "demo", "unique_id": "motion", "disabled_by": None},
                         {"entity_id": "input_boolean.owner", "area_id": "room",
                          "platform": "input_boolean", "unique_id": "owner", "disabled_by": None},
                         {"entity_id": "timer.pilotsuite_room_anwesenheitsnachlauf", "area_id": None,
                          "platform": "timer", "unique_id": "timer", "disabled_by": None}],
            "states": [{"entity_id": "binary_sensor.motion", "state": "off",
                        "attributes": {"device_class": "motion"}},
                       {"entity_id": "input_boolean.owner", "state": "off", "attributes": {}},
                       {"entity_id": "timer.pilotsuite_room_anwesenheitsnachlauf", "state": "idle",
                        "attributes": {"duration": "0:05:00"}}], "devices": []})
        await self.service._derive()
        await self.service.selections.patch("room", 0,
            {"binary_sensor.motion": "relevant", "input_boolean.owner": "relevant"})
        await self.service.context.configure("room", 1,
            {"presence": ["binary_sensor.motion", "input_boolean.owner"]}, False)

    async def asyncTearDown(self):
        await self.client.close()
        self.temp.cleanup()

    async def test_http_replay_is_explicit_non_persistent_and_read_only(self):
        before = copy.deepcopy(await self.service.context.get("room"))
        response = await self.client.post("/api/v1/zones/room/presence-runtime/replay",
            json={"revision": 2, "scenario": "restart_during_grace"})
        self.assertEqual(200, response.status)
        body = await response.json()
        self.assertEqual("pilotsuite-presence-replay-v1", body["schema"])
        self.assertFalse(body["persisted"])
        self.assertFalse(body["execution"]["allowed"])
        self.assertEqual([], body["execution"]["actions"])
        self.assertEqual(before, await self.service.context.get("room"))

    async def test_replay_rejects_unknown_scenario_stale_revision_and_bad_json(self):
        bad = await self.client.post("/api/v1/zones/room/presence-runtime/replay",
            json={"revision": 2, "scenario": "from-user-data"})
        self.assertEqual(400, bad.status)
        bad_type = await self.client.post("/api/v1/zones/room/presence-runtime/replay",
            json={"revision": 2, "scenario": []})
        self.assertEqual(400, bad_type.status)
        stale = await self.client.post("/api/v1/zones/room/presence-runtime/replay",
            json={"revision": 1, "scenario": "unknown_source"})
        self.assertEqual(409, stale.status)
        malformed = await self.client.post("/api/v1/zones/room/presence-runtime/replay",
            data="{broken")
        self.assertEqual(400, malformed.status)

    async def test_checkpoint_survives_reload_and_source_change_clears_it(self):
        point = PresenceCheckpoint("grace", 3, 500, 100, "activity_pulse")
        await self.service.context.save_presence_checkpoint("room", 2, point)
        reloaded = ContextStore(self.service.selections)
        self.assertEqual(500, (await reloaded.presence_checkpoint("room"))["deadline"])
        with self.assertRaises(SelectionConflict):
            await reloaded.save_presence_checkpoint("room", 1, point)
        await self.service.context.configure("room", 2, {}, False)
        cleared = await reloaded.presence_checkpoint("room")
        self.assertEqual("unknown", cleared["state"])
        self.assertIsNone(cleared["deadline"])

    async def test_dormant_runtime_uses_checkpoint_but_public_enable_stays_blocked(self):
        self.service._connected = self.service._stream_connected = True
        self.service.client.call_bounded_service = AsyncMock()
        self.service._presence_runtime_enabled.add("room")
        await self.service._reconcile_presence_zone("room", "synthetic_test", pulse=True)
        point = await self.service.context.presence_checkpoint("room")
        self.assertEqual("grace", point["state"])
        self.assertIsNotNone(point["deadline"])
        self.assertEqual(2, self.service.client.call_bounded_service.await_count)
        self.service.client.call_bounded_service.reset_mock()
        await self.service._reconcile_presence_zone("room", "synthetic_restart", restart=True)
        restarted = await ContextStore(self.service.selections).presence_checkpoint("room")
        self.assertEqual(point["deadline"], restarted["deadline"])
        self.service.client.call_bounded_service.assert_awaited_once_with(
            "input_boolean", "turn_on", "input_boolean.owner")
        self.service._presence_runtime_enabled.clear()
        self.service.client.call_bounded_service.reset_mock()
        with self.assertRaises(InvalidSelection):
            await self.service.configure_presence_runtime("room",
                {"revision": 2, "enabled": True, "confirm": True})
        self.service.client.call_bounded_service.assert_not_awaited()

    async def test_non_activation_event_still_reaches_dormant_runtime_reconcile(self):
        self.service._presence_runtime_enabled.add("room")
        self.service._reconcile_presence_zone = AsyncMock()
        stamp = datetime.now(UTC).isoformat()
        await self.service._on_state_change({"entity_id": "binary_sensor.motion",
            "old_state": {"state": "off"},
            "new_state": {"entity_id": "binary_sensor.motion", "state": "off",
                          "last_changed": stamp, "last_updated": stamp,
                          "attributes": {"device_class": "motion"}}})
        self.service._reconcile_presence_zone.assert_awaited_once_with(
            "room", "state_change", pulse=False)


if __name__ == "__main__":
    unittest.main()
