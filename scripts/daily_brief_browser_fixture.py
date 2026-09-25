"""Disposable actual-app server controlled via stdin, never via an HTTP backdoor."""
from __future__ import annotations
import asyncio
from datetime import UTC, datetime
import json
import logging
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

from aiohttp import web
from pilotsuite.app import create_app, SERVICE_KEY
from pilotsuite.core.settings import Settings

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'pilotsuite'/'tests'))
from daily_brief_support import seed_daily_brief, fixture_control


async def main():
    logging.basicConfig(level=logging.ERROR, stream=sys.stderr)
    with tempfile.TemporaryDirectory(prefix='daily-brief-browser-') as temp:
        root = Path(temp)
        app = create_app(Settings(root, root/'options.json', golden_zone_area_ids=('a', 'b'),
            supervisor_token='', refresh_interval_seconds=3600, ingress_allowed_peers=('127.0.0.1',)))
        runner = web.AppRunner(app)
        await runner.setup()
        try:
            now = datetime(2026, 9, 24, 18, tzinfo=UTC).timestamp()
            with patch('time.time', return_value=now):
                service = app[SERVICE_KEY]
                fixture = await seed_daily_brief(service, now)
                url = None
                # Separate component-test mode: no HTTP server, no browser network.
                if '--stdio-only' not in sys.argv:
                    site = web.TCPSite(runner, '127.0.0.1', 0)
                    await site.start()
                    port = site._server.sockets[0].getsockname()[1]
                    url = f'http://127.0.0.1:{port}/' + ('' if '--workspace' in sys.argv else '#ps-all')
                print(json.dumps({'url': url, 'pattern_id': fixture['pattern_id']}), flush=True)
                while line := await asyncio.to_thread(sys.stdin.readline):
                    result = await fixture_control(service, fixture, json.loads(line))
                    print(json.dumps(result), flush=True)
        finally:
            await runner.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
