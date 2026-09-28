#!/usr/bin/env python3
"""Bounded synthetic tick + view baseline; no household credentials or HA operations.

Run with the repository's Python dependencies and PYTHONPATH=pilotsuite. Reuses the
existing disposable full-app test fixture. Counts are deterministic workload facts;
wall times depend on this host and include instrumentation, not household latency.
"""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import sqlite3
import statistics
import sys
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'pilotsuite' / 'tests'))
from test_zone_presence_runtime import MOTION, SOURCE, ZonePresenceRuntimeTests


async def measure(cycles):
    fixture = ZonePresenceRuntimeTests('test_current_publication_and_heartbeat_throttle_still_work')
    await fixture.asyncSetUp()
    connect = sqlite3.connect
    counts = {'connections': 0, 'checkpoint_writes': 0, 'immediate_transactions': 0,
              'select_statements': 0}

    def trace(sql):
        if sql.startswith('INSERT OR REPLACE INTO zone_meta') and 'zone_presence_state:' in sql:
            counts['checkpoint_writes'] += 1
        if sql == 'BEGIN IMMEDIATE':
            counts['immediate_transactions'] += 1
        if sql.startswith('SELECT'):
            counts['select_statements'] += 1

    def observed_connect(*args, **kwargs):
        counts['connections'] += 1
        db = connect(*args, **kwargs)
        db.set_trace_callback(trace)
        return db

    try:
        for label, values in [('occupied', {SOURCE: 'on', MOTION: 'off'}),
                              ('vacant', {SOURCE: 'off', MOTION: 'off'}),
                              ('unknown', {SOURCE: 'unavailable', MOTION: 'unavailable'}),
                              ('suspended', {SOURCE: 'off', MOTION: 'off'})]:
            await fixture.tick(1, values)
            await fixture.tick(40)
            if label == 'suspended':
                next(row for row in fixture.world['entities'] if row['entity_id'] == SOURCE)['unique_id'] += '_replacement'
                await fixture.tick(1)
            for key in counts:
                counts[key] = 0
            durations = []
            decisions = []
            with patch('sqlite3.connect', side_effect=observed_connect):
                for _ in range(cycles):
                    start = time.perf_counter()
                    result = await fixture.tick(5)
                    durations.append((time.perf_counter() - start) * 1000)
                    decisions.append({'current': result['current'], 'status': result['status']})
            if label == 'suspended':
                assert result['current'] is None and result['status'] == 'source_basis_changed'
            else:
                assert result['current']['state'] == label
            fixture.service.client.history.assert_not_awaited()
            fixture.service.client.zone_output_service.assert_not_awaited()
            print(json.dumps({'synthetic_only': True, 'zones': 1, 'scenario': label,
                'cycles': cycles, **counts,
                'final_state': result['current']['state'] if result['current'] else None,
                'final_status': result['status'],
                'decision_trace_sha256': hashlib.sha256(json.dumps(decisions, sort_keys=True).encode()).hexdigest(),
                'tick_and_view_ms_median': round(statistics.median(durations), 3),
                'tick_and_view_ms_p95': round(sorted(durations)[max(0, (95 * cycles + 99) // 100 - 1)], 3),
                'history_requests': 0, 'ha_output_calls': 0}), flush=True)
    finally:
        await fixture.asyncTearDown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cycles', type=int, default=60)
    args = parser.parse_args()
    if not 1 <= args.cycles <= 600:
        parser.error('--cycles must be between 1 and 600')
    asyncio.run(measure(args.cycles))
