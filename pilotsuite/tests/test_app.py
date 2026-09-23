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
            ingress_allowed_peers=("127.0.0.1",),
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

    async def test_history_routes_and_asset_preserve_ingress_boundary(self):
        from unittest.mock import AsyncMock
        from pilotsuite.app import SERVICE_KEY
        from pilotsuite.core.selections import SelectionConflict
        service=self.client.server.app[SERVICE_KEY]
        service.history_view=AsyncMock(return_value={'zone_id':'a','trends':{}})
        response=await self.client.post('/api/v1/zones/a/history',json={'start':'x'})
        self.assertEqual(200,response.status)
        service.history_view.assert_awaited_once_with('a',{'start':'x'},import_learning=False)
        service.history_view.side_effect=SelectionConflict('changed')
        response=await self.client.post('/api/v1/zones/a/history/import',json={'consent':True})
        self.assertEqual(409,response.status)
        response=await self.client.get('/assets/history.js')
        self.assertEqual(200,response.status)
        self.assertIn('renderHistoryChart',await response.text())
        response=await self.client.post('/api/v1/zones/a/history',data='{broken')
        self.assertEqual(400,response.status)


if __name__ == "__main__":
    unittest.main()
