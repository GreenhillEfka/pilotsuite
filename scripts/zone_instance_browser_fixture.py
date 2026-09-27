"""Disposable real-app fixture. No household token, no outgoing Home Assistant access."""
import asyncio,json,logging,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pilotsuite/tests'))
from test_zone_presence_v2 import ZoneInstanceIntegrationTests,SOURCE,MOTION,KEY

async def main():
    logging.basicConfig(level=logging.CRITICAL,stream=sys.stderr)
    f=ZoneInstanceIntegrationTests('test_get_has_no_ha_write')
    await f.asyncSetUp()
    try:
        await f.tick(values={SOURCE:'on'})
        print(json.dumps({'url':str(f.http.make_url('/#ps-zone')),'now':f.now}),flush=True)
        while line:=await asyncio.to_thread(sys.stdin.readline):
            c=json.loads(line)
            if c['action']=='tick':await f.tick(c.get('seconds',1),c.get('values',{}))
            elif c['action']!='snapshot':raise ValueError('Invalid fixture command')
            config=await f.s.context.get('room')
            print(json.dumps({'view':await f.s.zone_presence_view('room'),'mode':(config.get(KEY)or{}).get('mode'),
                'learning':config['learning'],'roles':config['roles'],'history_reads':f.s.client.history.await_count,
                'helper_creates':f.s.client.zone_create_storage_helper.await_count+f.s.client.zone_create_binary_sensor.await_count,
                'output_calls':f.s.client.zone_output_service.await_count,'metadata_calls':f.s.client.zone_set_metadata.await_count},allow_nan=False),flush=True)
    finally:await f.asyncTearDown()
if __name__=='__main__':asyncio.run(main())
