"""Integrated existing routes and owners. No live HA or repeated fixture tests."""
import json
import sqlite3
import unittest
from unittest.mock import AsyncMock
import test_routine_drafts as fixtures
import test_review_notes as note_fixtures
from pilotsuite.core.plans import PlanStore


class ReviewCompassAPITests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=fixtures.RoutineDraftTests.asyncSetUp
    create=fixtures.RoutineDraftTests.create
    edit=fixtures.RoutineDraftTests.edit
    review_draft=fixtures.RoutineDraftTests.review_draft
    prepared=note_fixtures.ReviewNoteTests.prepared
    save=note_fixtures.ReviewNoteTests.save

    async def test_creation_get_context_and_export_share_compass(self):
        draft=await self.create();compass=draft['review_compass']
        self.assertEqual('edit_draft',compass['next_step']['id'])
        for url in (self.url,'/api/v1/zones/a/context','/api/v1/zones/a/context/export'):
            response=await self.client.get(url);self.assertEqual(200,response.status,await response.text())
            data=await response.json();actual=(data.get('items') or data['drafts'])[0]['review_compass']
            self.assertEqual(compass,actual)

    async def test_get_head_and_restart_do_not_inspect_save_or_change_permissions(self):
        draft=await self.create()
        self.service.client.related_automations=AsyncMock();self.service.client.automation_config=AsyncMock()
        before=await self.service.context.report('a')
        with sqlite3.connect(self.service.selections.path) as db:
            tables=set(db.execute("SELECT name FROM sqlite_master WHERE type='table'"))
            saved=db.execute('SELECT * FROM routine_drafts').fetchall()
        for method in ('get','head'):
            self.assertEqual(200,(await getattr(self.client,method)(self.url)).status)
        restored=PlanStore(self.path,self.service.audit,self.service.context)
        result=(await restored.drafts('a',await self.service.selection_inventory('a')))[0]
        self.assertEqual('unknown',result['review_compass']['checks'][3]['state'])
        self.service.client.related_automations.assert_not_awaited();self.service.client.automation_config.assert_not_awaited()
        self.assertEqual(before,await self.service.context.report('a'))
        with sqlite3.connect(self.service.selections.path) as db:
            self.assertEqual(tables,set(db.execute("SELECT name FROM sqlite_master WHERE type='table'")))
            self.assertEqual(saved,db.execute('SELECT * FROM routine_drafts').fetchall())
        self.assertEqual(409,(await self.client.post('/api/v1/transactions/'+draft['id']+'/apply')).status)

    async def test_edit_recalculates_basis_and_does_not_persist_compass(self):
        draft=await self.create()
        response=await self.client.patch(self.url+'/'+draft['id'],json=self.edit(draft,goal='Synthetic comfort'))
        result=await response.json();self.assertEqual(2,result['review_compass']['basis']['draft_revision'])
        with sqlite3.connect(self.service.selections.path) as db:
            fields=db.execute('SELECT fields FROM routine_drafts').fetchone()[0]
            self.assertNotIn('review_compass',fields);self.assertNotIn('statistics',fields)

    async def test_reference_result_enriches_only_explicit_response(self):
        draft=await self.review_draft()
        self.service.client.related_automations=AsyncMock(return_value={'light.synthetic':['automation.synthetic']})
        response=await self.client.post(self.url+'/'+draft['id']+'/automation-review',json={'revision':2,'zone_revision':2})
        report=await response.json();self.assertEqual(200,response.status,report)
        self.assertEqual('partial',report['review_compass']['checks'][3]['state'])
        current=(await (await self.client.get(self.url)).json())['items'][0]
        self.assertEqual('unknown',current['review_compass']['checks'][3]['state'])
        self.assertEqual(report['basis']['source_ids'],report['review_compass']['basis']['source_ids'])

    async def test_detail_and_note_save_bind_current_review_revision(self):
        draft,payload,report,url=await self.prepared()
        self.assertEqual('last_read',report['review_compass']['checks'][3]['state'])
        result=await self.save(url,payload);compass=result['automation_review']['review_compass']
        self.assertEqual(1,compass['basis']['review_revision'])
        self.assertEqual(1,compass['checks'][4]['counts']['matches_last_read'])
        self.assertNotIn('RAW_CONFIG_CANARY',json.dumps(compass))
        self.assertNotIn('Synthetic user assessment',json.dumps(compass))
        saved=(await (await self.client.get(self.url)).json())['items'][0]
        self.assertEqual(1,saved['review_compass']['basis']['review_revision'])
        self.assertEqual(1,saved['review_compass']['checks'][4]['counts']['not_rechecked'])
        self.assertFalse(compass['execution']['allowed'])

    async def test_source_changes_keep_notes_and_mark_compass_stale(self):
        draft,payload,_,url=await self.prepared();await self.save(url,payload)
        await self.service.context.configure('a',2,{'presence':['binary_sensor.synthetic']},False)
        current=(await (await self.client.get(self.url)).json())['items'][0]
        self.assertEqual('stale',current['review_compass']['checks'][0]['state'])
        self.assertEqual(1,current['review_compass']['checks'][4]['counts']['stale'])
        self.assertEqual(payload['text'],current['review_notes']['items'][0]['text'])

    async def test_learning_reset_does_not_delete_authored_draft_or_create_new_consent(self):
        draft=await self.create()
        await self.service.context.configure('a',2,{'presence':['binary_sensor.synthetic']},False,reset=True)
        current=(await (await self.client.get(self.url)).json())['items'][0]
        self.assertEqual('missing',current['review_compass']['checks'][0]['state'])
        self.assertEqual(draft['fields'],current['fields'])
        self.assertFalse((await self.service.context.get('a'))['learning'])

    async def test_foreign_zone_is_empty_and_cannot_receive_another_compass(self):
        draft=await self.create()
        result=await (await self.client.get('/api/v1/zones/b/context')).json()
        self.assertEqual([],result['drafts']);self.assertNotIn(draft['id'],json.dumps(result))

    async def test_compass_assets_use_existing_ingress_and_no_extra_api_writes(self):
        for asset,content in (('review_compass.js','script'),('review_compass.css','css')):
            response=await self.client.get('/assets/'+asset)
            self.assertEqual(200,response.status)
            self.assertIn(content,response.headers['Content-Type'])
            self.assertIn("script-src 'self'",response.headers['Content-Security-Policy'])
        self.assertEqual(405,(await self.client.post('/assets/review_compass.js')).status)
