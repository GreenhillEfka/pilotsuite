"""Bounded registry reads and display-name updates only, through native HA APIs."""
from __future__ import annotations
import asyncio
from aiohttp import ClientError
from pilotsuite.core.organization import ENTITY, HELPER_PLATFORMS


class OrganizationWorldMixin:
    async def organization_catalog(self):
        # One snapshot, whitelisted attributes. No options, credentials or raw config.
        async with self._lock:
            result=[]
            for eid in sorted(set(self._entities)|set(self._states)):
                if not ENTITY.fullmatch(eid): continue
                row=self._entities.get(eid,{})
                state=self._states.get(eid,{})
                attrs=state.get('attributes',{})
                result.append({'entity_id':eid,'name':row.get('name') or attrs.get('friendly_name') or eid,
                    'registry_name':row.get('name'),'original_name':row.get('original_name'),
                    'platform':row.get('platform'),'unique_id':row.get('unique_id'),
                    'area_id':self._entity_area_id(row),'device_id':row.get('device_id'),
                    'labels':list(row.get('labels') or []),'disabled':row.get('disabled_by') is not None,
                    'state':state.get('state'),'unit':attrs.get('unit_of_measurement'),
                    'device_class':row.get('device_class') or attrs.get('device_class'),
                    'in_registry':eid in self._entities,
                    'derived':row.get('platform') in ('input_boolean','template','group','threshold','min_max')})
            return result


class OrganizationClientMixin:
    async def organization_registry(self,entity_id):
        from .client import HomeAssistantError
        if not isinstance(entity_id,str) or len(entity_id)>255 or not ENTITY.fullmatch(entity_id):
            raise HomeAssistantError('Invalid registry identity')
        await self.start()
        try:
            async with asyncio.timeout(20):
                async with self._session.ws_connect(self._ws_url,heartbeat=30,max_msg_size=128*1024) as socket:
                    await self._authenticate(socket)
                    result=await self._command(socket,1,{'type':'config/entity_registry/get','entity_id':entity_id})
                    if not isinstance(result,dict) or result.get('entity_id')!=entity_id:
                        raise HomeAssistantError('Registry identity not confirmed')
                    return {k:result.get(k) for k in ('entity_id','platform','unique_id','name','disabled_by')}
        except (TimeoutError,ClientError) as exc:
            raise HomeAssistantError('Registry read unavailable') from exc

    async def organization_set_name(self,entity_id,name):
        from .client import HomeAssistantError
        if (not isinstance(entity_id,str) or len(entity_id)>255 or not ENTITY.fullmatch(entity_id)
                or name is not None and (not isinstance(name,str) or len(name)>255
                or any(ord(c)<32 for c in name))):
            raise HomeAssistantError('Invalid bounded display-name update')
        await self.start()
        try:
            async with asyncio.timeout(20):
                async with self._session.ws_connect(self._ws_url,heartbeat=30,max_msg_size=128*1024) as socket:
                    await self._authenticate(socket)
                    # Exact field allowlist. No new_entity_id, area, labels, options, grants or service calls.
                    result=await self._command(socket,1,{'type':'config/entity_registry/update','entity_id':entity_id,'name':name})
                    if not isinstance(result,dict) or result.get('entity_entry',{}).get('entity_id')!=entity_id:
                        raise HomeAssistantError('Name update outcome unknown')
        except (TimeoutError,ClientError) as exc:
            raise HomeAssistantError('Name update outcome unknown') from exc
