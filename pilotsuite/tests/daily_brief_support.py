"""Synthetic canonical-owner setup shared by HTTP and full-shell browser tests.

Never imported by production modules; no credentials, HA calls or house data.
"""
from __future__ import annotations

from contextlib import closing
from copy import deepcopy
from datetime import UTC, datetime
import hashlib
import json
import sqlite3
from unittest.mock import AsyncMock


async def seed_daily_brief(service, now: float) -> dict:
    world = {
        'areas': [{'area_id': 'a', 'name': 'Synthetic A'}, {'area_id': 'b', 'name': 'Synthetic B'}],
        'devices': [],
        'entities': [{'entity_id': 'binary_sensor.synthetic', 'area_id': 'a'},
                     {'entity_id': 'light.synthetic', 'area_id': 'a'},
                     {'entity_id': 'light.other', 'area_id': 'b'}],
        'states': [{'entity_id': 'binary_sensor.synthetic', 'state': 'off',
                    'attributes': {'device_class': 'motion'}},
                   {'entity_id': 'light.synthetic', 'state': 'off', 'attributes': {}},
                   {'entity_id': 'light.other', 'state': 'off', 'attributes': {}}],
    }
    await service.world.replace(deepcopy(world))
    service._connected = service._stream_connected = True
    service._last_refresh_at = datetime.now(UTC).isoformat()
    service._last_error = None
    await service.selections.patch('a', 0, {'binary_sensor.synthetic': 'relevant', 'light.synthetic': 'relevant'})
    await service.context.configure('a', 1, {'presence': ['binary_sensor.synthetic']}, True, now=now-12*86400)
    for day in (10, 9, 8, 3, 2, 1):
        for minute in (0, 10):
            occurred = now-day*86400+minute*60-3600
            await service.context.record('a', 'binary_sensor.synthetic', occurred, 'unknown', now=occurred)
            await service.context.checkpoint('a', 'ready', now=occurred)
    await service._derive()
    service.client.related_automations = AsyncMock(side_effect=AssertionError('Unexpected HA lookup'))
    service.client.automation_config = AsyncMock(side_effect=AssertionError('Unexpected HA config read'))
    service.client.snapshot = AsyncMock(side_effect=AssertionError('Unexpected HA snapshot'))
    patterns = (await service.context.report('a'))['patterns']
    assert len(patterns) == 1
    return {'world': world, 'pattern_id': patterns[0]['id'], 'now': now}


def stored_digest(service) -> str:
    """Check every table, not only the derived brief; close read connections."""
    with closing(sqlite3.connect(service.selections.path)) as db:
        source = '\n'.join(db.iterdump()).encode()
    return hashlib.sha256(source).hexdigest()


async def fixture_control(service, fixture: dict, command: dict) -> dict:
    """Only stdin/API-test controls, not an application endpoint."""
    action = command['action']
    if action == 'projection':
        from pilotsuite.app import _context_payload
        zone_id = command.get('zone_id', 'a')
        if zone_id not in ('a', 'b'):
            raise ValueError('Unknown synthetic zone')
        async with service._projection_lock:
            return {'inventory': await service.selection_inventory(zone_id),
                    'report': await _context_payload(service, zone_id)}
    if action == 'snapshot':
        return {'database_sha256': stored_digest(service),
                'related_reads': service.client.related_automations.await_count,
                'config_reads': service.client.automation_config.await_count,
                'snapshot_reads': service.client.snapshot.await_count}
    if action == 'feedback':
        await service.context.feedback('a', fixture['pattern_id'], command['decision'])
    elif action == 'connection':
        service._stream_connected = command['ready']
        await service._derive()
    elif action == 'source':
        world = deepcopy(fixture['world'])
        world['states'][0]['state'] = command['state']
        await service.world.replace(world)
        await service._derive()
    elif action == 'learning':
        inventory = await service.selection_inventory('a')
        config = await service.context.get('a')
        await service.context.configure('a', inventory['revision'], config['roles'], command['enabled'])
        await service._derive()
    elif action == 'pause':
        current = next(z for z in await service.zones.list() if z['zone_id'] == 'a')
        definition = {key: current[key] for key in ('name', 'area_ids', 'extra_entity_ids', 'enabled', 'profile')}
        definition['enabled'] = False
        await service.zones.save(definition, 'a', current['revision'])
        await service._derive()
    else:
        raise ValueError('Unknown synthetic fixture command')
    return {'changed': True}
