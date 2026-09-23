"""PilotSuite Ingress web application."""

from __future__ import annotations

import logging
import uuid
import re
from pathlib import Path
from typing import Any

from aiohttp import web

from pilotsuite import ARCHITECTURE_VERSION, READ_ONLY_RELEASE, VERSION
from pilotsuite.core.logging import configure_logging
from pilotsuite.core.plans import InvalidPlan, ReadOnlyRelease
from pilotsuite.core.settings import Settings
from pilotsuite.core.selections import InvalidSelection, SelectionConflict
from pilotsuite.service import PilotSuiteService


LOGGER = logging.getLogger(__name__)
WEB_DIR = Path(__file__).with_name("web")
SERVICE_KEY: web.AppKey[PilotSuiteService] = web.AppKey(
    "service", PilotSuiteService
)


@web.middleware
async def ingress_guard(request: web.Request, handler: Any) -> web.StreamResponse:
    settings = request.app[SERVICE_KEY].settings
    # Trust the TCP peer, never a client-supplied forwarding header.
    local_probe = request.remote in {"127.0.0.1", "::1"} and request.path == "/health"
    if not local_probe and request.remote not in settings.ingress_allowed_peers:
        raise web.HTTPForbidden(text="Ingress access required")
    normalized = re.sub(r"/{2,}", "/", request.path)
    if normalized != request.path:
        # Resolve internally: redirects can lose the Supervisor's external prefix.
        request = request.clone(rel_url=request.rel_url.with_path(normalized, keep_query=True))
        match = await request.app.router.resolve(request)
        match.add_app(request.app)
        match.freeze()
        request._match_info = match
        return await match.handler(request)
    return await handler(request)


@web.middleware
async def request_context(
    request: web.Request, handler: Any
) -> web.StreamResponse:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))[:128]
    try:
        response = await handler(request)
    except web.HTTPException:
        raise
    except InvalidPlan as exc:
        response = web.json_response(
            {"error": "invalid_plan", "message": str(exc), "request_id": request_id},
            status=400,
        )
    except (InvalidSelection, SelectionConflict) as exc:
        response = web.json_response(
            {"error": "selection_conflict" if isinstance(exc, SelectionConflict) else "invalid_selection",
             "message": str(exc), "request_id": request_id},
            status=409 if isinstance(exc, SelectionConflict) else 400,
        )
    except ReadOnlyRelease as exc:
        response = web.json_response(
            {
                "error": "read_only_release",
                "message": str(exc),
                "request_id": request_id,
            },
            status=409,
        )
    except Exception:
        LOGGER.exception("Unhandled request failure request_id=%s", request_id)
        response = web.json_response(
            {
                "error": "internal_error",
                "message": "The request could not be completed",
                "request_id": request_id,
            },
            status=500,
        )
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'; "
        "img-src 'self' data:; connect-src 'self'"
    )
    return response


def create_app(settings: Settings | None = None) -> web.Application:
    resolved = settings or Settings.load()
    service = PilotSuiteService(resolved)
    app = web.Application(middlewares=[request_context, ingress_guard], client_max_size=128 * 1024)
    app[SERVICE_KEY] = service
    app.on_startup.append(_startup)
    app.on_cleanup.append(_cleanup)
    app.router.add_get("/", _index)
    app.router.add_get("/assets/app.js", _javascript)
    app.router.add_get("/assets/selections.js", _selection_javascript)
    app.router.add_get("/assets/styles.css", _stylesheet)
    app.router.add_get("/health", _health)
    app.router.add_get("/health/ready", _ready)
    app.router.add_get("/version", _version)
    app.router.add_get("/api/v1/status", _status)
    app.router.add_get("/api/v1/architecture", _architecture)
    app.router.add_get("/api/v1/areas", _areas)
    app.router.add_get('/api/v1/zones', _zones)
    app.router.add_get('/api/v1/zones/export', _zone_export)
    app.router.add_post('/api/v1/zones', _save_zone)
    app.router.add_patch('/api/v1/zones/{zone_id}', _save_zone)
    app.router.add_get('/api/v1/entity-catalog', _entity_catalog)
    app.router.add_get('/api/v1/zones/{zone_id}/context', _context_get)
    app.router.add_patch('/api/v1/zones/{zone_id}/context', _context_patch)
    app.router.add_get('/api/v1/zones/{zone_id}/context/export', _context_export)
    app.router.add_post('/api/v1/zones/{zone_id}/feedback', _pattern_feedback)
    app.router.add_get("/api/v1/world", _world)
    app.router.add_get("/api/v1/golden-zone", _golden_zone)
    app.router.add_get("/api/v1/selections/{area_id}", _selection_inventory)
    app.router.add_patch("/api/v1/selections/{area_id}", _selection_patch)
    app.router.add_get("/api/v1/moods", _moods)
    app.router.add_get("/api/v1/suggestions", _suggestions)
    app.router.add_get("/api/v1/audit", _audit)
    app.router.add_post("/api/v1/refresh", _refresh)
    app.router.add_post("/api/v1/plans", _create_plan)
    app.router.add_post("/api/v1/transactions/{plan_id}/apply", _apply_plan)
    return app


