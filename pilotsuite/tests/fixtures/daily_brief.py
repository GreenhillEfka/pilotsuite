"""Synthetic data seeded through canonical owners; never imported by runtime."""
import copy
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from unittest.mock import AsyncMock

NOW = datetime(2026, 9, 24, 12, tzinfo=UTC).timestamp()
WORLD = {
    'areas': [{'area_id': 'a', 'name': 'Synthetic A'}, {'area_id': 'b', 'name': 'Synthetic B'}],
    'entities': [
        {'entity_id': 'binary_sensor.synthetic', 'area_id': 'a'},
        {'entity_id': 'light.synthetic', 'area_id': 'a'},
        {'entity_id': 'light.other', 'area_id': 'b'}],
    'states': [
        {'entity_id': 'binary_sensor.synthetic', 'state': 'off', 'attributes': {'device_class': 'motion'}},
        {'entity_id': 'light.synthetic', 'state': 'off', 'attributes': {}},
        {'entity_id': 'light.other', 'state': 'off', 'attributes': {}}]}


async def seed(service):
    await service.world.replace(copy.deepcopy(WORLD))
    await service.selections.patch('a', 0, {'binary_sensor.synthetic': 'relevant', 'light.synthetic': 'relevant'})
    await service.context.configure('a', 1, {'presence': ['binary_sensor.synthetic']}, True, now=NOW-12*86400)
    for day in (10, 9, 8, 3, 2, 1):
        for minute in (0, 10):
            stamp = NOW-day*86400+minute*60
            assert await service.context.record('a', 'binary_sensor.synthetic', stamp, 'unknown', now=stamp)
            await service.context.checkpoint('a', 'ready', now=stamp)
    # Transport is simulated, never connected to an actual HA server.
    service._connected = service._stream_connected = True
    service._last_refresh_at = datetime.now(UTC).isoformat()
    await service._derive()
    inventory = await service.selection_inventory('a')
    pattern = (await service.context.report('a'))['patterns'][0]
    draft = await service.plans.create_draft('a', pattern['id'], inventory['revision'], inventory)
    service.client.related_automations = AsyncMock(side_effect=AssertionError('Unexpected HA comparison'))
    service.client.automation_config = AsyncMock(side_effect=AssertionError('Unexpected HA configuration read'))
    return {'pattern_id': pattern['id'], 'draft_id': draft['id']}


def database_snapshot(service):
    with closing(sqlite3.connect(service.selections.path)) as db:
        return '\n'.join(db.iterdump())
