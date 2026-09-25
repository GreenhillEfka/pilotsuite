"""Actual app with synthetic canonical stores; stdin controls are test-only."""
import asyncio
import copy
import hashlib
import json
import logging
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
from aiohttp import web
from pilotsuite.app import SERVICE_KEY, create_app
from pilotsuite.core.settings import Settings

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'pilotsuite'/'tests'))
from fixtures.daily_brief import NOW, WORLD, database_snapshot, seed


async def main():
    logging.basicConfig(level=logging.ERROR, stream=sys.stderr)
    with tempfile.TemporaryDirectory(prefix='pilotsuite-brief-browser-') as directory:
        root = Path(directory)
        app = create_app(Settings(root, root/'options.json', golden_zone_area_ids=('a', 'b'),
            supervisor_token='', refresh_interval_seconds=3600, ingress_allowed_peers=('127.0.0.1',)))
        runner = web.AppRunner(app); await runner.setup()
        service = app[SERVICE_KEY]
        clock = patch('time.time', return_value=NOW); clock.start()
        try:
            info = await seed(service)
            site = web.TCPSite(runner, '127.0.0.1', 0); await site.start()
            port = site._server.sockets[0].getsockname()[1]
            print(json.dumps(dict(info, url=f'http://127.0.0.1:{port}/')), flush=True)
            while line := await asyncio.to_thread(sys.stdin.readline):
                command = json.loads(line)
                action = command['action']
                if action == 'snapshot':
                    result = {'database': hashlib.sha256(database_snapshot(service).encode()).hexdigest(),
                        'related_reads': service.client.related_automations.await_count,
                        'config_reads': service.client.automation_config.await_count}
                elif action == 'connection':
                    assert type(command['connected']) is bool
                    service._stream_connected = command['connected']
                    result = {'changed': True}
                elif action == 'source_state':
                    assert command['state'] in ('off', 'unavailable')
                    world = copy.deepcopy(WORLD); world['states'][0]['state'] = command['state']
                    await service.world.replace(world); await service._derive()
                    result = {'changed': True}
                elif action == 'feedback':
                    await service.context.feedback('a', info['pattern_id'], command['decision'])
                    result = {'changed': True}
                else:
                    raise ValueError('Unsupported synthetic fixture command')
                print(json.dumps(result), flush=True)
        finally:
            clock.stop(); await runner.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
