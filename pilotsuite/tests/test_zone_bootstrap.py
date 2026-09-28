"""Bootstrap contention and durability checks against disposable real SQLite files."""
import asyncio
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from pilotsuite.core.context import ContextStore
from pilotsuite.core.selections import SelectionStore
from pilotsuite.core.zones import ZoneStore


MARKER = "SELECT 1 FROM zone_meta WHERE key='bootstrapped'"


class ZoneBootstrapTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.selections = SelectionStore(Path(self.temp.name))
        await self.selections.initialize()
        self.zones = ZoneStore(self.selections)

    def dump(self):
        with closing(sqlite3.connect(self.selections.path)) as db:
            return '\n'.join(db.iterdump())

    async def test_existing_marker_needs_no_write_transaction_and_preserves_four_zones(self):
        await self.zones.bootstrap(('one', 'two', 'three', 'four'))
        await self.selections.patch('one', 0, {'binary_sensor.synthetic': 'relevant'})
        context = ContextStore(self.selections)
        await context.configure('one', 1, {'presence': ['binary_sensor.synthetic']}, False)
        await context.save_zone_operational('one', 2, {'checkpoint': {'evaluated_at': 100}})
        before = self.dump()
        statements = []
        connect = sqlite3.connect

        def observed(*args, **kwargs):
            db = connect(*args, **kwargs)
            db.set_trace_callback(statements.append)
            return db

        with patch('sqlite3.connect', side_effect=observed):
            for _ in range(5):
                await self.zones.bootstrap(('changed_options_must_not_add_a_zone',))
        self.assertEqual(before, self.dump())
        self.assertFalse(any(sql.startswith('BEGIN IMMEDIATE') for sql in statements))
        self.assertFalse(any(sql.startswith(('INSERT', 'UPDATE', 'DELETE')) for sql in statements))
        self.assertEqual(4, len(await self.zones.list()))

    async def test_existing_marker_can_be_read_beside_a_reserved_writer(self):
        await self.zones.bootstrap(('one',))
        connect = sqlite3.connect

        def short_timeout(*args, **kwargs):
            return connect(*args, **dict(kwargs, timeout=0.01))

        with closing(connect(self.selections.path)) as writer, writer:
            writer.execute('BEGIN IMMEDIATE')
            with patch('sqlite3.connect', side_effect=short_timeout):
                await self.zones.bootstrap(('must_not_be_added',))
        self.assertEqual(['one'], [zone['zone_id'] for zone in await self.zones.list()])

    async def test_concurrent_first_reads_recheck_marker_under_transaction(self):
        connect = sqlite3.connect
        barrier = threading.Barrier(2)

        class SimultaneousRead(sqlite3.Connection):
            def execute(self, sql, *args, **kwargs):
                cursor = super().execute(sql, *args, **kwargs)
                if sql == MARKER and not self.in_transaction:
                    result = cursor.fetchone()
                    barrier.wait(timeout=3)
                    return SimpleNamespace(fetchone=lambda: result)
                return cursor

        def competing(*args, **kwargs):
            return connect(*args, **dict(kwargs, factory=SimultaneousRead))

        with patch('sqlite3.connect', side_effect=competing):
            await asyncio.gather(self.zones.bootstrap(('one',)),
                                 ZoneStore(self.selections).bootstrap(('two',)))
        result = await self.zones.list()
        self.assertEqual(1, len(result))
        self.assertIn(result[0]['zone_id'], ('one', 'two'))

    async def test_failed_initial_bootstrap_rolls_back_before_retry(self):
        connect = sqlite3.connect

        class FailSecondZone(sqlite3.Connection):
            inserts = 0

            def execute(self, sql, *args, **kwargs):
                if sql.startswith('INSERT OR IGNORE INTO habitus_zones'):
                    self.inserts += 1
                    if self.inserts == 2:
                        raise sqlite3.OperationalError('synthetic interrupted bootstrap')
                return super().execute(sql, *args, **kwargs)

        def failing(*args, **kwargs):
            return connect(*args, **dict(kwargs, factory=FailSecondZone))

        with patch('sqlite3.connect', side_effect=failing), self.assertRaises(sqlite3.OperationalError):
            await self.zones.bootstrap(('one', 'two', 'three', 'four'))
        self.assertEqual([], await self.zones.list())
        with closing(connect(self.selections.path)) as db:
            self.assertIsNone(db.execute(MARKER).fetchone())
        await self.zones.bootstrap(('one', 'two', 'three', 'four'))
        self.assertEqual(4, len(await self.zones.list()))

    async def test_marker_is_read_from_restored_storage_not_cached_in_memory(self):
        await self.zones.bootstrap(('one',))
        with closing(sqlite3.connect(self.selections.path)) as db, db:
            db.execute("DELETE FROM zone_meta WHERE key='bootstrapped'")
        await self.zones.bootstrap(('two',))
        self.assertEqual(['one', 'two'], [zone['zone_id'] for zone in await self.zones.list()])
        await ZoneStore(self.selections).bootstrap(('ignored_after_restart',))
        self.assertEqual(['one', 'two'], [zone['zone_id'] for zone in await self.zones.list()])


if __name__ == '__main__':
    unittest.main()
