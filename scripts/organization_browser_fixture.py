"""Disposable full app, synthetic registry API, stdin-only test control."""
import asyncio
import json
import logging
from pathlib import Path
import sys
import tempfile
from aiohttp import web
from pilotsuite.app import create_app,SERVICE_KEY
from pilotsuite.core.settings import Settings
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pilotsuite'/'tests'))
from organization_support import seed

async def main():
    logging.basicConfig(level=logging.CRITICAL,stream=sys.stderr)
    with tempfile.TemporaryDirectory(prefix='organization-ui-') as tmp:
        root=Path(tmp)
        app=create_app(Settings(root,root/'options.json',golden_zone_area_ids=('room',),supervisor_token='',
            refresh_interval_seconds=3600,ingress_allowed_peers=('127.0.0.1',)))
        runner=web.AppRunner(app);await runner.setup();service=app[SERVICE_KEY]
        registry=await seed(service)
        site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        print(json.dumps({'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/'}),flush=True)
        try:
            while line:=await asyncio.to_thread(sys.stdin.readline):
                cmd=json.loads(line)
                if cmd['action']=='touch_revision':
                    rev=(await service.selections.get('room'))['revision']
                    await service.selections.patch('room',rev,{'binary_sensor.room_motion':'relevant'})
                elif cmd['action']!='snapshot': raise ValueError('Unsupported fixture command')
                cfg=await service.context.get('room')
                result={'config':cfg,'name_writes':service.client.organization_set_name.await_count,
                    'names':{e:r['name'] for e,r in registry.items()},
                    'automation_reads':service.client.automation_config.await_count,
                    'control_calls':service.client.call_bounded_service.await_count,
                    'helper_calls':service.client.helper_create_timer.await_count+service.client.helper_delete_timer.await_count,
                    'plan_count':len(await service.plans.organization_plans('room'))}
                print(json.dumps(result),flush=True)
        finally: await runner.cleanup()

if __name__=='__main__':asyncio.run(main())
