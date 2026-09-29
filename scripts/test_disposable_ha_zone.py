"""Protocol acceptance against an actual, disposable Home Assistant Core.

CI-only. Temporary config and in-memory synthetic observations; no household
credentials, defaults/discovery or installed-system changes. PilotSuite uses its
unmodified HTTP/WS client, durable plans and publisher against real HA APIs.
"""
from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import UTC, datetime
import json
import logging
from pathlib import Path
import tempfile
import time

import os
import sys

from pilotsuite.core.settings import Settings
from pilotsuite.core.zone_presence import DEFAULTS
from pilotsuite.core.zone_presence_store import KEY
from pilotsuite.service import PilotSuiteService


async def wait_state(client, eid, expected):
    """Read-only settling: never replay a mutating command."""
    async with asyncio.timeout(10):
        while True:
            current = (await client.zone_output_states()).get(eid, {}).get('state')
            if current == expected:
                return
            await asyncio.sleep(.1)


async def main():
    logging.basicConfig(level=logging.WARNING)
    with tempfile.TemporaryDirectory(prefix='pilotsuite-actual-ha-') as temp:
        root = Path(temp)
        app_dir = root / 'app'
        app_dir.mkdir()
        child = await asyncio.create_subprocess_exec(
            os.environ['HA_PROTOCOL_PYTHON'],str(Path(__file__).with_name('disposable_ha_fixture.py')),
            stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,
            stderr=None)

        async def receive():
            async with asyncio.timeout(180):
                while line:=await child.stdout.readline():
                    if line.startswith(b'PILOTSUITE_PROTOCOL:'):
                        return json.loads(line[len(b'PILOTSUITE_PROTOCOL:'):])
                raise RuntimeError('Disposable Home Assistant stopped without a response')

        async def fixture(value=None):
            child.stdin.write((json.dumps({'operation':'source','value':value})+'\n').encode())
            await child.stdin.drain()
            assert (await receive()).get('settled') is True

        service = None
        try:
            info=await receive()
            port=info['port'];token=info.pop('token');source_id=info['source']
            service = PilotSuiteService(Settings(app_dir, app_dir/'options.json',
                golden_zone_area_ids=(info['area'],), supervisor_token=token,
                ha_ws_url=f'ws://127.0.0.1:{port}/api/websocket'))
            await service.selections.initialize()
            # The other process owns real HA; no app dependency is replaced or mocked.
            snapshot = await service.client.snapshot()
            await service.world.replace(snapshot)
            await service.zones.bootstrap((info['area'],))
            zone = (await service.zones.list())[0]
            zid = zone['zone_id']
            definition = {k:zone[k] for k in ('name','area_ids','extra_entity_ids','enabled','profile')}
            definition.update(name='Protocol Küche', enabled=True)
            await service.zones.save(definition, zid, zone['revision'])
            inv = await service.selection_inventory(zid)
            await service.selections.patch(zid, inv['revision'], {source_id:'relevant'})
            service._connected = service._stream_connected = True
            service._last_refresh_at = datetime.now(UTC).isoformat()
            spec = deepcopy(DEFAULTS)
            spec.update(grace_seconds=2, clear_seconds=0, sources=[{
                'entity_id':source_id, 'kind':'continuous', 'required':True,
                'max_age':0, 'group':source_id, 'can_start':True, 'active_states':['on']}])

            async def revision():
                return (await service.selection_inventory(zid))['revision']

            async def observe(value=None):
                await fixture(value)
                await service.world.replace(await service.client.snapshot())
                service._last_refresh_at = datetime.now(UTC).isoformat()
                async with service._projection_lock:
                    await service._zone_presence_tick_locked()

            # Missing individual helpers need no PilotSuite presence config and
            # must neither bind a role nor establish occupancy/publication.
            config_before = await service.context.get(zid)
            registry_before = {r['entity_id'] for r in await service.client.zone_output_registry()}
            singles = []
            for role, duration, expected in [('presence_status', None, 'off'),
                                               ('presence_timer', 180, 'idle')]:
                single = await service.zone_package_preview(zid, {
                    'revision':await revision(), 'helper_role':role, 'duration_seconds':duration})
                result = await service.zone_package_apply(zid, single['id'], {
                    'sha256':single['sha256'], 'confirm':True})
                assert result['state']=='verified'
                eid = single['operations'][0]['entity_id']
                await wait_state(service.client, eid, expected)
                if role=='presence_timer':
                    attrs=(await service.client.zone_output_states())[eid]['attributes']
                    assert attrs['duration']=='0:03:00', attrs
                    assert attrs['restore'] is True, attrs
                singles.append(single)
            assert await service.context.get(zid)==config_before
            created_ids={r['entity_id'] for r in await service.client.zone_output_registry()}-registry_before
            assert created_ids=={p['operations'][0]['entity_id'] for p in singles}
            await service.client.close()
            await service.client.start()
            for single in singles:
                repeated=await service.zone_package_apply(zid,single['id'],{
                    'sha256':single['sha256'],'confirm':True})
                assert repeated['write_repeated'] is False
            assert {r['entity_id'] for r in await service.client.zone_output_registry()}-registry_before==created_ids
            print('ok 0 - two individual native helpers, explicit duration/restore, no binding or duplicate after reconnect', flush=True)

            await service.zone_presence_configure(zid, {'revision':await revision(), 'spec':spec, 'mode':'compare'})
            plan = await service.zone_package_preview(zid, {'revision':await revision()})
            applied = await service.zone_package_apply(zid, plan['id'], {'sha256':plan['sha256'], 'confirm':True})
            assert applied['state'] == 'verified', json.dumps(applied, default=str)
            package = (await service.context.get(zid))[KEY]['package']
            e = package['entities']
            assert len(e) == 5
            assert e['sensor']=='binary_sensor.protocol_kueche_anwesenheit'
            public=next(r for r in await service.client.zone_output_registry() if r['entity_id']==e['sensor'])
            assert public['name']=='Protocol Küche Anwesenheit'
            await wait_state(service.client, e['sensor'], 'unavailable')
            print('ok 1 - real storage collections and template config flow create exactly five bound helpers', flush=True)

            await observe('on')
            await service.zone_presence_configure(zid, {'revision':await revision(), 'spec':spec, 'mode':'publish'})
            await observe()
            await service._zone_publish_all()
            await wait_state(service.client, e['sensor'], 'on')
            assert service._zone_views[zid]['publication'] == 'verified'
            await observe('off')
            deadline = service._zone_views[zid]['current']['deadline']
            await service._zone_publish_all()
            await wait_state(service.client, e['nachlauf'], 'active')
            await asyncio.sleep(max(0, deadline-time.time())+.25)
            await observe()
            await service._zone_publish_all()
            await wait_state(service.client, e['sensor'], 'off')
            print('ok 2 - real publisher: occupied, timer, grace expiry and public off', flush=True)

            await observe('on')
            await service._zone_publish_all()
            await wait_state(service.client, e['sensor'], 'on')
            await observe('unavailable')
            await service._zone_publish_all()
            await wait_state(service.client, e['sensor'], 'unavailable')
            assert (await service.client.zone_output_states())[e['anwesenheit_intern']]['state'] == 'on'
            print('ok 3 - input outage invalidates public sensor without false owner.off', flush=True)

            # Real labels/metadata; restoration uses the existing explicit inverse plan.
            for label in ('Protocol Room','Habitus Übersicht','Habitus Diagnose'):
                await service.client.zone_create_label(label)
            labels = await service.client.zone_labels()
            zone_label = next(l['label_id'] for l in labels if l['name']=='Protocol Room')
            before = next(r for r in await service.client.zone_output_registry() if r['entity_id']==source_id)
            op = await service.ontology_preview(zid, {'revision':await revision(), 'entity_id':source_id,
                'name':'Protocol · Presence', 'zone_label':zone_label, 'roles':['Habitus Übersicht'], 'target_entity_id':None})
            result = await service.ontology_apply(zid,op['id'],{'sha256':op['sha256'],'confirm':True})
            assert result['state'] == 'verified'
            inverse = await service.ontology_restore_preview(zid,op['id'],{'revision':await revision()})
            result = await service.ontology_apply(zid,inverse['id'],{'sha256':inverse['sha256'],'confirm':True})
            assert result['state'] == 'verified'
            after = next(r for r in await service.client.zone_output_registry() if r['entity_id']==source_id)
            assert (before['name'], before['labels']) == (after['name'], after['labels'])
            print('ok 4 - real name/label application and explicit rollback preserve registry identity', flush=True)

            # A real client restart preserves the existing native helper identities.
            identities = deepcopy(package['identities'])
            await service.client.close()
            await service.client.start()
            rows = {r['entity_id']:r for r in await service.client.zone_output_registry()}
            from pilotsuite.core.organization import same_identity
            assert all(same_identity(identities[k], rows[v]) for k,v in e.items())
            assert not (await service.context.get(zid))['learning']
            print('ok 5 - reconnect preserves identity and learning remains unchanged', flush=True)
            print(json.dumps({'actual_homeassistant': info['version'], 'tests':6,
                'scope':'disposable Core APIs, not household or Supervisor principal attestation'}), flush=True)
        finally:
            if service is not None:
                await service.client.close()
            if child.returncode is None:
                child.stdin.write(b'{"operation":"stop"}\n')
                await child.stdin.drain()
                child.stdin.close()
                try:
                    await asyncio.wait_for(child.wait(),timeout=30)
                except TimeoutError:
                    child.terminate()
                    await asyncio.wait_for(child.wait(),timeout=10)


if __name__ == '__main__':
    asyncio.run(main())
