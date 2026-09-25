"""Disposable actual app for maintenance tests. Control only over stdin; no HA."""
from __future__ import annotations
import asyncio
from datetime import UTC, datetime
import json
import logging
from pathlib import Path
import sys
import tempfile
from unittest.mock import AsyncMock
from aiohttp import web
from pilotsuite import VERSION
from pilotsuite.app import create_app, SERVICE_KEY
from pilotsuite.core.settings import Settings
from pilotsuite.core.maintenance import APP_SLUG

async def main():
    logging.basicConfig(level=logging.CRITICAL, stream=sys.stderr)
    with tempfile.TemporaryDirectory(prefix='pilotsuite-maintenance-') as temp:
        root = Path(temp)
        broken = '--broken' in sys.argv
        if broken:
            (root/'selections.sqlite3').write_bytes(b'not a SQLite database')
        app = create_app(Settings(root, root/'options.json', golden_zone_area_ids=('a',),
            supervisor_token='', refresh_interval_seconds=3600, ingress_allowed_peers=('127.0.0.1',)))
        runner = web.AppRunner(app)
        await runner.setup()
        service = app[SERVICE_KEY]
        reads=[]
        async def helpers(kind):
            reads.append(kind)
            return [{'id':'original_timer','duration':'0:03:00','restore':False}] if kind=='timer' else []
        service.client.helper_collection=helpers
        service.client.snapshot=AsyncMock(side_effect=AssertionError('No snapshot I/O'))
        service.client.automation_config=AsyncMock(side_effect=AssertionError('No automation I/O'))
        try:
            if not broken:
                await service.world.replace({'areas':[{'area_id':'a','name':'Testbereich'}],
                    'entities':[{'entity_id':'timer.renamed','platform':'timer','unique_id':'original_timer','area_id':'a'},
                                {'entity_id':'update.renamed','platform':'hassio','unique_id':APP_SLUG+'_version_latest'}],
                    'states':[{'entity_id':'timer.renamed','state':'idle','attributes':{'friendly_name':'Vorhandener Nachlauf'}},
                              {'entity_id':'update.renamed','state':'on','attributes':{'installed_version':VERSION,
                               'latest_version':'0.1.0-alpha.999','in_progress':False}}]})
                service._connected=service._stream_connected=True
                service._last_refresh_at=datetime.now(UTC).isoformat()
                await service._derive()
            site=web.TCPSite(runner,'127.0.0.1',0)
            await site.start()
            port=site._server.sockets[0].getsockname()[1]
            print(json.dumps({'url':f'http://127.0.0.1:{port}/','version':VERSION}),flush=True)
            while line := await asyncio.to_thread(sys.stdin.readline):
                command=json.loads(line)
                if command.get('action')=='change_zone':
                    zone=(await service.zones.list())[0]
                    definition={k:zone[k] for k in ('name','area_ids','extra_entity_ids','enabled','profile')}
                    definition['name']='Geändert';definition['enabled']=True
                    await service.zones.save(definition,zone['zone_id'],zone['revision'])
                result={'helper_reads':reads,'snapshot_reads':service.client.snapshot.await_count,
                        'automation_reads':service.client.automation_config.await_count,
                        'points':len(list((root/'savepoints').glob('*.json'))),
                        'zones':[] if broken else await service.zones.list(),
                        'broken_unchanged':not broken or (root/'selections.sqlite3').read_bytes()==b'not a SQLite database'}
                print(json.dumps(result),flush=True)
        finally:
            await runner.cleanup()

if __name__=='__main__':asyncio.run(main())
