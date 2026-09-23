"""Deterministic queued feedback races using synthetic evidence only."""
import sqlite3
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from pilotsuite.core.context import ContextStore, RETENTION
from pilotsuite.core.selections import InvalidSelection, SelectionStore
from pilotsuite.core.zones import ZoneStore


class FeedbackAtomicityTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.selections = SelectionStore(Path(temp.name))
        await self.selections.initialize()
        await ZoneStore(self.selections).bootstrap(('synthetic',))
        self.store = ContextStore(self.selections)
        self.now = datetime(2026, 9, 23, 12, tzinfo=UTC).timestamp()
        self.clock = patch('pilotsuite.core.context.time.time', side_effect=lambda: self.now)
        self.clock.start()
        self.addCleanup(self.clock.stop)
        self.roles = {'presence': ['binary_sensor.synthetic']}
        await self.selections.patch('synthetic', 0, {'binary_sensor.synthetic': 'relevant'})
        await self.store.configure('synthetic', 1, self.roles, True, now=self.now-4*86400)
        for day in (3, 2, 1):
            for minute in (0, 10):
                stamp = self.now-day*86400+minute*60
                self.assertTrue(await self.store.record('synthetic', 'binary_sensor.synthetic', stamp, 'unknown', now=stamp))
        self.before = await self.store.report('synthetic')
        self.pattern = self.before['patterns'][0]['id']

    async def reject_queued_feedback(self, change):
        save = self.store._feedback
        def queued(*args):
            # A queued worker must validate current state, not an earlier report.
            change()
            return save(*args)
        with patch.object(self.store, '_feedback', side_effect=queued):
            with self.assertRaisesRegex(InvalidSelection, 'expired or unknown'):
                await self.store.feedback('synthetic', self.pattern, 'accepted')
        with sqlite3.connect(self.store.path) as db:
            self.assertEqual([], db.execute('SELECT * FROM pattern_feedback').fetchall())

    def configure_sync(self, *, roles=None, reset=False, detector=None):
        return self.store._configure('synthetic', 2, self.roles if roles is None else roles,
                                     False, reset, self.now, detector, None)

    async def test_queued_feedback_cannot_reappear_after_reset(self):
        await self.reject_queued_feedback(lambda: self.configure_sync(reset=True))
        self.assertEqual(0, (await self.store.report('synthetic'))['event_count'])

    async def test_queued_feedback_rechecks_changed_sources(self):
        await self.reject_queued_feedback(lambda: self.configure_sync(roles={}))

    async def test_queued_feedback_rechecks_changed_detector(self):
        await self.reject_queued_feedback(lambda: self.configure_sync(detector={'min_events': 10, 'min_days': 3}))
        self.assertEqual(self.before['evidence'], (await self.store.report('synthetic'))['evidence'])

    async def test_queued_feedback_rechecks_retention_at_write_time(self):
        def expire():
            self.now += RETENTION
        await self.reject_queued_feedback(expire)

    async def test_retained_pattern_feedback_survives_restart_with_learning_off(self):
        self.configure_sync()
        before = await self.store.report('synthetic')
        await self.store.feedback('synthetic', self.pattern, 'later')
        after = await ContextStore(self.selections).report('synthetic')
        self.assertEqual('later', after['patterns'][0]['preference'])
        for key in ('evidence', 'event_count', 'reobservation'):
            self.assertEqual(before[key], after[key])
        for key in ('statistics', 'rule_strength', 'confidence', 'risk'):
            self.assertEqual(before['patterns'][0][key], after['patterns'][0][key])

    async def test_competing_writer_cannot_reset_between_validation_and_save(self):
        project = self.store._report_in_transaction
        checked = []
        def projected(db, zone, now):
            report = project(db, zone, now)
            # Deterministic second SQLite writer at the former race boundary.
            with sqlite3.connect(self.store.path, timeout=0) as competing:
                with self.assertRaisesRegex(sqlite3.OperationalError, 'locked'):
                    competing.execute('DELETE FROM activity_evidence WHERE zone_id=?', (zone,))
            checked.append(True)
            return report
        with patch.object(self.store, '_report_in_transaction', side_effect=projected):
            await self.store.feedback('synthetic', self.pattern, 'accepted')
        self.assertEqual([True], checked)
        after = await self.store.report('synthetic')
        self.assertEqual(self.before['evidence'], after['evidence'])
        self.assertEqual('accepted', after['patterns'][0]['preference'])
