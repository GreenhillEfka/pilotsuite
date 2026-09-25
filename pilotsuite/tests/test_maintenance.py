import tempfile
import unittest
import sqlite3
from pilotsuite.core.helper_inspection import inspect
from pathlib import Path
from unittest.mock import AsyncMock

from aiohttp.test_utils import TestClient, TestServer
from pilotsuite import VERSION
from pilotsuite.app import create_app,SERVICE_KEY
from pilotsuite.core.settings import Settings
from pilotsuite.core.maintenance import APP_SLUG,update_view,release_history


class UpdateViewTests(unittest.TestCase):
    def fixture(self,installed=VERSION,latest=VERSION,state='off'):
        return ([{'entity_id':'update.renamed','unique_id':APP_SLUG+'_version_latest','platform':'hassio'}],
                {'update.renamed':{'state':state,'attributes':{'installed_version':installed,'latest_version':latest,'in_progress':False}}})
    def test_renamed_entity_uses_stable_identity_and_current_state(self):
        registry,states=self.fixture()
        self.assertEqual('current',update_view(registry,states,fresh=True)['state'])
        self.assertEqual('unknown',update_view(registry,states,fresh=False)['state'])
    def test_only_matching_hassio_entry_and_exact_runtime_version_are_accepted(self):
        registry,states=self.fixture();registry[0]['platform']='template'
        self.assertEqual('unknown',update_view(registry,states,fresh=True)['state'])
        registry,states=self.fixture(installed='0.1.0-alpha.1')
        self.assertEqual('version_mismatch',update_view(registry,states,fresh=True)['state'])
    def test_update_availability_progress_and_skipping_are_distinct(self):
        registry,states=self.fixture(latest='0.1.0-alpha.999',state='on')
        self.assertTrue(update_view(registry,states,fresh=True)['install_available'])
        states['update.renamed']['attributes']['in_progress']=True
        self.assertEqual('installing',update_view(registry,states,fresh=True)['state'])
        states['update.renamed']['attributes']['in_progress']=False;states['update.renamed']['state']='off'
        self.assertEqual('unknown',update_view(registry,states,fresh=True)['state'])
        states['update.renamed']['attributes']['skipped_version']='0.1.0-alpha.999'
        self.assertEqual('skipped',update_view(registry,states,fresh=True)['state'])
    def test_duplicate_or_missing_metadata_is_unknown(self):
        registry,states=self.fixture()
        self.assertEqual('unknown',update_view(registry*2,states,fresh=True)['state'])
        states['update.renamed']['attributes']={}
        self.assertFalse(update_view(registry,states,fresh=True)['install_available'])
    def test_invalid_progress_cannot_offer_installation(self):
        for value in (None, 'false', -1, 101, float('inf'), float('nan')):
            registry,states=self.fixture(latest='0.1.0-alpha.999',state='on')
            states['update.renamed']['attributes']['in_progress']=value
            self.assertFalse(update_view(registry,states,fresh=True)['install_available'])
    def test_history_is_three_bundled_versions_not_installed_history(self):
        rows=release_history();self.assertEqual(3,len(rows));self.assertEqual(VERSION,rows[0]['version'])
        self.assertEqual(3,len({r['version'] for r in rows}))


class ExistingHelperInspectionTests(unittest.TestCase):
    def test_timer_storage_key_not_current_name_and_no_ownership_claim(self):
        rows=[{'entity_id':'timer.renamed','name':'Nachlauf','platform':'timer','unique_id':'original', 'decision':'unreviewed'}]
        result=inspect(rows,{'timer':[{'id':'original','duration':'0:03:00','restore':False,'token':'never expose'}]}, {})[0]
        self.assertEqual({'duration':'0:03:00','restore':False},result['config'])
        self.assertTrue(result['warnings']);self.assertEqual('existing_not_adopted',result['ownership'])
    def test_missing_or_duplicate_storage_identity_never_implies_create(self):
        rows=[{'entity_id':'timer.renamed','name':'x','platform':'timer','unique_id':'original','decision':'ignored'}]
        for configs in ([],[{'id':'renamed'}],[{'id':'original'},{'id':'original'}]):
            result=inspect(rows,{'timer':configs},{})[0]
            self.assertEqual('needs_separate_inspection',result['state'])
            self.assertEqual({},result['config'])
    def test_flow_helpers_are_visible_without_claiming_configuration_read(self):
        rows=[{'entity_id':'binary_sensor.room','name':'x','platform':'template','unique_id':'abc','decision':'relevant'}]
        result=inspect(rows,{}, {'presence':['binary_sensor.room']})[0]
        self.assertEqual('needs_separate_inspection',result['state']);self.assertEqual(['presence'],result['roles'])


