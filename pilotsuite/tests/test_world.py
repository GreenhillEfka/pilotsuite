from __future__ import annotations

import unittest

from pilotsuite.ha.world import WorldModel


class WorldModelTests(unittest.IsolatedAsyncioTestCase):
    async def test_entity_inherits_device_area(self) -> None:
        world = WorldModel()
        await world.replace(
            {
                "config": {"version": "2026.9.3"},
                "areas": [{"area_id": "erdkeller", "name": "Erdkeller"}],
                "devices": [{"id": "device-1", "area_id": "erdkeller"}],
                "entities": [
                    {
                        "entity_id": "sensor.cellar",
                        "device_id": "device-1",
                        "area_id": None,
                    }
                ],
                "states": [
                    {
                        "entity_id": "sensor.cellar",
                        "state": "12.0",
                        "attributes": {"device_class": "temperature"},
                    }
                ],
            }
        )
        scope = await world.scope(("erdkeller",))
        self.assertEqual(["erdkeller"], scope["resolved_area_ids"])
        self.assertEqual(1, len(scope["entities"]))
        self.assertEqual("erdkeller", scope["entities"][0]["area_id"])

    async def test_unknown_area_is_reported(self) -> None:
        world = WorldModel()
        await world.replace({"areas": [], "devices": [], "entities": [], "states": []})
        scope = await world.scope(("erdkeller",))
        self.assertEqual(["erdkeller"], scope["missing_area_ids"])


if __name__ == "__main__":
    unittest.main()