async def _startup(app: web.Application) -> None:
    await app[SERVICE_KEY].start()


async def _selection_inventory(request: web.Request) -> web.Response:
    return web.json_response(await request.app[SERVICE_KEY].selection_inventory(request.match_info["area_id"]))


async def _zones(request: web.Request) -> web.Response:
    service = request.app[SERVICE_KEY]
    return web.json_response({'items': await service.zones.list(), 'results': service._zone_results})


async def _entity_catalog(request: web.Request) -> web.Response:
    return web.json_response({'items': await request.app[SERVICE_KEY].world.catalog()})


async def _zone_export(request: web.Request) -> web.Response:
    service = request.app[SERVICE_KEY]
    async with service._projection_lock:
        items = [dict(zone, selection=await service.selections.get(zone['zone_id'])) for zone in await service.zones.list()]
        return web.json_response({'format': 'pilotsuite-habitus-zones', 'schema': 1, 'items': items},
                                 headers={'Content-Disposition': 'attachment; filename="pilotsuite-zones.json"'})


async def _save_zone(request: web.Request) -> web.Response:
    service = request.app[SERVICE_KEY]
    try:
        payload = await request.json()
    except ValueError as exc:
        raise InvalidSelection('invalid JSON') from exc
    zone_id = request.match_info.get('zone_id')
    expected = {'definition', 'revision'} if zone_id else {'definition'}
    if not isinstance(payload, dict) or set(payload) != expected:
        raise InvalidSelection('invalid zone request fields')
    definition = service.zones.validate(payload['definition'])
    async with service._projection_lock:
        previous = next((z for z in await service.zones.list() if z['zone_id'] == zone_id), {})
        areas = {a['area_id'] for a in await service.world.areas()} | set(previous.get('area_ids', []))
        entities = {e['entity_id'] for e in await service.world.catalog() if not e['disabled']} | set(previous.get('extra_entity_ids', []))
        if not set(definition['area_ids']) <= areas or not set(definition['extra_entity_ids']) <= entities:
            raise InvalidSelection('unknown area or unavailable extra entity; reload the inventory')
        saved = await service.zones.save(definition, zone_id, payload.get('revision'))
        await service._derive()
        return web.json_response(saved, status=200 if zone_id else 201)


async def _selection_patch(request: web.Request) -> web.Response:
    service = request.app[SERVICE_KEY]
    area_id = request.match_info["area_id"]
    try:
        payload = await request.json()
    except ValueError as exc:
        raise InvalidSelection("body must be valid JSON") from exc
    if not isinstance(payload, dict) or set(payload) not in ({"revision", "changes"}, {"revision", "changes", "active"}):
        raise InvalidSelection("body requires revision, changes and optionally active")
    if "active" in payload and type(payload["active"]) is not bool:
        raise InvalidSelection("active must be a boolean")
    async with service._projection_lock:
        inventory = await service.selection_inventory(area_id)
        known = {item["entity_id"] for item in inventory["items"] + inventory["missing"]}
        changes = payload["changes"]
        if not isinstance(changes, dict) or not set(changes).issubset(known):
            raise InvalidSelection("all changed entities must belong to this zone's inventory")
        await service.selections.patch(area_id, payload["revision"], changes, payload.get("active"))
        await service._derive()
        return web.json_response(await service.selection_inventory(area_id))


async def _cleanup(app: web.Application) -> None:
    await app[SERVICE_KEY].close()


async def _index(_: web.Request) -> web.FileResponse:
    return web.FileResponse(WEB_DIR / "index.html")


