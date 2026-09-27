"""Native Ingress-protected per-zone functions; analysis is not an execution grant."""
from aiohttp import web
from .core.selections import InvalidSelection
from .ha.client import HomeAssistantError


def register_zone_presence(app,service_key):
    async def view(request):
        return web.json_response(await request.app[service_key].zone_presence_view(request.match_info['zone_id']),headers={'Cache-Control':'no-store'})
    async def config(request):
        return await invoke(request,'zone_presence_configure')
    async def history(request):
        return await invoke(request,'zone_data')
    async def setup(request):
        return await invoke(request,'zone_package_preview')
    async def setup_apply(request):
        return await invoke(request,'zone_package_apply',plan=True)
    async def ontology(request):
        try:
            result=await request.app[service_key].ontology_catalog(request.match_info['zone_id'])
        except HomeAssistantError:
            return web.json_response({'message':'Ontologiebestand nicht lesbar'},status=503)
        return web.json_response(result,headers={'Cache-Control':'no-store'})
    async def ontology_preview(request):
        return await invoke(request,'ontology_preview')
    async def ontology_apply(request):
        return await invoke(request,'ontology_apply',plan=True)
    async def ontology_restore(request):
        return await invoke(request,'ontology_restore_preview',plan=True)
    async def invoke(request,method,plan=False):
        try:payload=await request.json()
        except ValueError as exc:raise InvalidSelection('Ungültiges JSON') from exc
        service=request.app[service_key];zid=request.match_info['zone_id']
        args=(zid,request.match_info['plan_id'],payload) if plan else (zid,payload)
        try:result=await getattr(service,method)(*args)
        except (HomeAssistantError,TimeoutError):
            return web.json_response({'message':'HA-Ergebnis nicht bestätigt. Kein automatisches Wiederholen; Planstatus prüfen.'},status=503,headers={'Cache-Control':'no-store'})
        return web.json_response(result,headers={'Cache-Control':'no-store'})
    app.router.add_get('/api/v1/zones/{zone_id}/presence',view)
    app.router.add_put('/api/v1/zones/{zone_id}/presence',config)
    app.router.add_post('/api/v1/zones/{zone_id}/data',history)
    app.router.add_post('/api/v1/zones/{zone_id}/presence/package',setup)
    app.router.add_post('/api/v1/zones/{zone_id}/presence/package/{plan_id}/apply',setup_apply)
    app.router.add_get('/api/v1/zones/{zone_id}/ontology',ontology)
    app.router.add_post('/api/v1/zones/{zone_id}/ontology',ontology_preview)
    app.router.add_post('/api/v1/zones/{zone_id}/ontology/{plan_id}/apply',ontology_apply)

    app.router.add_post('/api/v1/zones/{zone_id}/ontology/{plan_id}/restore-preview',ontology_restore)
