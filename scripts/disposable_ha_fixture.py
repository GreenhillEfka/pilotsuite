"""Real HA Core test server controlled only by its parent process's stdin.

No household token, files or network endpoints. The generated credential crosses a
private subprocess pipe only and is never included in CI output or artifacts.
"""
from __future__ import annotations
import asyncio
import json
import logging
from pathlib import Path
import socket
import sys
import tempfile
from homeassistant.auth.const import GROUP_ID_ADMIN
from homeassistant import loader
from homeassistant.bootstrap import async_from_config_dict
from homeassistant.const import __version__
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry, entity_registry

PREFIX='PILOTSUITE_PROTOCOL:'


def reply(data):
    print(PREFIX+json.dumps(data),flush=True)


async def main():
    logging.basicConfig(level=logging.WARNING,stream=sys.stderr)
    with tempfile.TemporaryDirectory(prefix='pilotsuite-core-protocol-') as temp:
        hass=HomeAssistant(temp)
        # Match Core bootstrap: initialize loader caches after config_dir is set.
        loader.async_setup(hass)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        config={'homeassistant':{'name':'Disposable protocol test','latitude':0,'longitude':0,
                    'elevation':0,'time_zone':'UTC','unit_system':'metric'},
                'http':{'server_host':'127.0.0.1','server_port':port},
                'api':{},'websocket_api':{},'config':{},'input_boolean':{},
                'input_datetime':{},'timer':{},'template':{}}
        try:
            assert await async_from_config_dict(config,hass) is hass
            user=await hass.auth.async_create_system_user('isolated-pilotsuite',group_ids=[GROUP_ID_ADMIN])
            refresh=await hass.auth.async_create_refresh_token(user)
            token=hass.auth.async_create_access_token(refresh)
            await hass.async_start();await hass.async_block_till_done()
            area=area_registry.async_get(hass).async_create('Protocol Room')
            registry=entity_registry.async_get(hass)
            source=registry.async_get_or_create('binary_sensor','protocol_test','presence',
                                               suggested_object_id='protocol_presence')
            registry.async_update_entity(source.entity_id,area_id=area.id)
            hass.states.async_set(source.entity_id,'on',{'device_class':'occupancy'})
            await hass.async_block_till_done()
            reply({'port':port,'token':token,'source':source.entity_id,'area':area.id,'version':__version__})
            while line:=await asyncio.to_thread(sys.stdin.readline):
                data=json.loads(line)
                if data=={'operation':'stop'}:
                    reply({'stopping':True});break
                if set(data)!={'operation','value'} or data['operation']!='source' or data['value'] not in ('on','off','unavailable',None):
                    raise ValueError('Unsupported disposable fixture operation')
                if data['value'] is not None:
                    hass.states.async_set(source.entity_id,data['value'],{'device_class':'occupancy'})
                await hass.async_block_till_done()
                reply({'settled':True})
        finally:
            await hass.async_stop()


if __name__=='__main__':asyncio.run(main())