async def _javascript(_: web.Request) -> web.FileResponse:
    return web.FileResponse(WEB_DIR / "app.js", headers={"Content-Type": "text/javascript"})


async def _stylesheet(_: web.Request) -> web.FileResponse:
    return web.FileResponse(WEB_DIR / "styles.css", headers={"Content-Type": "text/css"})


async def _selection_javascript(_: web.Request) -> web.FileResponse:
    return web.FileResponse(WEB_DIR / "selections.js", headers={"Content-Type": "text/javascript"})


async def _health(_: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "version": VERSION})


async def _ready(request: web.Request) -> web.Response:
    status = await request.app[SERVICE_KEY].status()
    ready = bool(status["ready"])
    return web.json_response(
        {"status": "ready" if ready else "degraded", **status},
        status=200 if ready else 503,
    )


async def _version(_: web.Request) -> web.Response:
    return web.json_response(
        {"version": VERSION, "architecture": ARCHITECTURE_VERSION}
    )


async def _status(request: web.Request) -> web.Response:
    return web.json_response(await request.app[SERVICE_KEY].status())


async def _architecture(_: web.Request) -> web.Response:
    return web.json_response(
        {
            "architecture": ARCHITECTURE_VERSION,
            "home_assistant_source_of_truth": True,
            "llm_in_critical_path": False,
            "read_only_release": READ_ONLY_RELEASE,
            "mutation_path": ["plan", "backup", "apply", "verify", "rollback"],
            "golden_zone": "erdkeller",
        }
    )


async def _areas(request: web.Request) -> web.Response:
    return web.json_response({"items": await request.app[SERVICE_KEY].world.areas()})


async def _world(request: web.Request) -> web.Response:
    return web.json_response(await request.app[SERVICE_KEY].world.summary())


async def _golden_zone(request: web.Request) -> web.Response:
    return web.json_response(await request.app[SERVICE_KEY].golden_zone())


async def _moods(request: web.Request) -> web.Response:
    return web.json_response({"items": request.app[SERVICE_KEY].moods()})


async def _suggestions(request: web.Request) -> web.Response:
    return web.json_response({"items": request.app[SERVICE_KEY].suggestions()})


async def _audit(request: web.Request) -> web.Response:
    try:
        limit = int(request.query.get("limit", "100"))
    except ValueError:
        limit = 100
    return web.json_response(
        {"items": await request.app[SERVICE_KEY].audit.tail(limit)}
    )


async def _refresh(request: web.Request) -> web.Response:
    summary = await request.app[SERVICE_KEY].refresh(reason="api")
    return web.json_response({"status": "refreshed", "world": summary})


async def _create_plan(request: web.Request) -> web.Response:
    payload = await request.json()
    if not isinstance(payload, dict):
        raise InvalidPlan("request body must be an object")
    plan = await request.app[SERVICE_KEY].plans.create(payload)
    return web.json_response(plan, status=201)


async def _apply_plan(request: web.Request) -> web.Response:
    await request.app[SERVICE_KEY].plans.apply(request.match_info["plan_id"])
    raise AssertionError("read-only transaction boundary returned unexpectedly")


def main() -> None:
    settings = Settings.load()
    configure_logging(settings.log_level)
    LOGGER.info(
        "Starting PilotSuite version=%s architecture=%s mode=hard_read_only",
        VERSION,
        ARCHITECTURE_VERSION,
    )
    web.run_app(create_app(settings), host=settings.host, port=settings.port)


