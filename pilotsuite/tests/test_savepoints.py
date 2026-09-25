"""Actual SQLite/file recovery, including failure, concurrency and replay boundaries."""
import asyncio
import json
import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from pilotsuite.core.audit import AuditLog
from pilotsuite.core.context import ContextStore
from pilotsuite.core.plans import PlanStore
from pilotsuite.core.savepoints import MAX_POINTS, capture, digest
from pilotsuite.core.selections import InvalidSelection, SelectionConflict, SelectionStore
from pilotsuite.core.zones import ZoneStore


class SavepointTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.selections = SelectionStore(self.root)
        await self.selections.initialize()
        self.zones = ZoneStore(self.selections); await self.zones.bootstrap(['a'])
        self.context = ContextStore(self.selections)
        self.plans = PlanStore(self.root, AuditLog(self.root, 100), self.context)
        await self.selections.patch('a', 0, {'binary_sensor.p': 'relevant'})
        await self.context.configure('a', 1, {'presence': ['binary_sensor.p']}, True)

    def state(self):
        with closing(sqlite3.connect(self.selections.path)) as db, db:
            return capture(db)

    async def point(self):
        return await self.plans.create_savepoint('Vor Rollenänderung')

    async def restore(self, point, preview=None):
        preview = preview or await self.plans.preview_restore(point['id'])
        return await self.plans.restore_savepoint(point['id'], {
            'sha256': preview['sha256'], 'basis': preview['basis'], 'confirm_paused_restore': True})

    async def test_real_file_has_checksum_permissions_and_excludes_secrets_evidence_consents(self):
        before = self.state(); point = await self.point()
        self.assertEqual(before, self.state())
        file = self.root/'savepoints'/f"{point['id']}.json"
        payload = json.loads(file.read_text()); expected=payload.pop('sha256')
        self.assertEqual(expected, digest(payload))
        self.assertEqual(0o600, file.stat().st_mode & 0o777)
        self.assertEqual({'zone_id','revision','definition','decisions','roles','detector'}, set(payload['zones'][0]))
        self.assertNotIn('consented_at', file.read_text())
        self.assertEqual(1, len(await self.plans.savepoints()))

    async def test_restore_pauses_without_replaying_learning_or_deleting_new_zones(self):
        point=await self.point()
        zone=(await self.zones.list())[0]
        await self.zones.save({k:v for k,v in zone.items() if k not in {'zone_id','revision'}} | {'name':'changed'},'a',zone['revision'])
        extra=await self.zones.save({'name':'Newer zone','area_ids':['b'],'extra_entity_ids':[], 'enabled':False,'profile':'observe'})
        preview=await self.plans.preview_restore(point['id']); self.assertEqual(1,preview['preserved_zone_count'])
        result=await self.restore(point,preview)
        data={z['zone_id']:z for z in await self.zones.list()}
        self.assertEqual('a',data['a']['name']);self.assertFalse(data['a']['enabled'])
        self.assertIn(extra['zone_id'],data)
        self.assertFalse((await self.context.get('a'))['learning'])
        self.assertIsNone((await self.context.get('a'))['consented_at'])
        self.assertEqual(2,len(await self.plans.savepoints()))
        self.assertNotEqual(point['id'],result['before_savepoint'])
        self.assertGreater(data['a']['revision'],zone['revision'])

    async def test_preview_is_not_a_restore_or_file_write(self):
        point=await self.point();before=self.state();count=len(await self.plans.savepoints())
        preview=await self.plans.preview_restore(point['id'])
        self.assertFalse(preview['ha_execution']);self.assertEqual(before,self.state())
        self.assertEqual(count,len(await self.plans.savepoints()))

    async def test_stale_revision_refuses_before_creating_a_before_point(self):
        point=await self.point();preview=await self.plans.preview_restore(point['id'])
        state=await self.selections.get('a')
        await self.selections.patch('a',state['revision'],{'sensor.new':'ignored'})
        before=self.state()
        with self.assertRaises(SelectionConflict):await self.restore(point,preview)
        self.assertEqual(before,self.state());self.assertEqual(1,len(await self.plans.savepoints()))

    async def test_successful_restore_receipt_is_idempotent(self):
        point=await self.point();preview=await self.plans.preview_restore(point['id'])
        result=await self.restore(point,preview);before=self.state()
        again=await self.restore(point,preview)
        self.assertTrue(again['replayed']);self.assertEqual(result['before_savepoint'],again['before_savepoint'])
        self.assertEqual(before,self.state());self.assertEqual(2,len(await self.plans.savepoints()))

    async def test_before_point_disk_failure_prevents_database_change(self):
        point=await self.point();before=self.state()
        with patch.object(self.plans,'_write_point',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):await self.restore(point)
        self.assertEqual(before,self.state())

    async def test_database_failure_rolls_back_and_preserves_before_point(self):
        point=await self.point();before=self.state()
        with patch.object(self.selections,'prune_journal',side_effect=RuntimeError('synthetic commit boundary')):
            with self.assertRaises(RuntimeError):await self.restore(point)
        self.assertEqual(before,self.state());self.assertEqual(2,len(await self.plans.savepoints()))
        self.assertFalse((await self.restore(point))['replayed'])

    async def test_point_corruption_rejected_and_reported_not_silently_hidden(self):
        point=await self.point();file=self.root/'savepoints'/f"{point['id']}.json"
        file.write_text(file.read_text().replace('Vor Rollenänderung','tampered'))
        with self.assertRaises(InvalidSelection):await self.plans.preview_restore(point['id'])
        self.assertFalse((await self.plans.savepoints())[0]['valid'])

    async def test_path_traversal_and_symlink_are_not_read(self):
        point=await self.point()
        for bad in ('../selections.sqlite3','../../secret','x','',None):
            with self.subTest(bad=bad), self.assertRaises(InvalidSelection):await self.plans.preview_restore(bad)
        path=self.root/'savepoints'/f"{point['id']}.json";path.unlink();path.symlink_to(self.selections.path)
        with self.assertRaises(InvalidSelection):await self.plans.preview_restore(point['id'])

    async def test_confirmation_must_be_exact_and_hashed(self):
        point=await self.point();preview=await self.plans.preview_restore(point['id'])
        for flag in (False,1,'true',None):
            with self.subTest(flag=flag),self.assertRaises(InvalidSelection):
                await self.plans.restore_savepoint(point['id'],{'sha256':preview['sha256'],'basis':preview['basis'],'confirm_paused_restore':flag})

    async def test_no_automatic_deletion_on_limit(self):
        point=await self.point();before=self.state()
        with patch.object(self.plans,'_point_paths',return_value=[Path('x')]*MAX_POINTS):
            with self.assertRaises(InvalidSelection):await self.point()
        self.assertEqual(before,self.state());self.assertTrue((await self.plans.savepoints())[0]['valid'])

    async def test_reinitializing_with_other_start_areas_does_not_rewrite_zones(self):
        before=self.state();await self.zones.bootstrap(['different'])
        self.assertEqual(before,self.state())

    async def test_evidence_and_review_content_are_not_exported_or_restored(self):
        with closing(sqlite3.connect(self.selections.path)) as db, db:
            db.execute("INSERT INTO activity_evidence VALUES ('a','binary_sensor.p',1,'manual')")
            db.execute("INSERT INTO pattern_feedback VALUES ('a','example','dismiss',1)")
        point=await self.point();await self.restore(point)
        with closing(sqlite3.connect(self.selections.path)) as db, db:
            self.assertEqual(1,db.execute('SELECT COUNT(*) FROM activity_evidence').fetchone()[0])
            self.assertEqual(1,db.execute('SELECT COUNT(*) FROM pattern_feedback').fetchone()[0])
        self.assertNotIn('activity_evidence',(self.root/'savepoints'/f"{point['id']}.json").read_text())

    async def test_future_schema_refuses_read_preview_or_restore(self):
        point=await self.point()
        with closing(sqlite3.connect(self.selections.path)) as db, db:db.execute('PRAGMA user_version=99')
        with self.assertRaises(InvalidSelection):await self.plans.preview_restore(point['id'])
        with self.assertRaises(InvalidSelection):await self.point()

if __name__=='__main__':unittest.main()
