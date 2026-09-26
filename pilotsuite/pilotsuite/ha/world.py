"""Bounded in-memory projection of the Home Assistant source of truth."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any


from .organization import OrganizationWorldMixin


class WorldModel(OrganizationWorldMixin):
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

    async def update_state(self, event_data: dict[str, Any]) -> bool:
        """Return acceptance so consumers cannot learn from a rejected stream frame.

        Equal timestamps are not new observations. Undated legacy/test snapshots can
        still be projected, but cannot replace a newer, timestamped state.
        """
        if not isinstance(event_data, dict) or "new_state" not in event_data:
            return False
        entity_id = event_data.get("entity_id")
        new_state = event_data["new_state"]
        if not isinstance(entity_id, str) or not entity_id:
            return False
        async with self._lock:
            current = self._states.get(entity_id, {})
            current_at = _state_timestamp(current)
            if new_state is None:
                old = event_data.get("old_state")
                old_at = _state_timestamp(old)
                if isinstance(old, dict) and old.get("entity_id", entity_id) != entity_id:
                    return False
                if current_at is not None and (old_at is None or old_at < current_at):
                    return False
                return self._states.pop(entity_id, None) is not None
            if (not isinstance(new_state, dict)
                    or new_state.get("entity_id", entity_id) != entity_id
                    or not isinstance(new_state.get("state"), str)):
                return False
            new_at = _state_timestamp(new_state)
            if current_at is not None and (new_at is None or new_at <= current_at):
                return False
            if new_state == current:
                return False
            self._states[entity_id] = deepcopy(new_state)
            return True

    async def context_at_or_before(self, entity_ids: list[str], at: datetime) -> bool:
        """Check projection timestamps, not physical simultaneity or sensor accuracy.

        Missing times and a source updated after the event cannot establish event-time
        context. Called under the service projection lock; makes no HA/history reads.
        """
        if not entity_ids or at.tzinfo is None:
            return False
        async with self._lock:
            for entity_id in entity_ids:
                updated = _state_timestamp(self._states.get(entity_id))
                if updated is None or updated > at:
                    return False
        return True

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

    async def catalog(self) -> list[dict[str, Any]]:
        async with self._lock:
            return [{'entity_id': key, 'area_id': self._entity_area_id(value),
                     'name': value.get('name') or _as_dict(self._states.get(key, {}).get('attributes')).get('friendly_name') or key,
                     'disabled': value.get('disabled_by') is not None}
                    for key, value in sorted(self._entities.items())]

    async def maintenance_update(self, *, fresh):
        from pilotsuite.core.maintenance import update_view
        async with self._lock:
            return update_view(list(self._entities.values()), self._states, fresh=fresh)

    async def helper_registry(self):
        """Only registry identity fields; no states, options, tokens or config blobs."""
        async with self._lock:
            return [{"entity_id": eid, "area_id": self._entity_area_id(row),
                     "platform": row.get("platform"), "unique_id": row.get("unique_id"),
                     "disabled": row.get("disabled_by") is not None}
                    for eid, row in sorted(self._entities.items())]

    async def scope(self, area_ids: tuple[str, ...], extra_entity_ids: tuple[str, ...] = ()) -> dict[str, Any]:
        requested = set(area_ids)
        async with self._lock:
            resolved_areas = [
                deepcopy(area)
                for area_id, area in self._areas.items()
                if area_id in requested
            ]
            scoped_entities: list[dict[str, Any]] = []
            for entity_id, registry in self._entities.items():
                if registry.get("disabled_by") is not None:
                    continue
                area_id = self._entity_area_id(registry)
                if area_id not in requested and entity_id not in extra_entity_ids:
                    continue
                state = deepcopy(self._states.get(entity_id, {}))
                scoped_entities.append(
                    {
                        "entity_id": entity_id,
                        "area_id": area_id or "",
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


def _state_timestamp(state: Any) -> datetime | None:
    if not isinstance(state, dict):
        return None
    try:
        stamp = datetime.fromisoformat(state["last_updated"])
        return stamp if stamp.tzinfo is not None else None
    except (KeyError, TypeError, ValueError):
        return None