class MaintenanceAPITests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.app=create_app(Settings(self.root,self.root/'options.json',supervisor_token='',golden_zone_area_ids=('a',),
            refresh_interval_seconds=3600,ingress_allowed_peers=('127.0.0.1',)))
        self.client=TestClient(TestServer(self.app));await self.client.start_server();self.addAsyncCleanup(self.client.close)
        self.service=self.app[SERVICE_KEY]
        self.service.client.snapshot=AsyncMock(side_effect=AssertionError('No network read allowed'))
        self.service.client.automation_config=AsyncMock(side_effect=AssertionError('No automation read allowed'))
        self.service.client.helper_collection=AsyncMock(return_value=[{'id':'original_presence','initial':False}])

    async def test_maintenance_is_no_store_and_never_does_ha_io_on_get(self):
        r=await self.client.get('/api/v1/maintenance');self.assertEqual(200,r.status)
        self.assertEqual('no-store',r.headers['Cache-Control']);data=await r.json()
        self.assertFalse(data['ha_execution']);self.assertEqual('bundled_release_notes',data['history_kind'])
        self.service.client.snapshot.assert_not_awaited();self.service.client.helper_collection.assert_not_awaited()
        self.assertEqual(200,(await self.client.get('/maintenance')).status)
        self.assertEqual(200,(await self.client.get('/assets/maintenance.js')).status)

    async def test_create_preview_confirm_restore_via_real_application(self):
        response=await self.client.post('/api/v1/maintenance/savepoints',json={'label':'API test'})
        self.assertEqual(201,response.status);point=await response.json()
        response=await self.client.post(f"/api/v1/maintenance/savepoints/{point['id']}/preview",json={})
        self.assertEqual(200,response.status);preview=await response.json()
        args={k:preview[k] for k in ('sha256','basis')};args['confirm_paused_restore']=False
        path=f"/api/v1/maintenance/savepoints/{point['id']}/restore"
        self.assertEqual(400,(await self.client.post(path,json=args)).status)
        args['confirm_paused_restore']=True
        response=await self.client.post(path,json=args);self.assertEqual(200,response.status)
        self.assertEqual(1,(await response.json())['restored'])
        self.assertFalse((await self.service.zones.list())[0]['enabled'])
        self.service.client.snapshot.assert_not_awaited()

    async def test_methods_csrf_content_type_and_ingress_are_guarded(self):
        self.assertEqual(405,(await self.client.get('/api/v1/maintenance/savepoints')).status)
        self.assertEqual(400,(await self.client.post('/api/v1/maintenance/savepoints',data='{"label":"x"}',headers={'Content-Type':'text/plain'})).status)
        from dataclasses import replace
        self.service.settings=replace(self.service.settings,ingress_allowed_peers=('172.30.32.2',))
        for path in ('/maintenance','/api/v1/maintenance','/assets/maintenance.js'):
            self.assertEqual(403,(await self.client.get(path)).status)
        self.assertEqual(403,(await self.client.post('/api/v1/maintenance/savepoints',json={'label':'x'})).status)

    async def test_explicit_helpers_match_renamed_storage_id(self):
        await self.service.world.replace({'areas':[{'area_id':'a'}],'entities':[
          {'entity_id':'input_boolean.renamed','area_id':'a','platform':'input_boolean','unique_id':'original_presence'}],
          'states':[{'entity_id':'input_boolean.renamed','state':'off','attributes':{}}]})
        revision=(await self.service.selection_inventory('a'))['revision']
        response=await self.client.post('/api/v1/zones/a/helpers/inspect',json={'zone_revision':revision})
        self.assertEqual(200,response.status);data=await response.json()
        self.assertEqual('input_boolean.renamed',data['items'][0]['entity_id'])
        self.assertEqual('configuration_read',data['items'][0]['state'])
        self.assertEqual('existing_not_adopted',data['items'][0]['ownership'])
        self.service.client.helper_collection.assert_awaited_once_with('input_boolean')

    async def test_helper_inspection_rechecks_revision_after_network(self):
        await self.service.world.replace({'areas':[{'area_id':'a'}],'entities':[
          {'entity_id':'timer.old','area_id':'a','platform':'timer','unique_id':'old'}]})
        async def changed(_):
            await self.service.selections.patch('a',0,{'timer.old':'ignored'})
            return [{'id':'old'}]
        self.service.client.helper_collection=AsyncMock(side_effect=changed)
        self.assertEqual(409,(await self.client.post('/api/v1/zones/a/helpers/inspect',json={'zone_revision':0})).status)


class RescueTests(unittest.IsolatedAsyncioTestCase):
    async def test_broken_database_is_not_replaced_and_ui_survives(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'selections.sqlite3';original=b'not a SQLite database';path.write_bytes(original)
            app=create_app(Settings(root,root/'options.json',ingress_allowed_peers=('127.0.0.1',),supervisor_token=''))
            client=TestClient(TestServer(app));await client.start_server()
            try:
                response=await client.get('/');self.assertEqual(200,response.status)
                self.assertIn('rescue-warning',await response.text())
                self.assertEqual(503,(await client.get('/health/ready')).status)
                data=await (await client.get('/api/v1/maintenance')).json();self.assertTrue(data['rescue_mode'])
                self.assertEqual(503,(await client.post('/api/v1/maintenance/savepoints',json={'label':'no'})).status)
                self.assertEqual(503,(await client.get('/api/v1/zones')).status)
                self.assertEqual(original,path.read_bytes());self.assertEqual([],app[SERVICE_KEY]._tasks)
            finally:await client.close()

if __name__=='__main__':unittest.main()
