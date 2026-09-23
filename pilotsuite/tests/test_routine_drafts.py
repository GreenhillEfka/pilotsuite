"""Synthetic routine editing; no live HA, consent changes or actuator calls."""
import asyncio
import copy
import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, UTC
from pathlib import Path
from unittest.mock import patch

from aiohttp.test_utils import TestClient, TestServer
from pilotsuite.app import create_app, SERVICE_KEY
from pilotsuite.core.settings import Settings
from pilotsuite.core.plans import PlanStore, ReadOnlyRelease
from pilotsuite.core.selections import SelectionConflict, InvalidSelection, SelectionStore


class RoutineDraftTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.path = Path(temp.name)
        app = create_app(Settings(self.path, self.path/'options.json', golden_zone_area_ids=('a','b'),
                                 supervisor_token='', refresh_interval_seconds=3600,
                                 ingress_allowed_peers=('127.0.0.1',)))
        self.client = TestClient(TestServer(app)); await self.client.start_server()
        self.addAsyncCleanup(self.client.close)
        self.service = app[SERVICE_KEY]; self.store = self.service.plans
        self.now = datetime(2026,9,23,12,tzinfo=UTC).timestamp()
        clock = patch('time.time', side_effect=lambda: self.now); clock.start(); self.addCleanup(clock.stop)
        await self.service.world.replace({'areas':[{'area_id':'a'},{'area_id':'b'}],
            'entities':[{'entity_id':'binary_sensor.synthetic','area_id':'a'},
                        {'entity_id':'light.synthetic','area_id':'a'},
                        {'entity_id':'light.unreviewed','area_id':'a'},
                        {'entity_id':'light.other','area_id':'b'}],
            'states':[{'entity_id':'binary_sensor.synthetic','state':'off','attributes':{'device_class':'motion'}},
                      {'entity_id':'light.synthetic','state':'off','attributes':{}},
                      {'entity_id':'light.unreviewed','state':'off','attributes':{}},
                      {'entity_id':'light.other','state':'off','attributes':{}}]})
        await self.service.selections.patch('a',0,{'binary_sensor.synthetic':'relevant','light.synthetic':'relevant'})
        await self.service.context.configure('a',1,{'presence':['binary_sensor.synthetic']},True,now=self.now-4*86400)
        for day in (3,2,1):
            for minute in (0,10):
                t = self.now-day*86400+minute*60
                self.assertTrue(await self.service.context.record('a','binary_sensor.synthetic',t,'unknown',now=t))
        self.pattern = (await self.service.context.report('a'))['patterns'][0]['id']
        self.url = '/api/v1/zones/a/drafts'

    async def create(self):
        response = await self.client.post(self.url,json={'pattern_id':self.pattern,'zone_revision':2})
        self.assertEqual(201,response.status,await response.text())
        return await response.json()

    def edit(self, draft, **changes):
        fields = copy.deepcopy(draft['fields']); fields.update(changes)
        return {'revision':draft['revision'],'zone_revision':2,'fields':fields,'refresh_source':False}

    async def test_create_is_explicit_idempotent_and_persists_without_copying_evidence(self):
        self.assertEqual([], (await (await self.client.get(self.url)).json())['items'])
        before = await self.service.context.report('a')
        draft = await self.create(); again = await self.create()
        self.assertEqual(draft['id'],again['id']); self.assertEqual('incomplete',draft['state'])
        self.assertFalse(draft['execution']['allowed']); self.assertIsNone(draft['current_pattern']['confidence'])
        self.assertEqual('not_checked',draft['automation_check'])
        restored = PlanStore(self.path,self.service.audit,self.service.context)
        inventory = await self.service.selection_inventory('a')
        self.assertEqual(draft['id'],(await restored.drafts('a',inventory))[0]['id'])
        with sqlite3.connect(self.service.selections.path) as db:
            saved = db.execute('SELECT fields FROM routine_drafts').fetchone()[0]
        self.assertNotIn('statistics',saved); self.assertNotIn('activation_count',saved)
        after = await self.service.context.report('a')
        for key in ('evidence','patterns','config','reobservation'):
            self.assertEqual(before[key],after[key])

    async def test_edit_roundtrip_export_projection_and_no_execution(self):
        draft = await self.create()
        payload = self.edit(draft,title='<script>synthetic</script>',goal='Light comfort',trigger='Presence',
                            conditions='Only when dark',manual_override='Manual off takes priority',target_ids=['light.synthetic'])
        response = await self.client.patch(self.url+'/'+draft['id'],json=payload)
        self.assertEqual(200,response.status); saved = await response.json()
        self.assertEqual(2,saved['revision']); self.assertEqual('ready_for_review',saved['state'])
        self.assertEqual(payload['fields'],saved['fields']); self.assertEqual('not_assessed',saved['risk'])
        context = await (await self.client.get('/api/v1/zones/a/context')).json()
        self.assertEqual(saved['id'],context['drafts'][0]['id'])
        self.assertEqual(['light.synthetic'],[x['entity_id'] for x in context['draft_target_candidates']])
        with self.assertRaises(ReadOnlyRelease): await self.store.apply(saved['id'])
        self.assertEqual(409,(await self.client.post('/api/v1/transactions/'+saved['id']+'/apply')).status)

    async def test_concurrent_edit_cannot_overwrite_newer_revision(self):
        draft = await self.create(); inventory = await self.service.selection_inventory('a')
        results = await asyncio.gather(*[self.store.save_draft('a',draft['id'],self.edit(draft,goal=goal),inventory)
                                        for goal in ('first','second')],return_exceptions=True)
        self.assertEqual(1,sum(isinstance(r,SelectionConflict) for r in results))
        self.assertEqual(1,sum(isinstance(r,dict) for r in results))
        saved = (await self.store.drafts('a',inventory))[0]
        winner = next(r for r in results if isinstance(r,dict))
        self.assertEqual(winner['fields'],saved['fields']); self.assertEqual(2,saved['revision'])

    async def test_source_revision_change_requires_explicit_current_recheck(self):
        draft = await self.create()
        await self.service.context.configure('a',2,{'presence':['binary_sensor.synthetic']},False)
        current = (await (await self.client.get(self.url)).json())['items'][0]
        self.assertEqual('zone_changed',current['source_status'])
        old = self.edit(draft,goal='kept')
        self.assertEqual(409,(await self.client.patch(self.url+'/'+draft['id'],json=old)).status)
        old['zone_revision'] = 3
        response = await self.client.patch(self.url+'/'+draft['id'],json=old)
        saved = await response.json(); self.assertEqual('zone_changed',saved['source_status'])
        updated = self.edit(saved,goal='kept'); updated.update(zone_revision=3,refresh_source=True)
        saved = await (await self.client.patch(self.url+'/'+draft['id'],json=updated)).json()
        self.assertEqual('current',saved['source_status'])
        self.assertFalse((await self.service.context.get('a'))['learning'])

    async def test_reset_drops_evidence_but_retains_authored_draft_as_unverified(self):
        draft = await self.create()
        await self.service.context.configure('a',2,{'presence':['binary_sensor.synthetic']},False,reset=True)
        current = (await (await self.client.get(self.url)).json())['items'][0]
        self.assertEqual('pattern_missing',current['source_status']); self.assertIsNone(current['current_pattern'])
        payload = self.edit(current); payload.update(zone_revision=3,refresh_source=True)
        self.assertEqual(400,(await self.client.patch(self.url+'/'+draft['id'],json=payload)).status)
        with sqlite3.connect(self.service.selections.path) as db:
            self.assertEqual(0,db.execute('SELECT COUNT(*) FROM activity_evidence').fetchone()[0])

    async def test_expired_pattern_cannot_create_or_refresh_draft(self):
        draft = await self.create(); self.now += 15*86400
        self.assertEqual(400,(await self.client.post(self.url,json={'pattern_id':self.pattern,'zone_revision':2})).status)
        current = (await (await self.client.get(self.url)).json())['items'][0]
        self.assertEqual('needs_review',current['state'])
        self.assertEqual('pattern_missing',current['source_status'])

    async def test_zone_isolation_and_unreviewed_foreign_target_rejected(self):
        draft = await self.create()
        self.assertEqual([], (await (await self.client.get('/api/v1/zones/b/drafts')).json())['items'])
        payload = self.edit(draft); payload['zone_revision'] = 0
        self.assertEqual(400,(await self.client.patch('/api/v1/zones/b/drafts/'+draft['id'],json=payload)).status)
        for target in ('light.other','light.unreviewed','light.invented'):
            response = await self.client.patch(self.url+'/'+draft['id'],json=self.edit(draft,target_ids=[target]))
            self.assertEqual(400,response.status)

    async def test_removed_target_stays_visible_but_blocks_readiness(self):
        draft = await self.create()
        draft = await (await self.client.patch(self.url+'/'+draft['id'],json=self.edit(draft,target_ids=['light.synthetic']))).json()
        await self.service.selections.patch('a',2,{'light.synthetic':'ignored'})
        current = (await (await self.client.get(self.url)).json())['items'][0]
        self.assertEqual(['light.synthetic'],current['unavailable_targets'])
        self.assertEqual('needs_review',current['state'])
        payload = self.edit(current,target_ids=[]); payload['zone_revision'] = 3
        saved = await (await self.client.patch(self.url+'/'+draft['id'],json=payload)).json()
        self.assertEqual([],saved['fields']['target_ids'])

    async def test_unknown_execution_fields_and_malformed_inputs_are_rejected(self):
        draft = await self.create()
        for body in ([],None,{'actions':[{'service':'light.turn_on'}]}, {'revision':True}):
            self.assertEqual(400,(await self.client.patch(self.url+'/'+draft['id'],json=body)).status)
        payload = self.edit(draft); payload['fields']['actions'] = []
        self.assertEqual(400,(await self.client.patch(self.url+'/'+draft['id'],json=payload)).status)
        payload = self.edit(draft,title='x'*121)
        self.assertEqual(400,(await self.client.patch(self.url+'/'+draft['id'],json=payload)).status)

    async def test_delete_is_revision_guarded_and_does_not_remove_learning(self):
        draft = await self.create(); before = await self.service.context.report('a')
        self.assertEqual(409,(await self.client.delete(self.url+'/'+draft['id'],json={'revision':2})).status)
        self.assertEqual(200,(await self.client.delete(self.url+'/'+draft['id'],json={'revision':1})).status)
        self.assertEqual([], (await (await self.client.get(self.url)).json())['items'])
        self.assertEqual(before['evidence'],(await self.service.context.report('a'))['evidence'])

    async def test_v6_migration_backs_up_preserves_data_and_legacy_denied_plans(self):
        await self.store.create({'description':'synthetic old dry-run','actions':[]})
        legacy = (self.path/'plans.jsonl').read_bytes()
        before = await self.service.context.report('a')
        with sqlite3.connect(self.service.selections.path) as db:
            db.execute('DROP TABLE routine_drafts'); db.execute('PRAGMA user_version=6')
        await self.service.selections.initialize()
        backup = list(self.path.glob('selections.v6.*.bak')); self.assertEqual(1,len(backup))
        with sqlite3.connect(backup[0]) as db:
            self.assertEqual(6,db.execute('PRAGMA user_version').fetchone()[0])
            self.assertEqual(6,db.execute('SELECT COUNT(*) FROM activity_evidence').fetchone()[0])
            self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='routine_drafts'").fetchone())
        await self.service.selections.initialize(); self.assertEqual(1,len(list(self.path.glob('selections.v6.*.bak'))))
        with sqlite3.connect(self.service.selections.path) as db:
            self.assertEqual(7,db.execute('PRAGMA user_version').fetchone()[0])
        self.assertEqual(legacy,(self.path/'plans.jsonl').read_bytes())
        self.assertEqual(before['evidence'],(await self.service.context.report('a'))['evidence'])

    async def test_draft_limit_never_silently_discards_existing_work(self):
        draft = await self.create()
        with patch('pilotsuite.core.plans.MAX_DRAFTS',1):
            self.assertEqual(draft['id'],(await self.create())['id'])
            with sqlite3.connect(self.service.selections.path) as db:
                db.execute("UPDATE routine_drafts SET pattern_id='old_synthetic'")
            self.assertEqual(400,(await self.client.post(self.url,json={'pattern_id':self.pattern,'zone_revision':2})).status)
        self.assertEqual(1,len((await (await self.client.get(self.url)).json())['items']))
