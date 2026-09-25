import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from pilotsuite.core.settings import Settings
from pilotsuite.core.capabilities import capability_matrix
from pilotsuite.domain.models import Neuron
from pilotsuite.domain.moods import calculate_moods
from pilotsuite.domain.synapses import build_suggestions
from pilotsuite.service import PilotSuiteService


def observation(domain, kind, value, quality="good", unit=None):
    return Neuron(f"{domain}.example", "test", kind, value, unit, quality, None, "test")


class ClimateTests(unittest.TestCase):
    def test_unknown_button_does_not_pollute_climate(self):
        moods = calculate_moods([
            observation("sensor", "temperature", 15.5, unit="°C"),
            observation("button", "button", None, "unknown"),
            observation("sensor", "battery", None, "unknown"),
        ], connected=True)
        scores = {m.name: m.score for m in moods}
        self.assertEqual(0, scores["uncertainty"])
        self.assertIsNone(scores["humidity_high"])
        self.assertIsNone(scores["stable"])
        self.assertEqual([], build_suggestions(moods, ("test",)))

    def test_missing_existing_sensor_still_warns(self):
        moods = calculate_moods([
            observation("sensor", "temperature", None, "unavailable", "°C"),
        ], connected=True)
        self.assertEqual(1, next(m.score for m in moods if m.name == "uncertainty"))
        self.assertTrue(any(s.rule_id.endswith("data-quality") for s in build_suggestions(moods, ("test",))))


class CapabilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_temperature_only_zone_is_operational(self):
        with tempfile.TemporaryDirectory() as directory:
            service = PilotSuiteService(Settings(Path(directory), Path(directory) / "options.json"))
            await service.selections.initialize()
            service.client.snapshot = AsyncMock(return_value={
                "areas": [{"area_id": "erdkeller"}],
                "entities": [{"entity_id": "sensor.temperature", "area_id": "erdkeller"}],
                "states": [{"entity_id": "sensor.temperature", "state": "15.5",
                    "attributes": {"device_class": "temperature", "unit_of_measurement": "°C"}}]})
            await service.selections.patch('erdkeller', 0, {'sensor.temperature': 'relevant'})
            await service._on_connection(True)
            state = await service.status()
            self.assertTrue(state["ready"])
            self.assertTrue(state["golden_zone"]["resolved"])
            self.assertEqual("available", state["capabilities"]["temperature"]["status"])
            self.assertEqual("not_present", state["capabilities"]["humidity"]["status"])
            await service._on_connection(False)
            self.assertFalse((await service.status())["ready"])

    async def test_empty_scope_is_separate_from_transport(self):
        with tempfile.TemporaryDirectory() as directory:
            service = PilotSuiteService(Settings(Path(directory), Path(directory) / "options.json"))
            await service.selections.initialize()
            service.client.snapshot = AsyncMock(return_value={})
            await service._on_connection(True)
            state = await service.status()
            self.assertTrue(state["ready"])
            self.assertFalse(state["golden_zone"]["resolved"])
            self.assertEqual("not_present", state["capabilities"]["motion"]["status"])


class ZoneComfortMatrixTests(unittest.TestCase):
    def test_lighting_accepts_lux_or_binary_daylight_but_not_light_alone(self):
        self.assertEqual("needs_sources", capability_matrix({"light":["light.x"]})["items"][1]["state"])
        self.assertEqual("ready", capability_matrix({"light":["light.x"],"illuminance":["sensor.lux"]})["items"][1]["state"])
        self.assertEqual("ready", capability_matrix({"light":["light.x"],"daylight_binary":["binary_sensor.bright"]})["items"][1]["state"])
        self.assertNotIn("timer", {x for row in capability_matrix({"presence":["binary_sensor.p"]})["items"] for x in row["optional_available"]})
