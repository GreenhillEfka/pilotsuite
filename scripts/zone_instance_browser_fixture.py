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
 class FixtureDatetime(datetime):
  @classmethod
  def now(cls,tz=None):return datetime.fromtimestamp(now,tz)
 status_clock=patch('pilotsuite.service.datetime',FixtureDatetime);status_clock.start()
 app=create_app(Settings(p,p/'options.json',golden_zone_area_ids=('room','z_empty','z_paused','z_other'),supervisor_token='',
   refresh_interval_seconds=3600,ingress_allowed_peers=('127.0.0.1',)))
 http=TestClient(TestServer(app));await http.start_server();s=app[SERVICE_KEY]
 for t in s._tasks:t.cancel()
 await asyncio.gather(*s._tasks,return_exceptions=True);s._tasks=[]
 world=await seed_shadow(s,now)
 for row in world['entities']:
  if row['entity_id']==SOURCE:row['labels']=['setup_demo','1']
  if row['entity_id']=='light.demo':row['device_id']='demo_device'
 world['devices'].append({'id':'demo_device','area_id':'room','labels':['setup_demo']})
 for eid,platform,uid,value,attrs in [
   ('input_boolean.existing_presence','input_boolean','existing-owner','on',{}),
   ('timer.existing_presence','timer','existing-timer','active',{'finishes_at':datetime.fromtimestamp(now+120,UTC).isoformat()}),
   ('binary_sensor.existing_presence','template','existing-public','on',{'device_class':'occupancy'}),
   ('automation.existing_presence','automation','existing-controller','on',{}),
   ('automation.existing_consumer','automation','existing-consumer','on',{})]:
  world['entities'].append({'entity_id':eid,'platform':platform,'unique_id':uid,'name':eid,'area_id':None,'disabled_by':None})
  world['states'].append(state(eid,value,now,attrs))
 s.client.related_automations=AsyncMock(return_value={'binary_sensor.existing_presence':['automation.existing_consumer']})
 async def existing_config(eid):
  if eid=='automation.existing_presence':
   return {'triggers':[{'trigger':'state','entity_id':SOURCE,'to':'on'}],
    'actions':[{'action':'input_boolean.turn_on','target':{'entity_id':'input_boolean.existing_presence'}},
               {'action':'timer.start','target':{'entity_id':'timer.existing_presence'}}]}
  return {'triggers':[{'trigger':'state','entity_id':'binary_sensor.existing_presence','to':'on'}],
   'actions':[{'action':'light.turn_on','target':{'entity_id':'light.synthetic_consumer'}}]}
 s.client.automation_config=AsyncMock(side_effect=existing_config)
 for zid,title in [('z_empty','Demo ohne Quellen'),('z_paused','Demo pausiert'),('z_other','Demo weiterer Raum')]:
  world['areas'].append({'area_id':zid,'name':title})
  old=next(z for z in await s.zones.list() if z['zone_id']==zid)
  await s.zones.save({'name':title,'area_ids':[zid],'extra_entity_ids':[],'enabled':zid!='z_paused','profile':'observe'},zid,old['revision'])
 source_registration=deepcopy(next(row for row in world['entities'] if row['entity_id']==SOURCE))
 s.client.snapshot=AsyncMock(side_effect=lambda:deepcopy(world))
 registry=deepcopy(world['entities'])
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
 async def metadata(eid,**fields):
  next(r for r in registry if r['entity_id']==eid).update(fields)
  for row in world['entities']:
   if row['entity_id']==eid:row.update(fields)
 public_id=None;template_inputs=None
 s.client.zone_output_registry=AsyncMock(side_effect=lambda:deepcopy(registry))
 s.client.zone_registry_entry=AsyncMock(side_effect=lambda eid:deepcopy(next(r for r in registry if r['entity_id']==eid)))
 s.client.zone_output_states=AsyncMock(side_effect=lambda:deepcopy(states))
 s.client.zone_output_service=AsyncMock(side_effect=service_call)
 s.client.zone_create_storage_helper=AsyncMock(side_effect=create_helper)
 s.client.zone_create_binary_sensor=AsyncMock(side_effect=create_sensor)
 s.client.zone_label_devices=AsyncMock(side_effect=lambda:{r['id']:r.get('labels',[]) for r in world['devices']})
 s.client.zone_structure_areas=AsyncMock(side_effect=lambda:deepcopy(world['areas']))
 labels=[{'label_id':str(i),'name':r} for i,r in enumerate(ROLES)]+[{'label_id':'zone','name':'room'},{'label_id':'setup_demo','name':'Habitus Demobereich'}]
 s.client.zone_labels=AsyncMock(side_effect=lambda:deepcopy(labels))
 async def create_label(name):
  from pilotsuite.core.zone_ontology import slug
  row={'label_id':slug(name),'name':name};labels.append(row);return deepcopy(row)
 s.client.zone_create_label=AsyncMock(side_effect=create_label)
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
   elif cmd['action']=='publish':await s._zone_publish_all() # Only the mocked client above.
   elif cmd['action']=='legacy_anchor_role':
    from pilotsuite.core.organization import identity
    zone=next(row for row in await s.zones.list() if row['zone_id']=='room')
    definition={k:zone[k] for k in ('name','area_ids','extra_entity_ids','enabled','profile')}
    catalog=await s.world.organization_catalog();inv=await s.selection_inventory('room')
    profile={'schema':'pilotsuite-zone-structure-v1','label_id':'fixture_anchor','members':{
      SOURCE:{'identity':identity(next(row for row in catalog if row['entity_id']==SOURCE)),'roles':['Habitus Zone']}}}
    await s.zones.save(definition,'room',zone['revision'],setup=profile,
      relevant=[row['entity_id'] for row in inv['items'] if row['decision']=='relevant'])
    await tick()
   elif cmd['action']=='member_identity':
    world['entities']=[row for row in world['entities'] if row['entity_id'] not in (SOURCE,'binary_sensor.demo_renamed','binary_sensor.demo_duplicate')]
    row=deepcopy(source_registration)
    if cmd['variant']=='renamed':row['entity_id']='binary_sensor.demo_renamed'
    elif cmd['variant']=='disabled':row['disabled_by']='user'
    if cmd['variant']!='missing':world['entities'].append(row)
    if cmd['variant']=='ambiguous':world['entities'].append({**row,'entity_id':'binary_sensor.demo_duplicate'})
    registry[:]=deepcopy(world['entities'])
    await s.world.replace(deepcopy(world))
   elif cmd['action']=='tag_membership_change':
    changed=cmd['changed']
    for row in world['entities']:
     if row['entity_id']==SOURCE:row['labels']=['1'] if changed else ['setup_demo','1']
     elif row['entity_id']==MOTION:row['labels']=['setup_demo'] if changed else []
     elif row['entity_id']=='light.demo':row['labels']=['3'] if changed else []
    registry[:]=deepcopy(world['entities'])
    await s.world.replace(deepcopy(world))
   elif cmd['action']=='light_group':
    eid='light.demo_group'
    world['entities'].append({'entity_id':eid,'name':'Lichtgruppe Demo','platform':'group',
      'unique_id':eid,'area_id':'room','disabled_by':None})
    world['states'].append(state(eid,'off',now,{'entity_id':['light.demo'],'supported_color_modes':['brightness']}))
    inv=await s.selection_inventory('room')
    await s.selections.patch('room',inv['revision'],{eid:'relevant'})
    await tick()
   elif cmd['action']!='snapshot':raise ValueError('Invalid fixture command')
   cfg=await s.context.get('room')
   print(json.dumps({'view':await s.zone_presence_view('room'),'zones':[{k:v for k,v in z.items() if k!='revision'} for z in await s.zones.list()],'mode':(cfg.get(KEY)or{}).get('mode'),
    'learning':cfg['learning'],'roles':cfg['roles'],'selections':await s.selections.get('room'),'history_reads':s.client.history.await_count,
    'automation_reads':s.client.automation_config.await_count,'organization':cfg.get('organization'),
    'helper_creates':s.client.zone_create_storage_helper.await_count+s.client.zone_create_binary_sensor.await_count,
    'label_creates':s.client.zone_create_label.await_count,'output_calls':s.client.zone_output_service.await_count,'metadata_calls':s.client.zone_set_metadata.await_count},allow_nan=False),flush=True)
 finally:
  await http.close();status_clock.stop();clock.stop();tmp.cleanup()
if __name__=='__main__':asyncio.run(main())
