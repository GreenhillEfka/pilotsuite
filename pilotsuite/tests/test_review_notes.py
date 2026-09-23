"""Full app/PlanStore regressions using the existing synthetic routine fixture."""
import asyncio
import copy
import json
import sqlite3
import time
import unittest
from unittest.mock import AsyncMock, patch

import test_routine_drafts as fixtures
from pilotsuite.core.plans import PlanStore
from pilotsuite.core.selections import SelectionConflict, InvalidSelection
from pilotsuite.ha.client import HomeAssistantError


class ReviewNoteTests(unittest.IsolatedAsyncioTestCase):
    # Reuse setup/helpers, not the fixture's test methods (no duplicate test count).
    asyncSetUp = fixtures.RoutineDraftTests.asyncSetUp
    create = fixtures.RoutineDraftTests.create
    edit = fixtures.RoutineDraftTests.edit
    review_draft = fixtures.RoutineDraftTests.review_draft

    async def prepared(self):
        draft = await self.review_draft()
        self.service.client.related_automations = AsyncMock(return_value={'light.synthetic':['automation.synthetic']})
        self.service.client.automation_config = AsyncMock(return_value={
            'alias':'RAW_CONFIG_CANARY', 'actions':[{'action':'light.turn_on',
            'target':{'entity_id':'light.synthetic'},'data':{'message':'RAW_CONFIG_CANARY'}}]})
        report = await self.service.compare_automations('a',draft['id'],{
            'revision':2,'zone_revision':2,'automation_id':'automation.synthetic','previous_fingerprint':None},inspection=True)
        payload = {'revision':2,'zone_revision':2,'review_revision':0,'automation_id':'automation.synthetic',
                   'config_fingerprint':report['inspection']['config_fingerprint'],
                   'disposition':'reviewed','text':'Synthetic user assessment'}
        return draft, payload, report, self.url+'/'+draft['id']+'/review-notes'

    async def save(self, url, payload):
        response = await self.client.put(url,json=payload)
        self.assertEqual(200,response.status,await response.text())
        return await response.json()

    def deletion(self, payload):
        return {key:payload[key] for key in ('revision','zone_revision','review_revision','automation_id')}

    async def test_save_rechecks_and_persists_without_evidence_or_permission_changes(self):
        draft,payload,_,url = await self.prepared()
        before = await self.service.context.report('a')
        self.service.client.automation_config.reset_mock()
        result = await self.save(url,payload)
        self.service.client.automation_config.assert_awaited_once_with('automation.synthetic')
        self.assertEqual(1,result['review_notes']['revision'])
        self.assertFalse(result['review_notes']['execution']['allowed'])
        self.assertEqual('not_rechecked',result['review_notes']['items'][0]['config_status'])
        self.assertEqual(before,await self.service.context.report('a'))
        saved = (await (await self.client.get(self.url)).json())['items'][0]
        self.assertEqual(2,saved['revision']);self.assertEqual('not_assessed',saved['risk'])
        self.assertFalse(saved['execution']['allowed'])
        self.assertEqual(409,(await self.client.post('/api/v1/transactions/'+draft['id']+'/apply')).status)
        for file in self.path.glob('*'):
            if file.is_file(): self.assertNotIn(b'RAW_CONFIG_CANARY',file.read_bytes())
        exported = await (await self.client.get('/api/v1/zones/a/context/export')).json()
        self.assertEqual('Synthetic user assessment',exported['drafts'][0]['review_notes']['items'][0]['text'])

    async def test_restart_and_listing_keep_notes_without_network_or_freshness_claim(self):
        draft,payload,_,url=await self.prepared();await self.save(url,payload)
        self.service.client.automation_config.reset_mock();self.service.client.related_automations.reset_mock()
        restored=PlanStore(self.path,self.service.audit,self.service.context)
        notes=(await restored.drafts('a',await self.service.selection_inventory('a')))[0]['review_notes']
        self.assertEqual(1,notes['revision']);self.assertFalse(notes['items'][0]['stale'])
        response=await self.client.get(url)
        self.assertEqual('no-store',response.headers['Cache-Control'])
        self.assertEqual('not_rechecked',(await response.json())['items'][0]['config_status'])
        self.service.client.automation_config.assert_not_awaited();self.service.client.related_automations.assert_not_awaited()

    async def test_changed_configuration_rejects_save_and_preserves_previous_note(self):
        _,payload,_,url=await self.prepared();await self.save(url,payload)
        self.service.client.automation_config.return_value['actions'][0]['action']='light.turn_off'
        response=await self.client.put(url,json=dict(payload,review_revision=1,text='must not replace'))
        self.assertEqual(409,response.status)
        self.assertEqual(payload['text'],(await (await self.client.get(url)).json())['items'][0]['text'])

    async def test_failed_reinspection_never_persists_or_echoes_private_errors(self):
        _,payload,_,url=await self.prepared()
        self.service.client.automation_config.side_effect=HomeAssistantError('SECRET_FAILURE_CANARY')
        response=await self.client.put(url,json=payload)
        self.assertEqual(503,response.status);self.assertNotIn('SECRET_FAILURE_CANARY',await response.text())
        self.assertEqual([], (await (await self.client.get(url)).json())['items'])

    async def test_note_conflicts_fail_before_network_and_unknown_fields_are_rejected(self):
        _,payload,_,url=await self.prepared();await self.save(url,payload)
        self.service.client.related_automations.reset_mock()
        self.assertEqual(409,(await self.client.put(url,json=payload)).status)
        self.assertEqual(400,(await self.client.put(url,json=dict(payload,allowed=True))).status)
        self.service.client.related_automations.assert_not_awaited()

    async def test_foreign_zone_cannot_read_write_or_delete_note(self):
        _,payload,_,url=await self.prepared();await self.save(url,payload)
        other=url.replace('/zones/a/','/zones/b/')
        for method,data in [('get',None),('put',dict(payload,zone_revision=0)),('delete',self.deletion(dict(payload,zone_revision=0)))]:
            response=await getattr(self.client,method)(other,**({'json':data} if data else {}))
            self.assertEqual(400,response.status,await response.text())

    async def test_draft_changes_mark_notes_stale_without_erasing_them(self):
        draft,payload,_,url=await self.prepared();await self.save(url,payload)
        await self.store.save_draft('a',draft['id'],self.edit(draft,goal='A new intent'),await self.service.selection_inventory('a'))
        note=(await (await self.client.get(url)).json())['items'][0]
        self.assertTrue(note['stale']);self.assertIn('draft_changed',note['stale_reasons'])
        self.assertEqual(payload['text'],note['text'])

    async def test_learning_reset_retains_notes_and_revokes_their_current_basis(self):
        _,payload,_,url=await self.prepared();await self.save(url,payload)
        await self.service.context.configure('a',2,{},False,reset=True)
        note=(await (await self.client.get(url)).json())['items'][0]
        self.assertTrue(note['stale']);self.assertIn('pattern_missing',note['stale_reasons'])
        self.assertEqual(payload['text'],note['text']);self.assertFalse((await self.service.context.get('a'))['learning'])

    async def test_delete_needs_no_ha_read_and_tombstone_prevents_aba(self):
        _,payload,_,url=await self.prepared();await self.save(url,payload)
        self.service.client.automation_config=AsyncMock(side_effect=HomeAssistantError('offline'))
        deletion=self.deletion(dict(payload,review_revision=1))
        response=await self.client.delete(url,json=deletion)
        self.assertEqual(200,response.status);data=await response.json()
        self.assertEqual(2,data['revision']);self.assertEqual([],data['items'])
        self.service.client.automation_config.assert_not_awaited()
        self.assertEqual(409,(await self.client.put(url,json=payload)).status)

    async def test_draft_delete_cannot_discard_unseen_new_review(self):
        draft,payload,_,url=await self.prepared();await self.save(url,payload)
        target=self.url+'/'+draft['id']
        self.assertEqual(409,(await self.client.delete(target,json={'revision':2})).status)
        self.assertEqual(409,(await self.client.delete(target,json={'revision':2,'review_revision':0})).status)
        self.assertEqual(200,(await self.client.delete(target,json={'revision':2,'review_revision':1})).status)
        with sqlite3.connect(self.service.selections.path) as db:
            self.assertEqual(0,db.execute('SELECT COUNT(*) FROM routine_review_notes').fetchone()[0])

    async def test_concurrent_note_writers_cannot_overwrite_each_other(self):
        draft,payload,report,_=await self.prepared();inventory=await self.service.selection_inventory('a')
        results=await asyncio.gather(*[self.store.save_review_note('a',draft['id'],dict(payload,text=text),inventory,report,time.monotonic())
            for text in ('first','second')],return_exceptions=True)
        self.assertEqual(1,sum(isinstance(r,SelectionConflict) for r in results))
        self.assertEqual(1,sum(isinstance(r,dict) for r in results))

    async def test_write_lock_covers_validation_and_persistence(self):
        draft,payload,report,_=await self.prepared();inventory=await self.service.selection_inventory('a')
        original=self.store._write_review_notes
        def probe(db,*args):
            with sqlite3.connect(self.service.selections.path,timeout=0.01) as other:
                with self.assertRaises(sqlite3.OperationalError): other.execute('BEGIN IMMEDIATE')
            original(db,*args)
        with patch.object(self.store,'_write_review_notes',side_effect=probe):
            await self.store.save_review_note('a',draft['id'],payload,inventory,report,time.monotonic())

    async def test_expired_or_mismatched_server_inspection_is_rejected(self):
        draft,payload,report,url=await self.prepared();inventory=await self.service.selection_inventory('a')
        with self.assertRaises(SelectionConflict):
            await self.store.save_review_note('a',draft['id'],payload,inventory,report,time.monotonic()-31)
        for key,value in [('draft_revision',1),('zone_id','b'),('basis',{})]:
            with self.subTest(key=key), self.assertRaises(SelectionConflict):
                await self.store.save_review_note('a',draft['id'],payload,inventory,dict(report,**{key:value}),time.monotonic())
        self.assertEqual([], (await (await self.client.get(url)).json())['items'])

    async def test_edit_during_network_read_cannot_store_old_assessment(self):
        draft,payload,_,url=await self.prepared()
        async def changed(_):
            self.assertFalse(self.service._projection_lock.locked())
            await self.store.save_draft('a',draft['id'],self.edit(draft,goal='Concurrent edit'),await self.service.selection_inventory('a'))
            return {'actions':[]}
        self.service.client.automation_config.side_effect=changed
        self.assertEqual(409,(await self.client.put(url,json=payload)).status)
        self.assertEqual([], (await (await self.client.get(url)).json())['items'])

    async def test_bound_on_distinct_notes_allows_edit_but_not_silent_eviction(self):
        draft,payload,report,url=await self.prepared();inventory=await self.service.selection_inventory('a')
        for index in range(20):
            p=dict(payload,review_revision=index,automation_id='automation.synthetic_'+str(index))
            r=copy.deepcopy(report);r['inspection']['entity_id']=p['automation_id']
            await self.store.save_review_note('a',draft['id'],p,inventory,r,time.monotonic())
        with self.assertRaises(InvalidSelection):
            await self.store.save_review_note('a',draft['id'],dict(payload,review_revision=20),inventory,report,time.monotonic())
        self.assertEqual(20,len((await (await self.client.get(url)).json())['items']))

    async def test_schema7_backup_precedes_additive_migration_and_preserves_draft(self):
        draft=await self.create()
        with sqlite3.connect(self.service.selections.path) as db:
            db.execute('DROP TABLE routine_review_notes');db.execute('PRAGMA user_version=7')
            old=db.execute('SELECT * FROM routine_drafts').fetchall()
            cfg=db.execute('SELECT * FROM zone_context').fetchall()
        await self.service.selections.initialize()
        backups=list(self.path.glob('selections.v7.*.bak'));self.assertEqual(1,len(backups))
        with sqlite3.connect(backups[0]) as backup:
            self.assertEqual(7,backup.execute('PRAGMA user_version').fetchone()[0])
            self.assertEqual(old,backup.execute('SELECT * FROM routine_drafts').fetchall())
            self.assertFalse(backup.execute("SELECT 1 FROM sqlite_master WHERE name='routine_review_notes'").fetchone())
        with sqlite3.connect(self.service.selections.path) as db:
            self.assertEqual(8,db.execute('PRAGMA user_version').fetchone()[0])
            self.assertEqual(old,db.execute('SELECT * FROM routine_drafts').fetchall())
            self.assertEqual(cfg,db.execute('SELECT * FROM zone_context').fetchall())
        await self.service.selections.initialize()
        self.assertEqual(1,len(list(self.path.glob('selections.v7.*.bak'))))

    async def test_note_assets_are_served_with_correct_types(self):
        for name,kind in [('review_notes.js','javascript'),('review_notes.css','text/css')]:
            response=await self.client.get('/assets/'+name)
            self.assertEqual(200,response.status);self.assertIn(kind,response.headers['Content-Type'])
