"""Ingress-only maintenance: local savepoints and explicit existing-helper reads."""
from aiohttp import web
from pilotsuite.core.selections import InvalidSelection
from pilotsuite.ha.client import HomeAssistantError


def register_maintenance(app, service_key, web_dir):
    def response(data, status=200):
        return web.json_response(data, status=status, headers={'Cache-Control': 'no-store'})

    async def body(request, keys):
        if request.content_type != 'application/json':
            raise InvalidSelection('JSON-Anfrage erforderlich')
        try:
            value = await request.json()
        except ValueError as exc:
            raise InvalidSelection('Ungültiges JSON') from exc
        if not isinstance(value, dict) or set(value) != set(keys):
            raise InvalidSelection('Ungültige Anfragefelder')
        return value

    async def page(_):
        return web.FileResponse(web_dir / 'maintenance.html', headers={'Cache-Control': 'no-store'})

    async def js(_):
        return web.FileResponse(web_dir / 'maintenance.js', headers={'Content-Type': 'text/javascript'})

    async def css(_):
        return web.FileResponse(web_dir / 'maintenance.css', headers={'Content-Type': 'text/css'})

    async def status(request):
        return response(await request.app[service_key].maintenance())

    async def save(request):
        payload = await body(request, {'label'})
        service = request.app[service_key]
        async with service._projection_lock:
            result = await service.plans.create_savepoint(payload['label'])
        return response(result, 201)

    async def preview(request):
        await body(request, set())
        service = request.app[service_key]
        async with service._projection_lock:
            result = await service.plans.preview_restore(request.match_info['point_id'])
        return response(result)

    async def restore(request):
        payload = await body(request, {'sha256', 'basis', 'confirm_paused_restore'})
        service = request.app[service_key]
        async with service._projection_lock:
            result = await service.plans.restore_savepoint(request.match_info['point_id'], payload)
            # Rebuild only from the current world, never perform HA I/O or replay an old event.
            await service._derive()
        return response(result)

    async def helpers(request):
        payload = await body(request, {'zone_revision'})
        try:
            result = await request.app[service_key].inspect_existing_helpers(
                request.match_info['zone_id'], payload['zone_revision'])
        except HomeAssistantError:
            return response({'error': 'helper_inspection_unavailable',
                             'message': 'Helferkonfiguration nicht lesbar. Kein Helfer wurde verändert.'}, 503)
        return response(result)

    app.router.add_get('/maintenance', page)
    app.router.add_get('/assets/maintenance.js', js)
    app.router.add_get('/assets/maintenance.css', css)
    app.router.add_get('/api/v1/maintenance', status)
    app.router.add_post('/api/v1/maintenance/savepoints', save)
    app.router.add_post('/api/v1/maintenance/savepoints/{point_id}/preview', preview)
    app.router.add_post('/api/v1/maintenance/savepoints/{point_id}/restore', restore)
    app.router.add_post('/api/v1/zones/{zone_id}/helpers/inspect', helpers)