async def _context_payload(service, zone_id, export=False):
    inventory = await service.selection_inventory(zone_id)
    report = await service.context.report(zone_id)
    if not export:
        report.pop('evidence', None)
        report.pop('context_evidence', None)
        report.pop('coverage_samples', None)
    report['revision'] = inventory['revision']
    report['enabled'] = inventory['enabled']
    report['eligible'] = zone_id in service._learning_sources
    report['collection_state'] = (
        'off' if not report['config']['learning'] else
        'paused' if not report['enabled'] else
        'disconnected' if not (await service.status())['ready'] else
        'no_source' if not report['eligible'] else 'collecting')
    report['collecting_sources'] = service._learning_sources.get(zone_id, [])
    report['candidates'] = [i for i in inventory['items'] if i['decision'] == 'relevant']
    # Surface legacy automatic defaults so opening/saving cannot silently clear them.
    roles = dict(report['config']['roles'])
    for kind in ('temperature', 'humidity', 'illuminance', 'light'):
        ids = [i['entity_id'] for i in report['candidates'] if i['suggested_role'] == kind
               and i['entity_id'] not in roles.get('reference_temperature', [])]
        if kind not in roles:
            roles[kind] = ids if kind == 'light' or len(ids) == 1 else []
    report['effective_roles'] = roles
    report['modules'] = [
        {'id': 'references-v1', 'name': 'Zonenreferenzen', 'kind': 'deterministic',
         'state': 'active' if report['enabled'] else 'paused', 'configurable': 'Sensorrollen'},
        {'id': 'activity-v1', 'name': 'Wiederkehrende Aktivierungen', 'kind': 'learning',
         'state': report['collection_state'], 'configurable': 'Lernfreigabe und Mindestbelege'},
        {'id': 'activation-context-v1', 'name': 'Lichtkontext bei Aktivierungen', 'kind': 'learning',
         'state': report['collection_state'] if report['config'].get('context_learning') else 'off',
         'configurable': 'Zusätzliche Kontextfreigabe; Licht- und Helligkeitsrollen'},
        {'id': 'action-execution', 'name': 'Freigegebene HA-Aktionen', 'kind': 'planned', 'state': 'blocked'},
    ]
    return report


async def _context_get(request):
    service = request.app[SERVICE_KEY]
    async with service._projection_lock:
        return web.json_response(await _context_payload(service, request.match_info['zone_id']))


async def _context_export(request):
    service = request.app[SERVICE_KEY]
    async with service._projection_lock:
        return web.json_response(await _context_payload(service, request.match_info['zone_id'], True),
            headers={'Content-Disposition': 'attachment; filename="pilotsuite-learning.json"'})


async def _context_patch(request):
    from pilotsuite.core.context import ROLE_KINDS
    service = request.app[SERVICE_KEY]
    zone_id = request.match_info['zone_id']
    try: payload = await request.json()
    except ValueError as exc: raise InvalidSelection('invalid JSON') from exc
    if (not isinstance(payload, dict) or not {'revision', 'roles', 'learning'} <= set(payload)
            or set(payload) - {'revision', 'roles', 'learning', 'reset', 'detector', 'context_learning'}):
        raise InvalidSelection('revision, roles and learning required; unknown fields rejected')
    if 'context_learning' in payload and type(payload['context_learning']) is not bool:
        raise InvalidSelection('context_learning must be boolean')
    if 'detector' in payload:
        from pilotsuite.core.context import validate_detector
        validate_detector(payload['detector'])
    if not isinstance(payload['roles'], dict): raise InvalidSelection('roles must be a mapping')
    async with service._projection_lock:
        inventory = await service.selection_inventory(zone_id)
        previous = await service.context.get(zone_id)
        candidates = {i['entity_id']: i for i in inventory['items'] if i['decision'] == 'relevant'}
        for role, entities in payload['roles'].items():
            if role not in ROLE_KINDS or not isinstance(entities, list) or len(entities)>20 or any(not isinstance(e, str) for e in entities):
                raise InvalidSelection('Role groups require at most 20 entity IDs')
            for entity in entities:
                if entity in previous['roles'].get(role, []) and not payload['learning']: continue
                if entity not in candidates or candidates[entity]['suggested_role'] not in ROLE_KINDS[role]:
                    raise InvalidSelection('Role source must be a confirmed relevant entity of the matching type')
        await service.context.configure(zone_id, payload['revision'], payload['roles'], payload['learning'], reset=payload.get('reset', False), detector=payload.get('detector'), context_learning=payload.get('context_learning'))
        await service._derive()
        return web.json_response(await _context_payload(service, zone_id))


async def _pattern_feedback(request):
    service = request.app[SERVICE_KEY]
    try: payload = await request.json()
    except ValueError as exc: raise InvalidSelection('invalid JSON') from exc
    if not isinstance(payload, dict) or set(payload) != {'pattern_id', 'decision'} or not isinstance(payload['pattern_id'], str) or not isinstance(payload['decision'], str):
        raise InvalidSelection('pattern_id and decision required')
    async with service._projection_lock:
        await service.selection_inventory(request.match_info['zone_id'])
        await service.context.feedback(request.match_info['zone_id'], payload['pattern_id'], payload['decision'])
        return web.json_response(await _context_payload(service, request.match_info['zone_id']))


if __name__ == "__main__":
    main()
