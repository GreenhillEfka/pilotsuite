"""Explicit review-note routes. HA configuration is only read, never written."""
import time
from pathlib import Path

from aiohttp import web

from pilotsuite.core.review_notes import validate_note_request
from pilotsuite.core.review_compass import with_saved_notes
from pilotsuite.core.selections import InvalidSelection, SelectionConflict
from pilotsuite.ha.client import HomeAssistantError


def register_review_notes(app, service_key):
    async def notes(request):
        service = request.app[service_key]
        zone, draft = request.match_info['zone_id'], request.match_info['draft_id']
        payload = None
        if request.method not in ('GET', 'HEAD'):
            try:
                payload = await request.json()
            except ValueError as exc:
                raise InvalidSelection('Invalid JSON') from exc
            payload = validate_note_request(payload, deleting=request.method == 'DELETE')
        async with service._projection_lock:
            inventory = await service.selection_inventory(zone)
            if request.method in ('GET', 'HEAD'):
                result = await service.plans.review_notes(zone, draft, inventory)
                return web.json_response(result, headers={'Cache-Control': 'no-store'})
            if request.method == 'DELETE':
                result = await service.plans.delete_review_note(zone, draft, payload, inventory)
                return web.json_response(result, headers={'Cache-Control': 'no-store'})
            # Avoid network I/O for known revision conflicts; repeat atomically below.
            await service.plans.review_notes(zone, draft, inventory, payload)
        inspected_at = time.monotonic()
        try:
            report = await service.compare_automations(zone, draft, {
                'revision': payload['revision'], 'zone_revision': payload['zone_revision'],
                'automation_id': payload['automation_id'],
                'previous_fingerprint': payload['config_fingerprint'],
            }, inspection=True)
        except HomeAssistantError:
            return web.json_response({'error': 'review_inspection_unavailable',
                'message': 'Erneute Detailprüfung nicht verfügbar. Notiz nicht gespeichert; Eingaben bleiben erhalten.'},
                status=503, headers={'Cache-Control': 'no-store'})
        if report['inspection']['config_fingerprint'] != payload['config_fingerprint']:
            raise SelectionConflict('Automation changed; inspect the changed configuration before saving your note')
        async with service._projection_lock:
            inventory = await service.selection_inventory(zone)
            result = await service.plans.save_review_note(zone, draft, payload, inventory, report, inspected_at)
        report['review_compass'] = with_saved_notes(report.get('review_compass'), result, report)
        return web.json_response({'review_notes': result, 'automation_review': report},
                                 headers={'Cache-Control': 'no-store'})

    async def javascript(_):
        return web.FileResponse(Path(__file__).with_name('web') / 'review_notes.js',
                                headers={'Content-Type': 'text/javascript', 'Cache-Control': 'no-cache'})

    async def stylesheet(_):
        return web.FileResponse(Path(__file__).with_name('web') / 'review_notes.css',
                                headers={'Content-Type': 'text/css', 'Cache-Control': 'no-cache'})

    async def compass_javascript(_):
        return web.FileResponse(Path(__file__).with_name('web') / 'review_compass.js',
                                headers={'Content-Type': 'text/javascript', 'Cache-Control': 'no-cache'})

    async def compass_stylesheet(_):
        return web.FileResponse(Path(__file__).with_name('web') / 'review_compass.css',
                                headers={'Content-Type': 'text/css', 'Cache-Control': 'no-cache'})

    app.router.add_get('/assets/review_compass.js', compass_javascript)
    app.router.add_get('/assets/review_compass.css', compass_stylesheet)
    route = '/api/v1/zones/{zone_id}/drafts/{draft_id}/review-notes'
    app.router.add_get(route, notes)
    app.router.add_put(route, notes)
    app.router.add_delete(route, notes)
    app.router.add_get('/assets/review_notes.js', javascript)
    app.router.add_get('/assets/review_notes.css', stylesheet)
