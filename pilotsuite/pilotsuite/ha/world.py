"""Bounded in-memory projection of the Home Assistant source of truth."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any


class WorldModel:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._config: dict[str, Any] = {}
        self._areas: dict[str, dict[str, Any]] = {}
        self._devices: dict[str, dict[str, Any]] = {}
        self._entities: dict[str, dict[str, Any]] = {}
        self._states: dict[str, dict[str, Any]] = {}
        self._last_snapshot_at: str | None = None

    async def replace(self, snapshot: dict[str, Any]) -> None:
        async with self._lock:
            self._config = _as_dict(snapshot.get("config"))
            self._areas = _index(snapshot.get("areas"), "area_id")
            self._devices = _index(snapshot.get("devices"), "id")
            self._entities = _index(snapshot.get("entities"), "entity_id")
            self._states = _index(snapshot.get("states"), "entity_id")
            self._last_snapshot_at = datetime.now(UTC).isoformat()

    async def update_state(self, event_data: dict[str, Any]) -> None:
        entity_id = event_data.get("entity_id")
        new_state = event_data.get("new_state")
        if not isinstance(entity_id, str):
            return
        async with self._lock:
            if new_state is None:
                self._states.pop(entity_id, None)
            elif isinstance(new_state, dict):
                self._states[entity_id] = deepcopy(new_state)

    async def summary(self) -> dict[str, Any]:
        async with self._lock:
            return {
                "home_assistant_version": self._config.get("version"),
                "location_name": self._config.get("location_name"),
                "area_count": len(self._areas),
                "device_count": len(self._devices),
                "entity_count": len(self._entities),
                "state_count": len(self._states),
                "last_snapshot_at": self._last_snapshot_at,
            }

    async def areas(self) -> list[dict[str, Any]]:
        async with self._lock:
            return sorted(
                (deepcopy(area) for area in self._areas.values()),
                key=lambda item: str(item.get("name", item.get("area_id", ""))).lower(),
            )

    async def scope(self, area_ids: tuple[str, ...]) -> dict[str, Any]:
        requested = set(area_ids)
        async with self._lock:
            resolved_areas = [
                deepcopy(area)
                for area_id, area in self._areas.items()
                if area_id in requested
            ]
            scoped_entities: list[dict[str, Any]] = []
            for entity_id, registry in self._entities.items():
                area_id = self._entity_area_id(registry)
                if area_id not in requested:
                    continue
                state = deepcopy(self._states.get(entity_id, {}))
                scoped_entities.append(
                    {
                        "entity_id": entity_id,
                        "area_id": area_id,
                        "registry": deepcopy(registry),
                        "state": state,
                    }
                )
            scoped_entities.sort(key=lambda item: item["entity_id"])
            return {
                "requested_area_ids": sorted(requested),
                "resolved_area_ids": sorted(
                    str(area.get("area_id")) for area in resolved_areas
                ),
                "missing_area_ids": sorted(requested - self._areas.keys()),
                "areas": resolved_areas,
                "entities": scoped_entities,
            }

    def _entity_area_id(self, registry: dict[str, Any]) -> str | None:
        direct = registry.get("area_id")
        if isinstance(direct, str) and direct:
            return direct
        device_id = registry.get("device_id")
        device = self._devices.get(device_id, {}) if device_id else {}
        inherited = device.get("area_id")
        return inherited if isinstance(inherited, str) and inherited else None


def _index(value: Any, key: str) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in value:
        if not isinstance(item, dict):
            continue
        identity = item.get(key)
        if isinstance(identity, str) and identity:
            result[identity] = deepcopy(item)
    return result


def _as_dict(value: Any) -> dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}

