from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aiohttp.test_utils import TestClient, TestServer

from pilotsuite.app import create_app
from pilotsuite.core.settings import Settings


class AppSmokeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        settings = Settings(
            data_dir=Path(self.temp_dir.name),
            options_path=Path(self.temp_dir.name) / "options.json",
            refresh_interval_seconds=3600,
            supervisor_token="",
        )
        self.client = TestClient(TestServer(create_app(settings)))
        await self.client.start_server()

    async def asyncTearDown(self) -> None:
        await self.client.close()
        self.temp_dir.cleanup()

    async def test_liveness_survives_missing_home_assistant(self) -> None:
        response = await self.client.get("/health")
        self.assertEqual(200, response.status)
        body = await response.json()
        self.assertEqual("ok", body["status"])

        response = await self.client.get("/health/ready")
        self.assertEqual(503, response.status)
        body = await response.json()
        self.assertEqual("degraded", body["status"])

    async def test_plan_api_cannot_cross_apply_boundary(self) -> None:
        response = await self.client.post(
            "/api/v1/plans",
            json={
                "scope": ["erdkeller"],
                "actions": [{"domain": "fan", "service": "turn_on"}],
            },
        )
        self.assertEqual(201, response.status)
        plan = await response.json()
        self.assertFalse(plan["policy"]["allowed"])

        response = await self.client.post(
            f"/api/v1/transactions/{plan['id']}/apply"
        )
        self.assertEqual(409, response.status)
        body = await response.json()
        self.assertEqual("read_only_release", body["error"])


if __name__ == "__main__":
    unittest.main()

