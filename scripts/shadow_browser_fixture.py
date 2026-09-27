"""Disposable actual-app shadow test fixture; controls only over parent stdin."""
import asyncio
from copy import deepcopy
from datetime import UTC, datetime
import json
import logging
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
from aiohttp import web
from pilotsuite.app import SERVICE_KEY, create_app
from pilotsuite.core.settings import Settings
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pilotsuite'/'tests'))
from test_presence_shadow import seed_shadow, state, NOW, SOURCE, OWNER

async def main():
    logging.basicConfig(level=logging.ERROR,stream=sys.stderr)
    clock={'now':NOW}
    with tempfile.TemporaryDirectory(prefix='shadow-fixture-') as temp, patch('time.time',side_effect=lambda:clock['now']):
        root=Path(temp);app=create_app(Settings(root,root/'options.json',golden_zone_area_ids=('room',),
            supervisor_token='',refresh_interval_seconds=3600,ingress_allowed_peers=('127.0.0.1',)))
        runner=web.AppRunner(app);await runner.setup();s=app[SERVICE_KEY]
        for t in s._tasks:t.cancel()
        await asyncio.gather(*s._tasks,return_exceptions=True);s._tasks=[]
        world=await seed_shadow(s,clock['now'])
        try:
            site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
            print(json.dumps({'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/#ps-zone'}),flush=True)
            while line:=await asyncio.to_thread(sys.stdin.readline):
                c=json.loads(line)
                if c['action']=='tick':
                    clock['now']+=c.get('seconds',1)
                    for eid,value in c.get('values',{}).items():
                        row=next(r for r in world['states'] if r['entity_id']==eid)
                        row.update(state(eid,value,clock['now'],row['attributes']))
                    await s.world.replace(deepcopy(world));s._last_refresh_at=datetime.fromtimestamp(clock['now'],UTC).isoformat()
                    async with s._projection_lock:await s._shadow_tick_locked(now=clock['now'])
                elif c['action']=='replace_source':
                    world['entities'][0]['unique_id']='changed-synthetic-identity'
                    await s.world.replace(deepcopy(world))
                    async with s._projection_lock:await s._shadow_tick_locked(now=clock['now'])
                elif c['action']!='snapshot':raise ValueError('Unknown synthetic control')
                cfg=await s.context.get('room')
                print(json.dumps({'view':await s.presence_shadow('room'),'learning':cfg['learning'],
                    'roles':cfg['roles'],'writes':sum(getattr(s.client,k).await_count for k in
                      ('call_bounded_service','helper_create_timer','helper_delete_timer','organization_set_name')),
                    'history_reads':s.client.history.await_count},allow_nan=False),flush=True)
        finally:await runner.cleanup()

if __name__=='__main__':asyncio.run(main())
