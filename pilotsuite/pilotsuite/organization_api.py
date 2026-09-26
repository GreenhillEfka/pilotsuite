"""Ingress-protected organization endpoints; explicit operations, no generic proxy."""
from aiohttp import web
from .core.selections import InvalidSelection
from .ha.client import HomeAssistantError


def register_organization(app,service_key,web_dir):
    async def endpoint(request):
        service=request.app[service_key];zid=request.match_info['zone_id']
        if request.method in ('GET','HEAD'):
            if 'plan_id' in request.match_info:
                result=await service.plans.organization_plan_get(zid,request.match_info['plan_id'])
            else: result=await service.organization_overview(zid)
        else:
            try: payload=await request.json()
            except ValueError as exc: raise InvalidSelection('Ungültiges JSON') from exc
            operation=request.match_info.get('operation','bindings')
            methods={'bindings':service.organization_save,'analyze':service.organization_analyze,
                     'names':service.organization_name_preview,'repair-preview':service.organization_repair_preview}
            try:
                if 'plan_id' in request.match_info:
                    fn=service.organization_name_apply if operation=='apply' else service.organization_name_restore_preview
                    result=await fn(zid,request.match_info['plan_id'],payload)
                else: result=await methods[operation](zid,payload)
            except (HomeAssistantError,TimeoutError):
                return web.json_response({'error':'organization_unavailable',
                    'message':'Bestandszugriff nicht bestätigt. Keine automatische Wiederholung; Planstatus prüfen.'},status=503,
                    headers={'Cache-Control':'no-store'})
        return web.json_response(result,headers={'Cache-Control':'no-store'})

    app.router.add_get('/api/v1/zones/{zone_id}/organization',endpoint)
    app.router.add_patch('/api/v1/zones/{zone_id}/organization',endpoint)
    app.router.add_post('/api/v1/zones/{zone_id}/organization/{operation:analyze|names|repair-preview}',endpoint)
    app.router.add_get('/api/v1/zones/{zone_id}/organization/plans/{plan_id}',endpoint)
    app.router.add_post('/api/v1/zones/{zone_id}/organization/plans/{plan_id}/{operation:apply|restore-preview}',endpoint)
    async def asset(request):
        return web.FileResponse(web_dir / 'organization.js',headers={'Cache-Control':'no-cache'})
    app.router.add_get('/assets/organization.js',asset)
