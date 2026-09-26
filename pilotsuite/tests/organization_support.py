"""Disposable synthetic household, never production identifiers or credentials."""
from copy import deepcopy
from datetime import UTC,datetime
from unittest.mock import AsyncMock

SAMPLE = {
 'id':'synthetic-presence','alias':'PRIVATE_ALIAS_NOT_FOR_EXPORT',
 'triggers':[{'trigger':'state','entity_id':'binary_sensor.room_motion','to':'off',
              'for':{'minutes':"{{ states('input_number.room_timeout_old') | float(5) }}"}},
             {'trigger':'event','event_type':'timer.finished','event_data':{'entity_id':'timer.legacy_wait'}}],
 'actions':[{'if':[{'condition':'state','entity_id':'input_boolean.room_override','state':'off'}],
             'then':[{'action':'input_boolean.turn_on','target':{'entity_id':'input_boolean.legacy_presence'}}]},
            {'enabled':False,'action':'input_boolean.turn_off','target':{'entity_id':'input_boolean.disabled_copy'}}],
 'mode':'restart'}

async def seed(service):
    entries=[
      ('binary_sensor.room_motion','Motion source','homekit_controller','hardware-motion','room','off',{'device_class':'motion'}),
      ('input_boolean.legacy_presence','Legacy room flag','input_boolean','presence-stable',None,'off',{}),
      ('timer.legacy_wait','Legacy wait','timer','timer-stable',None,'idle',{'duration':'0:03:00'}),
      ('input_number.room_timeout_new','Room timeout','input_number','room_timeout_old',None,'5',{'unit_of_measurement':'min'}),
      ('input_boolean.room_override','Manual hold','input_boolean','override-stable','room','off',{}),
      ('input_boolean.room_blocker','Automation lock','input_boolean','blocker-stable','room','off',{}),
      ('binary_sensor.room_derived','Derived room state','template','derived-stable','room','off',{'device_class':'occupancy'}),
      ('automation.legacy_presence','Existing presence','automation','synthetic-presence','room','on',{}),
      ('sensor.room_power','Room power','demo','watts','room','35',{'unit_of_measurement':'W'}),
      ('sensor.room_energy','Room energy','demo','energy','room','35',{'unit_of_measurement':'kWh'}),
    ]
    registry={eid:{'entity_id':eid,'name':name,'platform':platform,'unique_id':uid,'area_id':area,'disabled_by':None}
              for eid,name,platform,uid,area,_,_ in entries}
    states=[{'entity_id':eid,'state':state,'attributes':attrs|{'friendly_name':name}} for eid,name,_,_,_,state,attrs in entries]
    await service.world.replace({'areas':[{'area_id':'room','name':'Demo room'},{'area_id':'other','name':'Other'}],
                                'entities':list(registry.values()),'states':states,'devices':[]})
    service._connected=service._stream_connected=True
    service._last_refresh_at=datetime.now(UTC).isoformat()
    service.client.automation_config=AsyncMock(return_value=deepcopy(SAMPLE))
    async def read(eid): return deepcopy(registry[eid])
    async def write(eid,name): registry[eid]['name']=name
    service.client.organization_registry=AsyncMock(side_effect=read)
    service.client.organization_set_name=AsyncMock(side_effect=write)
    service.client.call_bounded_service=AsyncMock(side_effect=AssertionError('No actuator/control calls'))
    service.client.helper_create_timer=AsyncMock(side_effect=AssertionError('No helper create'))
    service.client.helper_delete_timer=AsyncMock(side_effect=AssertionError('No helper delete'))
    await service._derive()
    return registry


def payload(revision,timing='timer'):
    return {'revision':revision,'timing':timing,'assignments':{
        'presence_sources':['binary_sensor.room_motion'],'presence_status':['input_boolean.legacy_presence'],
        'presence_timer':['timer.legacy_wait'],'presence_duration':['input_number.room_timeout_new'],
        'manual_override':['input_boolean.room_override'],'automation_blocker':['input_boolean.room_blocker'],
        'presence_automations':['automation.legacy_presence']},'confirm':True}
