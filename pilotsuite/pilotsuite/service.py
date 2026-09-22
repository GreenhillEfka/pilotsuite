"""PilotSuite application service and deterministic processing loop."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from dataclasses import replace
from typing import Any

from pilotsuite import ARCHITECTURE_VERSION, READ_ONLY_RELEASE, VERSION
from pilotsuite.core.audit import AuditLog
from pilotsuite.core.plans import PlanStore
from pilotsuite.core.settings import Settings
from pilotsuite.core.selections import SelectionStore, InvalidSelection
from pilotsuite.core.zones import ZoneStore
from pilotsuite.core.context import ContextStore
from pilotsuite.domain.context import context_summary
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
        self.selections = SelectionStore(settings.data_dir)
        self.zones = ZoneStore(self.selections)
        self.context = ContextStore(self.selections)
        self._learning_sources = {}
        self._zone_results: list[dict[str, Any]] = []
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
        self._selection_summary: dict[str, Any] = {}
        self._neurons: list[Neuron] = []
        self._moods: list[Mood] = []
        self._suggestions: list[Suggestion] = []

    async def start(self) -> None:
        await self.selections.initialize()
        await self.zones.bootstrap(self.settings.golden_zone_area_ids)
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
                state = await self.status()
                LOGGER.info("Readiness ready=%s stream=%s snapshot_fresh=%s zone_resolved=%s capabilities=%s",
                            state["ready"], self._stream_connected,
                            state["home_assistant"]["snapshot_fresh"], state["golden_zone"]["resolved"],
                            {key: value["status"] for key, value in state["capabilities"].items()})
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
        missing_kinds = [kind for kind in ('humidity', 'temperature')
                         if not any(n.kind == kind and n.quality == 'good' and n.value is not None for n in self._neurons)]
        ready = bool(self._connected and self._stream_connected and fresh)
        zone_resolved = bool(self._zone_results and not self._scope.get('missing_area_ids')
                             and (self._scope.get('resolved_area_ids') or self._scope.get('entities')))
        capabilities = {}
        for name, kinds in (("temperature", {"temperature"}), ("humidity", {"humidity"}),
                            ("motion", {"motion"}), ("presence", {"occupancy", "presence"}),
                            ("light", {"light"}), ("illuminance", {"illuminance"})):
            members = [n for n in self._neurons if n.kind in kinds]
            valid = [n for n in members if n.quality == "good" and n.value is not None]
            state = "not_present" if not members else "unavailable" if not valid else "partial" if len(valid) != len(members) else "available"
            capabilities[name] = {"status": state, "entity_count": len(members), "valid_count": len(valid)}
        return {
            "ready": ready,
            "capabilities": capabilities,
            "selection": self._selection_summary,
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
                "requested_area_ids": self._scope.get('requested_area_ids', list(self.settings.golden_zone_area_ids)),
                "resolved_area_ids": self._scope.get("resolved_area_ids", []),
                "missing_area_ids": self._scope.get("missing_area_ids", []),
                "entity_count": len(self._scope.get("entities", [])),
                "missing_required_kinds": missing_kinds,
                "resolved": zone_resolved,
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

    async def selection_inventory(self, area_id: str) -> dict[str, Any]:
        await self.zones.bootstrap(self.settings.golden_zone_area_ids)
        definition = next((z for z in await self.zones.list() if z['zone_id'] == area_id), None)
        if definition is None:
            raise InvalidSelection("unknown Habitus zone")
        scope = await self.world.scope(tuple(definition['area_ids']), tuple(definition['extra_entity_ids']))
        stored = await self.selections.get(area_id)
        items = []
        for item in scope["entities"]:
            entity_id = item["entity_id"]
            registry = item["registry"]
            attributes = item["state"].get("attributes", {})
            attributes = attributes if isinstance(attributes, dict) else {}
            domain = entity_id.split(".", 1)[0]
            kind = attributes.get("device_class") or registry.get("device_class") or domain
            recommended = domain in {"sensor", "binary_sensor", "light", "climate", "cover", "fan", "media_player"} and not registry.get("entity_category")
            items.append({"entity_id": entity_id,
                          "name": registry.get("name") or attributes.get("friendly_name") or entity_id,
                          "state": item["state"].get("state"),
                          "suggested_role": kind, "recommended": recommended,
                          "decision": stored["decisions"].get(entity_id, "unreviewed")})
        present = {item["entity_id"] for item in items}
        return {"zone_id": area_id, "name": definition['name'], "enabled": definition['enabled'], "revision": stored["revision"], "items": items,
                "missing": [{"entity_id": key, "decision": stored['decisions'].get(key, 'unreviewed')} for key in sorted(set(stored['decisions']) | set(definition['extra_entity_ids'])) if key not in present],
                "resolved": not scope.get('missing_area_ids', []) and bool(scope["resolved_area_ids"] or items),
                "applied_to_inference": True}

    def moods(self) -> list[dict[str, Any]]:
        return [dict(item, zone_id=zone['zone_id'], zone_name=zone['name'])
                for zone in self._zone_results for item in zone['moods']]

    def suggestions(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self._suggestions]

    async def _derive(self) -> None:
        await self.zones.bootstrap(self.settings.golden_zone_area_ids)
        await self.context.maintain()
        definitions = [z for z in await self.zones.list() if z['enabled']]
        results, neurons, moods, suggestions = [], {}, [], []
        raw, resolved, missing, requested = {}, set(), set(), set()
        active_ids = []
        self._learning_sources = {}
        for zone in definitions:
            scope = await self.world.scope(tuple(zone['area_ids']), tuple(zone['extra_entity_ids']))
            selected = await self.selections.get(zone['zone_id'])
            requested.update(zone['area_ids'])
            resolved.update(scope.get('resolved_area_ids', []))
            missing.update(scope.get('missing_area_ids', []))
            raw.update({item['entity_id']: item for item in scope['entities']})
            entities = [item for item in scope['entities'] if selected['decisions'].get(item['entity_id']) == 'relevant' and item['entity_id'].split('.')[0] in {'sensor', 'binary_sensor', 'light', 'switch', 'climate', 'cover', 'fan', 'media_player'}]
            if selected['active']:
                active_ids.append(zone['zone_id'])
            zone_neurons = build_neurons({**scope, 'entities': entities})
            cfg = await self.context.get(zone['zone_id'])
            summary, climate_neurons = context_summary(zone_neurons, cfg['roles'])
            presence = [n.entity_id for n in zone_neurons if n.entity_id in cfg['roles'].get('presence', []) and n.kind in {'presence', 'occupancy', 'motion'} and n.quality == 'good']
            if cfg['learning'] and presence:
                self._learning_sources[zone['zone_id']] = presence
            zone_moods = calculate_moods(climate_neurons, connected=self._connected and self._stream_connected, profile=zone['profile'])
            total = sum(summary[k]['total_count'] for k in ('temperature', 'humidity'))
            valid = sum(summary[k]['valid_count'] for k in ('temperature', 'humidity'))
            ambiguous = any(summary[k]['status'] == 'ambiguous' for k in ('temperature', 'humidity'))
            uncertainty = (total-valid)/total if total and not ambiguous else None
            incomplete = any(summary[k]['status'] != 'available' for k in ('temperature', 'humidity'))
            zone_moods = [replace(m,
                score=uncertainty if m.name == 'uncertainty' else None if m.name == 'stable' and incomplete else m.score,
                evidence=({'role_groups': summary, 'aggregation': 'median of valid main sources', 'valid_sources': valid, 'total_sources': total},))
                for m in zone_moods]
            zone_suggestions = build_suggestions(zone_moods, (zone['zone_id'],), zone_name=zone['name'])
            neurons.update({n.entity_id: n for n in zone_neurons})
            moods.extend(zone_moods)
            suggestions.extend(zone_suggestions)
            results.append({'zone_id': zone['zone_id'], 'name': zone['name'], 'profile': zone['profile'],
                            'inventory_count': len(scope['entities']), 'evaluated_count': len(zone_neurons),
                            'counts': {decision: sum(selected['decisions'].get(i['entity_id'], 'unreviewed') == decision for i in scope['entities']) for decision in ('relevant', 'ignored', 'unreviewed')},
                            'summary': summary,
                            'moods': [m.to_dict() for m in zone_moods], 'neurons': [n.to_dict() for n in zone_neurons], 'missing_area_ids': scope.get('missing_area_ids', [])})
        self._scope = {'requested_area_ids': sorted(requested), 'resolved_area_ids': sorted(resolved),
                       'missing_area_ids': sorted(missing), 'entities': list(raw.values())}
        self._zone_results = results
        self._selection_summary = {
            "active_area_ids": active_ids,
            "inventory_count": len(self._scope["entities"]),
            "evaluated_count": len(neurons),
            "excluded_count": len(raw) - len(neurons),
        }
        self._neurons = list(neurons.values())
        self._moods = moods
        self._suggestions = suggestions

    async def _on_state_change(self, event_data: dict[str, Any]) -> None:
        async with self._projection_lock:
            await self.world.update_state(event_data)
            entity_id = event_data.get("entity_id")
            if any(item.entity_id == entity_id for item in self._neurons):
                await self._derive()
                old, new = event_data.get('old_state'), event_data.get('new_state')
                if not isinstance(old, dict) or not isinstance(new, dict) or old.get('state') != 'off' or new.get('state') != 'on':
                    return
                fresh = self._last_refresh_at and (datetime.now(UTC)-datetime.fromisoformat(self._last_refresh_at)).total_seconds() <= max(60, self.settings.refresh_interval_seconds*2)
                if not self._connected or not self._stream_connected or not fresh: return
                try:
                    stamp = datetime.fromisoformat(new['last_changed'])
                    if stamp.tzinfo is None: return
                    occurred = stamp.timestamp()
                except (KeyError, ValueError, TypeError):
                    return
                ctx = new.get('context') if isinstance(new.get('context'), dict) else {}
                origin = 'user_context' if ctx.get('user_id') else 'derived_context' if ctx.get('parent_id') else 'unknown'
                for zone_id, source in self._learning_sources.items():
                    if entity_id in source:
                        await self.context.record(zone_id, entity_id, occurred, origin)

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
