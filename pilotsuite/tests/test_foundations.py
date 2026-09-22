from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from aiohttp.test_utils import TestClient, TestServer

from pilotsuite.app import create_app
from pilotsuite.core.settings import Settings
from pilotsuite.domain.moods import calculate_moods
from pilotsuite.domain.neurons import build_neurons
from pilotsuite.domain.synapses import build_suggestions
from pilotsuite.ha.world import WorldModel
from pilotsuite.service import PilotSuiteService


def scope(value="12", unit="°C", kind="temperature"):
    return {"entities": [{"entity_id": "sensor.test", "area_id": "erdkeller",
        "registry": {}, "state": {"state": value, "attributes": {
            "device_class": kind, "unit_of_measurement": unit}}}]}


class SemanticTests(unittest.TestCase):
    def test_temperature_units(self):
        for value, unit in [("20", "°C"), ("68", "°F"), ("293.15", "K")]:
            with self.subTest(unit=unit):
                result = build_neurons(scope(value, unit))[0]
                self.assertAlmostEqual(20, result.value)
                self.assertEqual("°C", result.unit)

    def test_invalid_climate_values(self):
        for value, unit, kind in [("nan", "°C", "temperature"),
                ("inf", "%", "humidity"), ("abc", "°C", "temperature"),
                ("-274", "°C", "temperature"), ("101", "%", "humidity"),
                ("10", None, "temperature"), ("on", "%", "humidity")]:
            with self.subTest(value=value, unit=unit):
                result = build_neurons(scope(value, unit, kind))[0]
                self.assertIsNone(result.value)
                self.assertNotEqual("good", result.quality)

    def test_no_climate_is_not_stable(self):
        observations = build_neurons(scope("on", None, "switch"))
        moods = {m.name: m for m in calculate_moods(observations, connected=True)}
        self.assertIsNone(moods["stable"].score)
        self.assertIsNone(moods["uncertainty"].score)
        self.assertEqual(["humidity", "temperature"], moods["uncertainty"].evidence[0]["missing_required_kinds"])

    def test_severity_is_not_confidence_and_id_does_not_flap(self):
        results = []
        for humidity, areas in [("75", ("b", "a")), ("80", ("a", "b"))]:
            moods = calculate_moods(build_neurons(scope(humidity, "%", "humidity")), connected=True)
            results.append(next(s for s in build_suggestions(moods, areas) if s.rule_id.endswith("humidity-high")))
        self.assertEqual(results[0].id, results[1].id)
        self.assertNotEqual(results[0].severity, results[1].severity)
        self.assertIsNone(results[0].confidence)


class IngressTests(unittest.IsolatedAsyncioTestCase):
    async def test_denies_direct_and_spoofed_requests(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = Settings(Path(directory), Path(directory) / "options.json")
            async with TestClient(TestServer(create_app(settings))) as client:
                for path in ["/", "/api/v1/status", "/api/v1/audit", "/health/ready"]:
                    response = await client.get(path, headers={"X-Forwarded-For": "172.30.32.2"})
                    self.assertEqual(403, response.status)
                self.assertEqual(200, (await client.get("/health")).status)
                self.assertEqual(403, (await client.post("/api/v1/plans", json={})).status)

    async def test_repeated_slashes_and_assets_without_redirect(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = Settings(Path(directory), Path(directory) / "options.json",
                                ingress_allowed_peers=("127.0.0.1",))
            async with TestClient(TestServer(create_app(settings))) as client:
                for path in ["////", "////assets/app.js", "////api/v1/status?test=1"]:
                    reader, writer = await asyncio.open_connection(client.server.host, client.server.port)
                    writer.write(f"GET {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode())
                    await writer.drain()
                    reply = await asyncio.wait_for(reader.read(), 5)
                    writer.close()
                    await writer.wait_closed()
                    self.assertTrue(reply.startswith(b"HTTP/1.1 200"), reply[:200])
                self.assertEqual(404, (await client.get("/unknown")).status)


class ProjectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_older_event_cannot_overwrite_snapshot(self):
        world = WorldModel()
        await world.replace({"states": [{"entity_id": "sensor.test", "state": "20",
            "last_updated": "2026-09-22T12:00:00+00:00"}],
            "areas": [{"area_id": "a"}],
            "entities": [{"entity_id": "sensor.test", "area_id": "a"}]})
        await world.update_state({"entity_id": "sensor.test", "new_state": {
            "state": "10", "last_updated": "2026-09-22T11:59:00+00:00"}})
        self.assertEqual("20", (await world.scope(("a",)))["entities"][0]["state"]["state"])

    async def test_disabled_entities_are_excluded(self):
        world = WorldModel()
        await world.replace({"areas": [{"area_id": "a"}], "entities": [
            {"entity_id": "sensor.disabled", "area_id": "a", "disabled_by": "user"}]})
        self.assertEqual([], (await world.scope(("a",)))["entities"])

    async def test_readiness_requires_stream_scope_and_climate(self):
        with tempfile.TemporaryDirectory() as directory:
            service = PilotSuiteService(Settings(Path(directory), Path(directory) / "options.json"))
            await service.selections.initialize()
            service.client.snapshot = AsyncMock(return_value={
                "areas": [{"area_id": "erdkeller"}],
                "entities": [{"entity_id": f"sensor.{kind}", "area_id": "erdkeller"}
                             for kind in ["temperature", "humidity"]],
                "states": [{"entity_id": f"sensor.{kind}", "state": value,
                            "attributes": {"device_class": kind, "unit_of_measurement": unit}}
                           for kind, value, unit in [("temperature", "12", "°C"), ("humidity", "60", "%")]]})
            await service.refresh(reason="test")
            self.assertFalse((await service.status())["ready"])
            await service._on_connection(True)
            self.assertTrue((await service.status())["ready"])
            await service._on_connection(False)
            self.assertFalse((await service.status())["ready"])
            service._stream_connected = True
            service._last_refresh_at = "2020-01-01T00:00:00+00:00"
            self.assertFalse((await service.status())["ready"])
