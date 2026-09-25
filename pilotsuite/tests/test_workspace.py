"""Actual app shell and asset coverage; no household data or credentials."""
import tempfile
import unittest
from pathlib import Path
from dataclasses import replace
from aiohttp.test_utils import TestClient, TestServer
from pilotsuite.app import create_app, SERVICE_KEY
from pilotsuite.core.settings import Settings

class WorkspaceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name)
        self.app=create_app(Settings(data_dir=root,options_path=root/'options.json',
            supervisor_token='',refresh_interval_seconds=3600,ingress_allowed_peers=('127.0.0.1',)))
        self.client=TestClient(TestServer(self.app));await self.client.start_server()
    async def asyncTearDown(self):
        await self.client.close();self.tmp.cleanup()
    async def test_workspace_enhances_one_document_and_keeps_existing_forms(self):
        response=await self.client.get('/');self.assertEqual(200,response.status)
        html=await response.text()
        for name in ('workspace-model.js','workspace.js','workspace.css'):
            self.assertEqual(1,html.count('assets/'+name))
            response=await self.client.get('/assets/'+name)
            self.assertEqual(200,response.status);self.assertIn('no-cache',response.headers['Cache-Control'])
        for identity in ('context-form','zone-form','routine-form','selection-save','history-section'):
            self.assertEqual(1,html.count('id="'+identity+'"'))
        self.assertIn("script-src 'self'",response.headers['Content-Security-Policy'])
        self.assertEqual(404,(await self.client.get('/assets/workspace-unlisted.js')).status)
    async def test_workspace_does_not_add_configuration_endpoints_or_weaken_ingress(self):
        service=self.app[SERVICE_KEY]
        before=await service.zones.list()
        await self.client.get('/');await self.client.get('/assets/workspace.js')
        self.assertEqual(before,await service.zones.list())
        self.assertEqual(405,(await self.client.post('/assets/workspace.js',json={})).status)
        service.settings=replace(service.settings,ingress_allowed_peers=('172.30.32.2',))
        for path in ('/','/assets/workspace.js','/assets/workspace-model.js','/assets/workspace.css'):
            self.assertEqual(403,(await self.client.get(path)).status)
    async def test_rescue_keeps_minimal_maintenance_page_and_does_not_load_workspace(self):
        self.app[SERVICE_KEY]._rescue_error='synthetic_database_failure'
        html=await (await self.client.get('/')).text()
        self.assertNotIn('assets/workspace.js',html)
        self.assertIn('maintenance',html)
        self.assertEqual(503,(await self.client.get('/assets/workspace.js')).status)
if __name__=='__main__':unittest.main()
