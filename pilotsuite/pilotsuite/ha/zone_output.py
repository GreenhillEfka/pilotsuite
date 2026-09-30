"""Private allowlisted HA transport for managed zone helpers and ontology metadata.

No generic HTTP/WS endpoint is exposed. Creates are never retried here. A failed or
ambiguous write is resolved by the caller's durable plan, not repeated automatically.
"""
from __future__ import annotations
import asyncio
import re
from urllib.parse import urlsplit, urlunsplit
from aiohttp import ClientError

ID=re.compile(r'[a-z_]+\.[a-z0-9_]+\Z')
HELPERS={'input_boolean','timer','input_datetime'}

class ZoneOutputClientMixin:
    async def _zone_ws(self, command):
        from .client import HomeAssistantError, MAX_WS_MESSAGE_BYTES
        await self.start()
        try:
            async with asyncio.timeout(25):
                async with self._session.ws_connect(self._ws_url,heartbeat=30,max_msg_size=MAX_WS_MESSAGE_BYTES) as ws:
                    await self._authenticate(ws)
                    return await self._command(ws,1,command)
        except (TimeoutError,ClientError) as exc:
            raise HomeAssistantError('Zonen-Zugriff nicht bestätigt') from exc

    async def zone_output_registry(self):
        from .client import HomeAssistantError
        rows=await self._zone_ws({'type':'config/entity_registry/list'})
        if not isinstance(rows,list) or len(rows)>50000: raise HomeAssistantError('Register nicht vollständig')
        # No credentials, config-entry payloads or integration secrets.
        return [{k:r.get(k) for k in ('entity_id','unique_id','platform','config_entry_id','name','labels','disabled_by','device_id')}
                for r in rows if isinstance(r,dict)]

    async def zone_label_devices(self):
        from .client import HomeAssistantError
        rows = await self._zone_ws({'type': 'config/device_registry/list'})
        if not isinstance(rows, list) or len(rows) > 50000:
            raise HomeAssistantError('Geräteregister nicht vollständig')
        return {row['id']: list(row.get('labels') or []) for row in rows if isinstance(row, dict) and 'id' in row}

    async def zone_output_states(self):
        from .client import HomeAssistantError
        rows=await self._zone_ws({'type':'get_states'})
        if not isinstance(rows,list): raise HomeAssistantError('Zustände nicht lesbar')
        return {r['entity_id']:r for r in rows if isinstance(r,dict) and isinstance(r.get('entity_id'),str)}

    async def zone_labels(self):
        from .client import HomeAssistantError
        rows=await self._zone_ws({'type':'config/label_registry/list'})
        if not isinstance(rows,list): raise HomeAssistantError('Labels nicht lesbar')
        return rows

    async def zone_structure_areas(self):
        from .client import HomeAssistantError
        rows = await self._zone_ws({'type': 'config/area_registry/list'})
        if not isinstance(rows, list) or any(not isinstance(row, dict) or 'area_id' not in row for row in rows):
            raise HomeAssistantError('Bereichsregister nicht vollständig')
        return [{key: row.get(key) for key in ('area_id', 'name', 'floor_id')} for row in rows]

    async def zone_registry_entry(self, eid):
        from .client import HomeAssistantError
        if not isinstance(eid, str) or not ID.fullmatch(eid):
            raise HomeAssistantError('Ungültige Registry-Identität')
        row = await self._zone_ws({'type': 'config/entity_registry/get', 'entity_id': eid})
        if not isinstance(row, dict) or row.get('entity_id') != eid:
            raise HomeAssistantError('Registry-Identität nicht bestätigt')
        return {key: row.get(key) for key in ('entity_id', 'unique_id', 'platform', 'name', 'labels', 'disabled_by')}

    async def zone_create_label(self,name):
        from .client import HomeAssistantError
        if not isinstance(name,str) or not 1<=len(name)<=80 or any(ord(c)<32 for c in name):
            raise HomeAssistantError('Ungültiger Labelname')
        return await self._zone_ws({'type':'config/label_registry/create','name':name})

    async def zone_set_metadata(self,eid,*,name,labels):
        from .client import HomeAssistantError
        if (not isinstance(eid,str) or not ID.fullmatch(eid) or
            name is not None and (not isinstance(name,str) or not 1<=len(name)<=120 or any(ord(c)<32 for c in name)) or
            not isinstance(labels,list) or len(labels)>100 or any(not isinstance(v,str) or not v or len(v)>128 for v in labels)):
            raise HomeAssistantError('Ungültige Metadatenänderung')
        return await self._zone_ws({'type':'config/entity_registry/update','entity_id':eid,'name':name,'labels':labels})

    async def zone_create_storage_helper(self,domain,name,*,grace_seconds=300):
        from .client import HomeAssistantError
        if domain not in HELPERS or not isinstance(name,str) or not re.fullmatch(r'ps_[a-f0-9]{12}_[a-z_]+',name):
            raise HomeAssistantError('Nur neue eindeutig benannte PilotSuite-Helfer erlaubt')
        command={'type':domain+'/create','name':name}
        if domain=='timer':
            if type(grace_seconds) is not int or not 1<=grace_seconds<=86400: raise HomeAssistantError('Ungültiger Nachlauf')
            command.update(duration=f'{grace_seconds//3600:02d}:{grace_seconds//60%60:02d}:{grace_seconds%60:02d}',restore=True)
        if domain=='input_datetime': command.update(has_date=True,has_time=True)
        # HA derives storage ID from name. Never overwrite WS message id with a helper id.
        return await self._zone_ws(command)

    async def _zone_template_flow(self,path,data):
        from .client import HomeAssistantError
        if not re.fullmatch(r'/api/config/config_entries/flow(?:/[a-zA-Z0-9_-]+)?',path):
            raise HomeAssistantError('Unzulässiger Konfigurationspfad')
        split=urlsplit(self._ws_url)
        prefix=split.path[:-len('/api/websocket')] if split.path.endswith('/api/websocket') else split.path[:-len('/websocket')]
        url=urlunsplit(('https' if split.scheme=='wss' else 'http',split.netloc,prefix+path,'',''))
        await self.start()
        try:
            async with asyncio.timeout(25):
                async with self._session.post(url,json=data,headers={'Authorization':'Bearer '+self._token},allow_redirects=False) as response:
                    if response.status not in (200,201): raise HomeAssistantError('Template-Flow nicht bestätigt')
                    return await response.json()
        except (TimeoutError,ClientError,ValueError) as exc:
            raise HomeAssistantError('Template-Ergebnis unklar; nicht wiederholen') from exc

    async def zone_create_binary_sensor(self,name,owner,valid,lease):
        from .client import HomeAssistantError
        if (not isinstance(name,str) or len(name)>120 or any(not isinstance(e,str) or not ID.fullmatch(e) for e in (owner,valid,lease))
            or not owner.startswith('input_boolean.ps_') or not valid.startswith('input_boolean.ps_') or not lease.startswith('input_datetime.ps_')):
            raise HomeAssistantError('Unzulässige Zonen-Sensorreferenz')
        path='/api/config/config_entries/flow'
        flow=await self._zone_template_flow(path,{'handler':'template','show_advanced_options':True})
        if not isinstance(flow,dict) or flow.get('type')!='menu' or 'binary_sensor' not in flow.get('menu_options',[]):
            raise HomeAssistantError('Template-Menü muss explizit binary_sensor anbieten')
        flow_id=flow.get('flow_id')
        if not isinstance(flow_id,str): raise HomeAssistantError('Fehlende Flow-ID')
        path+='/'+flow_id
        form=await self._zone_template_flow(path,{'next_step_id':'binary_sensor'})
        if not isinstance(form,dict) or form.get('type')!='form': raise HomeAssistantError('Template-Formular nicht bestätigt')
        payload={'name':name,'device_class':'occupancy',
            'state':"{{ is_state('"+owner+"', 'on') }}",
            'additional_options':{'availability':"{{ has_value('"+owner+"') and is_state('"+valid+"', 'on') and (state_attr('"+lease+"', 'timestamp') | float(0)) > as_timestamp(now()) }}"}}
        result=await self._zone_template_flow(path,payload)
        if not isinstance(result,dict) or result.get('type')!='create_entry':
            raise HomeAssistantError('Sensoranlage nicht bestätigt; Flow prüfen')
        return result

    async def zone_output_service(self,domain,service,eid,data=None):
        from .client import HomeAssistantError
        allowed={('input_boolean','turn_on'),('input_boolean','turn_off'),('timer','start'),('timer','cancel'),('input_datetime','set_datetime')}
        if (domain,service) not in allowed or not isinstance(eid,str) or not re.fullmatch(re.escape(domain)+r'\.ps_[a-f0-9]{12}_[a-z_]+',eid):
            raise HomeAssistantError('Ausgang ist kein verwalteter Zonenhelfer')
        data=data or {}
        if (domain,service)==('timer','start'):
            if set(data)!={'duration'} or type(data['duration']) is not int or not 1<=data['duration']<=86400:
                raise HomeAssistantError('Ungültige Restdauer')
        elif domain=='input_datetime':
            if set(data)!={'timestamp'} or type(data['timestamp']) not in (int,float) or not 1<=data['timestamp']<4102444800:
                raise HomeAssistantError('Ungültiges Gültigkeitsende')
        elif data: raise HomeAssistantError('Zusätzliche Aktionsdaten nicht erlaubt')
        return await self._zone_ws({'type':'call_service','domain':domain,'service':service,'target':{'entity_id':eid},'service_data':data})
