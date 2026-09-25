"""Isolated full-app browser fixture. No token, HA connection or real-house data.

This script is test tooling, never imported by the app or exposed as an HTTP API.
Control messages arrive only over the parent test process's stdin. All fixture
mutations use existing canonical owners and a temporary database.
"""
from __future__ import annotations
import asyncio
import copy
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
import sqlite3
import sys
import tempfile
from unittest.mock import AsyncMock, patch

from aiohttp import web
from pilotsuite.app import create_app, SERVICE_KEY
from pilotsuite.core.settings import Settings


async def main():
    logging.basicConfig(level=logging.ERROR, stream=sys.stderr)
    with tempfile.TemporaryDirectory(prefix='pilotsuite-browser-') as temp:
        root=Path(temp)
        app=create_app(Settings(root,root/'options.json',golden_zone_area_ids=('a','b'),
            supervisor_token='',refresh_interval_seconds=3600,ingress_allowed_peers=('127.0.0.1',)))
        runner=web.AppRunner(app);await runner.setup()
        service=app[SERVICE_KEY]
        now=datetime(2026,9,24,12,tzinfo=UTC).timestamp()
        clock=patch('time.time',return_value=now);clock.start()
        try:
            world={'areas':[{'area_id':'a','name':'Synthetic A'},{'area_id':'b','name':'Synthetic B'}],
                'devices':[], 'entities':[
                    {'entity_id':'binary_sensor.synthetic','area_id':'a'},
                    {'entity_id':'light.synthetic','area_id':'a'},
                    {'entity_id':'light.other','area_id':'b'}],
                'states':[
                    {'entity_id':'binary_sensor.synthetic','state':'off','attributes':{'device_class':'motion'}},
                    {'entity_id':'light.synthetic','state':'off','attributes':{}},
                    {'entity_id':'light.other','state':'off','attributes':{}}]}
            await service.world.replace(copy.deepcopy(world))
            await service.selections.patch('a',0,{'binary_sensor.synthetic':'relevant','light.synthetic':'relevant'})
            await service.context.configure('a',1,{'presence':['binary_sensor.synthetic']},True,now=now-12*86400)
            for day in (10,9,8,3,2,1):
                for hour in (0,4):
                    for minute in (0,10):
                        t=now-day*86400+hour*3600+minute*60
                        await service.context.record('a','binary_sensor.synthetic',t,'unknown',now=t)
            await service._derive()
            inventory=await service.selection_inventory('a')
            patterns=(await service.context.report('a'))['patterns']
            ids=[]
            for i,pattern in enumerate(patterns):
                draft=await service.plans.create_draft('a',pattern['id'],2,inventory)
                fields=copy.deepcopy(draft['fields']);fields['title']='Angaben ergänzen' if i==0 else 'Lichtkomfort prüfen'
                if i:
                    fields.update(goal='Passendes Licht',trigger='Präsenz',conditions='Bei Dunkelheit',
                                  manual_override='Manuell hat Vorrang',target_ids=['light.synthetic'])
                saved=await service.plans.save_draft('a',draft['id'],{
                    'revision':draft['revision'],'zone_revision':2,'fields':fields,'refresh_source':False},inventory)
                ids.append(saved['id'])
            assert len(ids)==2
            service.client.related_automations=AsyncMock(return_value={
                'light.synthetic':['automation.synthetic'],'binary_sensor.synthetic':['automation.synthetic']})
            service.client.automation_config=AsyncMock(return_value={
                'alias':'PRIVATE_CONFIG_CANARY','triggers':[{'trigger':'state','entity_id':'binary_sensor.synthetic'}],
                'actions':[{'action':'light.turn_on','target':{'entity_id':'light.synthetic'}}]})
            # Rich synthetic workspace only. Other regression fixtures retain their exact basis.
            service.client.call_bounded_service=AsyncMock(side_effect=AssertionError("No HA writes in UI tests"))
            service.client.helper_create_timer=AsyncMock(side_effect=AssertionError("No helper creation in UI tests"))
            service.client.helper_delete_timer=AsyncMock(side_effect=AssertionError("No helper deletion in UI tests"))
            if '--workspace' in sys.argv:
                entries=[
                    ('sensor.synthetic_temperature','Raumtemperatur','21.8',{'device_class':'temperature','unit_of_measurement':'°C'}),
                    ('sensor.synthetic_humidity','Luftfeuchte','48',{'device_class':'humidity','unit_of_measurement':'%'}),
                    ('sensor.synthetic_lux','Tageslicht am Fenster','430',{'device_class':'illuminance','unit_of_measurement':'lx'}),
                    ('binary_sensor.synthetic_occupancy','Präsenz am Sitzplatz','off',{'device_class':'occupancy'}),
                    ('input_boolean.synthetic_presence','Logischer Raumstatus','off',{}),
                    ('timer.pilotsuite_a_anwesenheitsnachlauf','Nachlauftimer','idle',{}),
                    ('climate.synthetic','Raumregler','heat',{}),
                    ('media_player.synthetic','Musik im Wohnbereich','idle',{}),
                ]
                for eid,name,state,attrs in entries:
                    world['entities'].append({'entity_id':eid,'area_id':'a','name':name})
                    world['states'].append({'entity_id':eid,'state':state,'attributes':attrs})
                world['entities'][0]['name']='Bewegung im Durchgang'
                world['entities'][1]['name']='Leselicht'
                await service.world.replace(copy.deepcopy(world))
                rev=(await service.selections.get('a'))['revision']
                await service.selections.patch('a',rev,{e[0]:'relevant' for e in entries})
                rev=(await service.selections.get('a'))['revision']
                await service.context.configure('a',rev,{
                    'presence':['binary_sensor.synthetic','binary_sensor.synthetic_occupancy','input_boolean.synthetic_presence'],
                    'temperature':['sensor.synthetic_temperature'],'humidity':['sensor.synthetic_humidity'],
                    'illuminance':['sensor.synthetic_lux'],'light':['light.synthetic'],
                    'climate':['climate.synthetic'],'media':['media_player.synthetic']},False)
                for zone in await service.zones.list():
                    definition={k:zone[k] for k in ('name','area_ids','extra_entity_ids','enabled','profile')}
                    definition.update(name='Wohnbereich · Demo' if zone['zone_id']=='a' else 'Arbeitszimmer · Demo',profile='observe')
                    await service.zones.save(definition,zone['zone_id'],zone['revision'])
                service._connected=service._stream_connected=True
                service._last_refresh_at=datetime.now(UTC).isoformat()
                await service._derive()
            site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
            port=site._server.sockets[0].getsockname()[1]
            print(json.dumps({'url':f'http://127.0.0.1:{port}/' + ('' if '--workspace' in sys.argv else '#ps-all'),'draft_ids':ids}),flush=True)
            while line:=await asyncio.to_thread(sys.stdin.readline):
                command=json.loads(line);action=command['action']
                if action=='snapshot':
                    with sqlite3.connect(service.selections.path) as db:
                        notes=[json.loads(row[0]) for row in db.execute('SELECT records FROM routine_review_notes')]
                    result={'related_reads':service.client.related_automations.await_count,
                            'config_reads':service.client.automation_config.await_count,
                            'notes':notes,'learning':(await service.context.get('a'))['learning'],
                            'drafts':await service.plans.drafts('a',await service.selection_inventory('a')),
                            'roles':(await service.context.get('a'))['roles'],
                            'ha_writes':service.client.call_bounded_service.await_count,
                            'helper_writes':service.client.helper_create_timer.await_count+service.client.helper_delete_timer.await_count}
                elif action=='touch_draft':
                    inventory=await service.selection_inventory('a')
                    draft=next(d for d in await service.plans.drafts('a',inventory) if d['id']==command['id'])
                    fields=copy.deepcopy(draft['fields']);fields['goal']='Changed in another synthetic session'
                    await service.plans.save_draft('a',draft['id'],{'revision':draft['revision'],
                        'zone_revision':inventory['revision'],'fields':fields,'refresh_source':False},inventory)
                    result={'changed':True}
                elif action=='config_change':
                    service.client.automation_config.return_value['actions'][0]['action']='light.turn_off'
                    result={'changed':True}
                elif action=='source_unavailable':
                    changed=copy.deepcopy(world);changed['states'][0]['state']='unavailable'
                    await service.world.replace(changed);await service._derive();result={'changed':True}
                else:
                    raise ValueError('Unsupported synthetic control command')
                print(json.dumps(result,ensure_ascii=True),flush=True)
        finally:
            clock.stop();await runner.cleanup()


if __name__=='__main__':
    asyncio.run(main())
