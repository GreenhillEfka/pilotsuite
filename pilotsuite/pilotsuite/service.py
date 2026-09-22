"""PilotSuite application service and deterministic processing loop."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from pilotsuite import ARCHITECTURE_VERSION, READ_ONLY_RELEASE, VERSION
from pilotsuite.core.audit import AuditLog
from pilotsuite.core.plans import PlanStore
from pilotsuite.core.settings import Settings
from pilotsuite.domain.models import Mood, Neuron, Suggestion
from pilotsuite.domain.moods import calculate_moods
from pilotsuite.domain.neurons import build_neurons
from pilotsuite.domain.synapses import RULESET_VERSION, build_suggestions
from pilotsuite.ha.client import HomeAssistantClient
from pilotsuite.ha.world import WorldModel


LOGGER = logging.getLogger(__name__)


class PilotSuiteService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.audit = AuditLog(settings.data_dir, settings.audit_retention)
        self.plans = PlanStore(settings.data_dir, self.audit)
        self.world = WorldModel()
        self.client = HomeAssistantClient(
            settings.ha_ws_url, settings.supervisor_token
        )
        self._stop = asyncio.Event()
        self._refresh_lock = asyncio.Lock()
        self._projection_lock = asyncio.Lock()
        self._tasks: list[asyncio.Task[Any]] = []
        self._connected = False
        self._stream_connected = False
        self._last_error: str | None = None
        self._last_refresh_at: str | None = None
        self._scope: dict[str, Any] = {}
        self._neurons: list[Neuron] = []
        self._moods: list[Mood] = []
        self._suggestions: list[Suggestion] = []

    async def start(self) -> None:
        await self.client.start()
        await self.audit.append(
            "runtime.start",
            details={
                "version": VERSION,
                "architecture": ARCHITECTURE_VERSION,
                "read_only": READ_ONLY_RELEASE,
            },
        )
        try:
            await self.refresh(reason="startup")
        except Exception as exc:
            self._last_error = str(exc)
            LOGGER.warning("Initial Home Assistant snapshot failed: %s", exc)
            await self.audit.append(
                "ha.snapshot",
                outcome="degraded",
                details={"reason": "startup", "error": type(exc).__name__},
            )
        self._tasks = [
            asyncio.create_task(self.client.listen(self._on_state_change, self._stop, self._on_connection)),
            asyncio.create_task(self._refresh_loop()),
        ]

    async def close(self) -> None:
        self._stop.set()
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        await self.client.close()
        await self.audit.append("runtime.stop")

    async def refresh(self, *, reason: str) -> dict[str, Any]:
        async with self._refresh_lock, self._projection_lock:
            try:
                snapshot = await self.client.snapshot()
                await self.world.replace(snapshot)
                self._connected = True
                self._last_error = None
                self._last_refresh_at = datetime.now(UTC).isoformat()
                await self._derive()
                summary = await self.world.summary()
                await self.audit.append(
                    "ha.snapshot",
                    details={"reason": reason, "summary": summary},
                )
                return summary
            except Exception as exc:
                self._connected = False
                self._last_error = str(exc)
                await self._derive()
                raise

    async def status(self) -> dict[str, Any]:
        fresh = self._last_refresh_at is not None and (
            datetime.now(UTC) - datetime.fromisoformat(self._last_refresh_at)
        ).total_seconds() <= max(60, self.settings.refresh_interval_seconds * 2)
        missing_kinds = next((
            list(m.evidence[0].get("missing_required_kinds", []))
            for m in self._moods if m.name == "uncertainty" and m.evidence
        ), ["humidity", "temperature"])
        ready = bool(self._connected and self._stream_connected and fresh
                     and self._scope.get("resolved_area_ids")
                     and not self._scope.get("missing_area_ids") and not missing_kinds)
        return {
            "ready": ready,
            "version": VERSION,
            "architecture": ARCHITECTURE_VERSION,
            "mode": "hard_read_only",
            "home_assistant": {
                "connected": self._connected,
                "event_stream_connected": self._stream_connected,
                "snapshot_fresh": fresh,
                "last_refresh_at": self._last_refresh_at,
                "last_error": self._last_error,
            },
            "golden_zone": {
                "requested_area_ids": list(self.settings.golden_zone_area_ids),
                "resolved_area_ids": self._scope.get("resolved_area_ids", []),
                "missing_area_ids": self._scope.get("missing_area_ids", []),
                "entity_count": len(self._scope.get("entities", [])),
                "missing_required_kinds": missing_kinds,
            },
            "habitus": {
                "neuron_count": len(self._neurons),
                "mood_count": len(self._moods),
                "suggestion_count": len(self._suggestions),
                "ruleset": RULESET_VERSION,
            },
        }

    async def golden_zone(self) -> dict[str, Any]:
        return {
            **self._scope,
            "neurons": [item.to_dict() for item in self._neurons],
        }

    def moods(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self._moods]

    def suggestions(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self._suggestions]

    async def _derive(self) -> None:
        self._scope = await self.world.scope(self.settings.golden_zone_area_ids)
        self._neurons = build_neurons(self._scope)
        self._moods = calculate_moods(self._neurons, connected=self._connected and self._stream_connected)
        self._suggestions = build_suggestions(
            self._moods, self.settings.golden_zone_area_ids
        )

    async def _on_state_change(self, event_data: dict[str, Any]) -> None:
        async with self._projection_lock:
            await self.world.update_state(event_data)
            entity_id = event_data.get("entity_id")
            if any(item.entity_id == entity_id for item in self._neurons):
                await self._derive()

    async def _on_connection(self, connected: bool) -> None:
        self._stream_connected = connected
        if connected:
            # Resynchronize after subscription, including every reconnect.
            await self.refresh(reason="stream_connected")
        else:
            async with self._projection_lock:
                await self._derive()

    async def _refresh_loop(self) -> None:
        while not self._stop.is_set():
            try:
                await asyncio.wait_for(
                    self._stop.wait(),
                    timeout=self.settings.refresh_interval_seconds,
                )
                continue
            except TimeoutError:
                pass
            try:
                await self.refresh(reason="interval")
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                LOGGER.warning("Home Assistant snapshot refresh failed: %s", exc)
                await self.audit.append(
                    "ha.snapshot",
                    outcome="degraded",
                    details={"reason": "interval", "error": type(exc).__name__},
                )
