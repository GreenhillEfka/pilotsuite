"""Disposable actual-app zone fixture. No household token or outgoing HA access."""
import asyncio,json,logging,sys,tempfile
from copy import deepcopy
from datetime import UTC,datetime
from pathlib import Path
from unittest.mock import AsyncMock,patch
from aiohttp.test_utils import TestClient,TestServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pilotsuite/tests'))
from test_presence_shadow import seed_shadow,state,NOW,SOURCE,MOTION
from pilotsuite.app import create_app,SERVICE_KEY
from pilotsuite.core.settings import Settings
from pilotsuite.core.zone_presence_store import KEY
from pilotsuite.core.zone_ontology import ROLES

async def main():
 logging.basicConfig(level=logging.CRITICAL,stream=sys.stderr)
 tmp=tempfile.TemporaryDirectory();p=Path(tmp.name);now=NOW
 clock=patch('time.time',side_effect=lambda:now);clock.start()
 app=create_app(Settings(p,p/'options.json',golden_zone_area_ids=('room',),supervisor_token='',
   refresh_interval_seconds=3600,ingress_allowed_peers=('127.0.0.1',)))
 http=TestClient(TestServer(app));await http.start_server();s=app[SERVICE_KEY]
 for t in s._tasks:t.cancel()
 await asyncio.gather(*s._tasks,return_exceptions=True);s._tasks=[]
 world=await seed_shadow(s,now)
 registry=[{'entity_id':e['entity_id'],'unique_id':e['unique_id'],'platform':e['platform'],
   'name':e['name'],'labels':[],'disabled_by':None} for e in world['entities']]
 states={e['entity_id']:deepcopy(e) for e in world['states']}
 async def create_helper(domain,name,grace_seconds=300):
  eid=domain+'.'+name;registry.append({'entity_id':eid,'unique_id':name,'platform':domain,'name':name,'labels':[],'disabled_by':None})
  states[eid]=state(eid,'idle' if domain=='timer' else 'off',now);return {'id':name,'name':name}
 async def create_sensor(name,owner,valid,lease):
  nonlocal public_id,template_inputs
  template_inputs=(owner,valid,lease)
  from pilotsuite.core.zone_ontology import slug
  public_id='binary_sensor.'+slug(name)
  registry.append({'entity_id':public_id,'unique_id':'template_uid','platform':'template','config_entry_id':'entry','name':name,'labels':[],'disabled_by':None})
  states[public_id]=state(public_id,'unavailable',now);return {'type':'create_entry','result':{'entry_id':'entry'}}
 async def service_call(domain,service,eid,data=None):
  val='on' if service=='turn_on' else 'off' if service=='turn_off' else 'active' if service=='start' else 'idle' if service=='cancel' else str(data['timestamp'])
  states[eid]=state(eid,val,now)
  if template_inputs:
   owner,valid,lease=template_inputs
   try:alive=float(states.get(lease,{}).get('state','0'))>now
   except ValueError:alive=False
   v=states.get(owner,{}).get('state') if alive and states.get(valid,{}).get('state')=='on' else 'unavailable'
   states[public_id]=state(public_id,v,now)
 async def metadata(eid,**fields):next(r for r in registry if r['entity_id']==eid).update(fields)
 public_id=None;template_inputs=None
 s.client.zone_output_registry=AsyncMock(side_effect=lambda:deepcopy(registry))
 s.client.zone_output_states=AsyncMock(side_effect=lambda:deepcopy(states))
 s.client.zone_output_service=AsyncMock(side_effect=service_call)
 s.client.zone_create_storage_helper=AsyncMock(side_effect=create_helper)
 s.client.zone_create_binary_sensor=AsyncMock(side_effect=create_sensor)
 s.client.zone_labels=AsyncMock(return_value=[{'label_id':str(i),'name':r} for i,r in enumerate(ROLES)]+[{'label_id':'zone','name':'room'}])
 s.client.zone_set_metadata=AsyncMock(side_effect=metadata)
 s.client.history=AsyncMock(return_value={'records':{SOURCE:[{'lu':NOW-3600,'s':'off'},{'lu':NOW-300,'s':'on'}]},'metadata':{}})
 async def tick(delta=1,values=None):
  nonlocal now
  now+=delta
  for e,v in (values or {}).items():
   row=next(r for r in world['states'] if r['entity_id']==e);row.update(state(e,v,now,row['attributes']))
  await s.world.replace(deepcopy(world));s._last_refresh_at=datetime.fromtimestamp(now,UTC).isoformat()
  async with s._projection_lock:await s._zone_presence_tick_locked()
 try:
  await tick(values={SOURCE:'on'})
  print(json.dumps({'url':str(http.make_url('/#ps-zone')),'now':now}),flush=True)
  while line:=await asyncio.to_thread(sys.stdin.readline):
   cmd=json.loads(line)
   if cmd['action']=='tick':await tick(cmd.get('seconds',1),cmd.get('values',{}))
   elif cmd['action']!='snapshot':raise ValueError('Invalid fixture command')
   cfg=await s.context.get('room')
   print(json.dumps({'view':await s.zone_presence_view('room'),'mode':(cfg.get(KEY)or{}).get('mode'),
    'learning':cfg['learning'],'roles':cfg['roles'],'history_reads':s.client.history.await_count,
    'helper_creates':s.client.zone_create_storage_helper.await_count+s.client.zone_create_binary_sensor.await_count,
    'output_calls':s.client.zone_output_service.await_count,'metadata_calls':s.client.zone_set_metadata.await_count},allow_nan=False),flush=True)
 finally:
  await http.close();clock.stop();tmp.cleanup()
if __name__=='__main__':asyncio.run(main())
