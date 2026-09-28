"""Operational checkpoint contention/durability against disposable SQLite only."""
import asyncio
from contextlib import closing
from copy import deepcopy
from pathlib import Path
import sqlite3
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from pilotsuite.core.context import ContextStore
from pilotsuite.core.selections import InvalidSelection, SelectionConflict, SelectionStore
from pilotsuite.core.zones import ZoneStore


class ZoneOperationalStoreTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.selections = SelectionStore(Path(self.temp.name))
        await self.selections.initialize()
        self.zones = ZoneStore(self.selections)
        await self.zones.bootstrap(('one', 'two', 'three', 'four'))
        await self.selections.patch('one', 0, {'binary_sensor.synthetic': 'relevant'})
        self.context = ContextStore(self.selections)
        await self.context.configure('one', 1, {'presence': ['binary_sensor.synthetic']}, False)
        self.value = {'checkpoint': {'evaluated_at': 100, 'deadline': 130},
                      'session': 'synthetic', 'suspended': 'source_basis_changed'}
        await self.context.save_zone_operational('one', 2, self.value)

    def dump(self):
        with closing(sqlite3.connect(self.selections.path)) as db:
            return '\n'.join(db.iterdump())

    async def test_identical_checkpoint_needs_no_write_reservation_and_preserves_database(self):
        before = self.dump()
        statements = []
        connect = sqlite3.connect

        def observed(*args, **kwargs):
            db = connect(*args, **kwargs)
            db.set_trace_callback(statements.append)
            return db

        with patch('sqlite3.connect', side_effect=observed):
            for _ in range(5):
                await self.context.save_zone_operational('one', 2, self.value)
        self.assertFalse(any(sql == 'BEGIN IMMEDIATE' for sql in statements))
        self.assertFalse(any(sql.startswith(('INSERT', 'UPDATE', 'DELETE')) for sql in statements))
        self.assertEqual(before, self.dump())

    async def test_identical_checkpoint_succeeds_beside_a_reserved_writer(self):
        connect = sqlite3.connect

        def short_timeout(*args, **kwargs):
            return connect(*args, **dict(kwargs, timeout=0.01))

        with closing(connect(self.selections.path)) as writer, writer:
            writer.execute('BEGIN IMMEDIATE')
            with patch('sqlite3.connect', side_effect=short_timeout):
                await self.context.save_zone_operational('one', 2, self.value)
        self.assertEqual(self.value, await self.context.zone_operational('one'))

    async def test_identical_value_does_not_bypass_zone_or_revision_validation(self):
        await self.context.save_zone_operational('two', 0, self.value)
        await self.selections.patch('three', 0, {'binary_sensor.synthetic': 'relevant'})
        await self.context.save_zone_operational('three', 1, self.value)
        before = self.dump()
        for zid, revision, error in (('one', 1, SelectionConflict), ('one', True, InvalidSelection),
                                    ('one', -1, InvalidSelection), ('missing', 2, InvalidSelection),
                                    ('two', False, InvalidSelection), ('three', True, InvalidSelection)):
            with self.subTest(zid=zid, revision=revision), self.assertRaises(error):
                await self.context.save_zone_operational(zid, revision, self.value)
        self.assertEqual(before, self.dump())

    async def test_changed_clock_is_still_durable_and_read_back_after_restart(self):
        value = deepcopy(self.value)
        value['checkpoint']['evaluated_at'] = 101
        await self.context.save_zone_operational('one', 2, value)
        self.assertEqual(value, await ContextStore(self.selections).zone_operational('one'))
        # Read the actual durable row, not a process-local deduplication cache.
        with closing(sqlite3.connect(self.selections.path)) as db, db:
            db.execute('DELETE FROM zone_meta WHERE key=?', ('zone_presence_state:one',))
        await self.context.save_zone_operational('one', 2, value)
        self.assertEqual(value, await self.context.zone_operational('one'))

    async def test_concurrent_equal_changes_recheck_value_under_write_lock(self):
        connect = sqlite3.connect
        barrier = threading.Barrier(2)
        writes = []
        reads = []
        value = {**self.value, 'suspended': 'configuration_changed'}

        class SimultaneousRead(sqlite3.Connection):
            def execute(self, sql, *args, **kwargs):
                cursor = super().execute(sql, *args, **kwargs)
                if 'LEFT JOIN zone_meta' in sql and not self.in_transaction:
                    result = cursor.fetchone()
                    reads.append(result)
                    barrier.wait(timeout=3)
                    return SimpleNamespace(fetchone=lambda: result)
                if sql.startswith('INSERT OR REPLACE INTO zone_meta'):
                    writes.append(sql)
                return cursor

        def competing(*args, **kwargs):
            return connect(*args, **dict(kwargs, factory=SimultaneousRead))

        with patch('sqlite3.connect', side_effect=competing):
            await asyncio.gather(self.context.save_zone_operational('one', 2, value),
                                 ContextStore(self.selections).save_zone_operational('one', 2, value))
        self.assertEqual(1, len(writes))
        self.assertEqual(2, len(reads))
        self.assertEqual(value, await self.context.zone_operational('one'))

    async def test_revision_change_before_write_reservation_cannot_be_overwritten(self):
        connect = sqlite3.connect
        fired = False
        value = {**self.value, 'suspended': 'configuration_changed'}

        class ConcurrentEdit(sqlite3.Connection):
            def execute(db, sql, *args, **kwargs):
                nonlocal fired
                if sql == 'BEGIN IMMEDIATE' and not fired:
                    fired = True
                    with closing(connect(self.selections.path)) as writer, writer:
                        writer.execute('UPDATE zones SET revision=3 WHERE zone_id=?', ('one',))
                        writer.execute('DELETE FROM zone_meta WHERE key=?', ('zone_presence_state:one',))
                return super().execute(sql, *args, **kwargs)

        def competing(*args, **kwargs):
            return connect(*args, **dict(kwargs, factory=ConcurrentEdit))

        with patch('sqlite3.connect', side_effect=competing), self.assertRaises(SelectionConflict):
            await self.context.save_zone_operational('one', 2, value)
        self.assertTrue(fired)
        self.assertEqual({}, await self.context.zone_operational('one'))

    async def test_failed_changed_write_rolls_back_and_can_be_retried(self):
        connect = sqlite3.connect
        value = {**self.value, 'suspended': 'configuration_changed'}

        class FailedWrite(sqlite3.Connection):
            def execute(self, sql, *args, **kwargs):
                result = super().execute(sql, *args, **kwargs)
                if sql.startswith('INSERT OR REPLACE INTO zone_meta'):
                    raise sqlite3.OperationalError('synthetic interruption before commit')
                return result

        def failing(*args, **kwargs):
            return connect(*args, **dict(kwargs, factory=FailedWrite))

        with patch('sqlite3.connect', side_effect=failing), self.assertRaises(sqlite3.OperationalError):
            await self.context.save_zone_operational('one', 2, value)
        self.assertEqual(self.value, await self.context.zone_operational('one'))
        await self.context.save_zone_operational('one', 2, value)
        self.assertEqual(value, await self.context.zone_operational('one'))


if __name__ == '__main__':
    unittest.main()
