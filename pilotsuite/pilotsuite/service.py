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
from pilotsuite.core.selections import SelectionStore, InvalidSelection, SelectionConflict
from pilotsuite.core.zones import ZoneStore
from pilotsuite.core.context import ContextStore
from pilotsuite.core.attribution import EventAttribution
from pilotsuite.domain.context import context_summary
from pilotsuite.domain.models import Mood, Neuron, Suggestion
from pilotsuite.domain.moods import calculate_moods
from pilotsuite.domain.neurons import build_neurons
from pilotsuite.domain.synapses import RULESET_VERSION, build_suggestions
from pilotsuite.ha.client import HomeAssistantClient, HomeAssistantError
from pilotsuite.ha.world import WorldModel


LOGGER = logging.getLogger(__name__)


def apply_role_overrides(neurons, roles):
    """Apply only explicit semantic role assignments; never infer helper meaning."""
    presence_helpers = set(roles.get('presence', []))
    return [
        replace(n, kind='presence') if n.entity_id in presence_helpers and n.kind == 'input_boolean' else n
        for n in neurons
    ]


class PilotSuiteService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.audit = AuditLog(settings.data_dir, settings.audit_retention)
        self.selections = SelectionStore(settings.data_dir)
        self.zones = ZoneStore(self.selections)
        self.context = ContextStore(self.selections)
        self.plans = PlanStore(settings.data_dir, self.audit, self.context)
        self.attribution = EventAttribution()
        self._learning_sources = {}
        self._history_lock = asyncio.Lock()
        self._automation_review_lock = asyncio.Lock()
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

    async def compare_automations(self, zone_id, draft_id, payload, *, inspection=False):
        from pilotsuite.domain.automation_review import reference_review
        expected = {'revision', 'zone_revision'} | ({'automation_id', 'previous_fingerprint'} if inspection else set())
        if (not isinstance(payload, dict) or set(payload) != expected
                or any(type(payload[k]) is not int for k in ('revision','zone_revision'))):
            raise InvalidSelection('Draft revision and zone_revision required')
        if inspection:
            import re
            if (not isinstance(payload['automation_id'],str) or len(payload['automation_id'])>255
                    or not re.fullmatch(r'automation\.[a-z0-9_]+',payload['automation_id'])
                    or (payload['previous_fingerprint'] is not None and
                        (not isinstance(payload['previous_fingerprint'],str) or not re.fullmatch(r'[0-9a-f]{64}',payload['previous_fingerprint'])))):
                raise InvalidSelection('Invalid selected automation or fingerprint')
        if self._automation_review_lock.locked():
            raise HomeAssistantError('An automation lookup is already running')
        async with self._automation_review_lock:
            async def basis():
                inventory = await self.selection_inventory(zone_id)
                drafts = await self.plans.drafts(zone_id, inventory)
                draft = next((d for d in drafts if d['id'] == draft_id), None)
                if not draft: raise InvalidSelection('Unknown draft in this zone')
                if draft['revision'] != payload['revision'] or inventory['revision'] != payload['zone_revision']:
                    raise SelectionConflict('Draft or zone changed; reload before comparison')
                if (draft['source_status'] != 'current' or draft['unavailable_targets']
                        or not draft['fields']['target_ids']):
                    raise InvalidSelection('Review current pattern and confirmed targets first')
                return draft
            async with self._projection_lock:
                draft = await basis()
            entities = sorted(set(draft['fields']['target_ids']) | set(draft['current_pattern']['sources']))
            # Network I/O never blocks the projection/learning lock.
            relations = await self.client.related_automations(entities)
            if inspection:
                if not any(payload['automation_id'] in ids for ids in relations.values()):
                    raise SelectionConflict('Selected automation no longer matches; repeat reference review')
                from pilotsuite.domain.automation_inspection import inspect_automation
                config = await self.client.automation_config(payload['automation_id'])
                detail = inspect_automation(config,draft,payload['automation_id'],payload['previous_fingerprint'])
                del config
            async with self._projection_lock:
                current = await basis()
                if current['current_pattern']['sources'] != draft['current_pattern']['sources']:
                    raise SelectionConflict('Pattern sources changed during comparison; retry')
                report = reference_review(current, payload['zone_revision'], relations)
                if inspection: report['inspection'] = detail
                from pilotsuite.core.review_compass import with_automation_review
                report['review_compass'] = with_automation_review(current['review_compass'], current, report)
                return report

    async def import_existing_automation(self, zone_id, automation_id, zone_revision):
        """Explicit transient read; shares review concurrency and no HA writes."""
        import re
        from pilotsuite.core.automation_import import import_automation
        if (not isinstance(automation_id, str) or len(automation_id) > 255
                or not re.fullmatch(r'automation\.[a-z0-9_]+', automation_id)
                or type(zone_revision) is not int or zone_revision < 0):
            raise InvalidSelection('Valid automation_id and zone_revision required')
        if self._automation_review_lock.locked():
            raise HomeAssistantError('An automation lookup is already running')
        async with self._automation_review_lock:
            async with self._projection_lock:
                inventory = await self.selection_inventory(zone_id)
                if inventory['revision'] != zone_revision:
                    raise SelectionConflict('Zone changed; reload before importing automation')
                inventory_ids = {i['entity_id'] for i in inventory['items']}
            config = await self.client.automation_config(automation_id)
            result = import_automation(automation_id, config, zone_id=zone_id,
                                       zone_revision=zone_revision, inventory_ids=inventory_ids)
            async with self._projection_lock:
                current = await self.selection_inventory(zone_id)
                if (current['revision'] != zone_revision or
                        {i['entity_id'] for i in current['items']} != inventory_ids):
                    raise SelectionConflict('Zone changed during automation import; retry')
                return result

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
            asyncio.create_task(self.client.listen(
                self._on_state_change,
                self._stop,
                self._on_connection,
                self._on_service_call,
            )),
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
            if domain == "binary_sensor" and kind == "light":
                kind = "daylight_binary"
            recommended = domain in {"sensor", "binary_sensor", "light", "climate", "cover", "fan", "media_player", "input_boolean", "input_select"} and not registry.get("entity_category")
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
        all_definitions = await self.zones.list()
        for zone in all_definitions:
            if not zone['enabled']:
                await self.context.checkpoint(zone['zone_id'], 'paused')
        definitions = [z for z in all_definitions if z['enabled']]
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
            entities = [item for item in scope['entities'] if selected['decisions'].get(item['entity_id']) == 'relevant' and item['entity_id'].split('.')[0] in {'sensor', 'binary_sensor', 'input_boolean', 'light', 'switch', 'climate', 'cover', 'fan', 'media_player'}]
            if selected['active']:
                active_ids.append(zone['zone_id'])
            zone_neurons = build_neurons({**scope, 'entities': entities})
            cfg = await self.context.get(zone['zone_id'])
            # A logical HA helper may be explicitly assigned as the zone presence
            # owner. It is never inferred as presence merely because it is boolean.
            zone_neurons = apply_role_overrides(zone_neurons, cfg['roles'])
            summary, climate_neurons = context_summary(zone_neurons, cfg['roles'])
            presence = [n.entity_id for n in zone_neurons if n.entity_id in cfg['roles'].get('presence', []) and n.kind in {'presence', 'occupancy', 'motion'} and n.quality == 'good']
            if cfg['learning'] and presence:
                self._learning_sources[zone['zone_id']] = presence
            transport_ready = (await self.status())['ready']
            check_state = 'disconnected' if not transport_ready else 'no_source' if not presence else 'partial_source' if len(presence) < len(cfg['roles'].get('presence', [])) else 'ready'
            await self.context.checkpoint(zone['zone_id'], check_state)
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
        if not self._learning_sources:
            self.attribution.clear()

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
                origin = self.attribution.classify_state(new)
                for zone_id, source in self._learning_sources.items():
                    if entity_id in source:
                        from pilotsuite.core.learning_views import activation_context
                        cfg = await self.context.get(zone_id)
                        result = next((z for z in self._zone_results if z['zone_id'] == zone_id), {})
                        context = activation_context(result.get('summary', {}), cfg['roles']) if cfg['context_learning'] else None
                        if context is not None:
                            context['captured_at'] = datetime.now(UTC).isoformat()
                        await self.context.record(zone_id, entity_id, occurred, origin, context=context)

    async def _on_service_call(self, event: dict[str, Any]) -> None:
        # Context correlation is useful only for zones with explicit active
        # learning consent. No service data or identifiers are persisted.
        if not self._learning_sources:
            self.attribution.clear()
            return
        self.attribution.observe_service_event(event)

    async def _on_connection(self, connected: bool) -> None:
        self._stream_connected = connected
        if connected:
            # Resynchronize after subscription, including every reconnect.
            await self.refresh(reason="stream_connected")
        else:
            self.attribution.clear()
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

    async def history_view(self, zone_id, payload, *, import_learning=False):
        import time
        from pilotsuite.core.history import interval, normalize, activations, trend_view, retrospective, KINDS
        from pilotsuite.core.context import ROLE_KINDS
        from pilotsuite.core.selections import SelectionConflict
        from pilotsuite.ha.client import HomeAssistantError
        expected = {'start', 'end', 'mode', 'revision'} | ({'consent'} if import_learning else set())
        if not isinstance(payload, dict) or set(payload) != expected:
            raise InvalidSelection('History requires start, end, mode and revision')
        if type(payload['revision']) is not int or payload['mode'] not in ('states','statistics'):
            raise InvalidSelection('Invalid history mode or revision')
        if import_learning and (payload['consent'] is not True or payload['mode'] != 'states'):
            raise InvalidSelection('Explicit historical learning consent and raw states required')
        now = time.time()
        start, end = interval(payload['start'], payload['end'], now)
        if import_learning and (start < now-14*86400-60 or end > now or end-start > 14*86400):
            raise InvalidSelection('Learning import supports at most the last 14 days')
        if self._history_lock.locked():
            raise InvalidSelection('A history request is running; retry after completion')
        async with self._history_lock:
            async with self._projection_lock:
                inventory = await self.selection_inventory(zone_id)
                cfg = await self.context.get(zone_id)
                if inventory['revision'] != payload['revision']:
                    raise SelectionConflict('Zone changed; reload before requesting history')
                candidates = {i['entity_id']:i for i in inventory['items'] if i['decision']=='relevant'}
                roles = {kind:[e for e in cfg['roles'].get(kind,[]) if e in candidates and candidates[e]['suggested_role'] in ROLE_KINDS[kind]] for kind in KINDS}
                if import_learning:
                    if not inventory['enabled'] or not cfg['learning'] or not roles['presence'] or roles['presence'] != cfg['roles'].get('presence'):
                        raise InvalidSelection('Active zone, learning consent and complete relevant presence group required')
                    # Activity-only import. Never infer historical light-context consent.
                    roles = {'presence':roles['presence']}
                if payload['mode']=='statistics':
                    roles = {k:v for k,v in roles.items() if k in ('temperature','humidity','illuminance')}
                ids = sorted({e for group in roles.values() for e in group})
                if not ids:
                    raise InvalidSelection('Save relevant main sensor groups for the requested history type first')
            try:
                raw = await self.client.history(ids,start,end,statistics=payload['mode']=='statistics')
            except (HomeAssistantError, TimeoutError) as exc:
                raise InvalidSelection('HA history unavailable or too large. Try a shorter interval; no partial import was saved.') from exc
            series = normalize(raw['records'],roles,start,end,statistics=payload['mode']=='statistics',metadata=raw['metadata'])
            events = activations(series,roles,start,end) if payload['mode']=='states' else []
            async with self._projection_lock:
                if (await self.selections.get(zone_id))['revision'] != payload['revision']:
                    raise SelectionConflict('Zone changed while history loaded; discard and reload')
                if import_learning:
                    receipt = await self.context.import_history(zone_id,payload['revision'],roles,events,start,end)
                    return {'receipt':receipt,'revision':payload['revision']+1}
                return {'zone_id':zone_id, 'revision':payload['revision'], 'start':start,'end':end,
                        'timezone':cfg['detector'].get('timezone','UTC'),
                        'trends':trend_view(series,roles,start,end,statistics=payload['mode']=='statistics'),
                        'activity':retrospective(events,cfg['detector'],start,end) if payload['mode']=='states' and cfg['learning'] else None,
                        'raw_activation_count':len(events) if cfg['learning'] else None,
                        'selection_basis':'current_saved_main_groups',
                        'excluded_sources':sorted({e for group in cfg['roles'].values() for e in group}-set(ids))}
