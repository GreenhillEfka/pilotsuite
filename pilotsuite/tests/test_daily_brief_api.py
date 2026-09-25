"""HTTP contracts through the actual app, ContextStore and selection owners."""
from contextlib import closing
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from aiohttp.test_utils import TestClient, TestServer
from pilotsuite.app import create_app, SERVICE_KEY
from pilotsuite.core.settings import Settings
from daily_brief_support import seed_daily_brief, fixture_control, stored_digest


class DailyBriefAPITests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='daily-brief-api-')
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.app = create_app(Settings(root, root/'options.json', golden_zone_area_ids=('a', 'b'),
            supervisor_token='', refresh_interval_seconds=3600, ingress_allowed_peers=('127.0.0.1',)))
        self.client = TestClient(TestServer(self.app))
        await self.client.start_server()
        self.addAsyncCleanup(self.client.close)
        self.service = self.app[SERVICE_KEY]
        self.now = datetime(2026, 9, 24, 18, tzinfo=UTC).timestamp()
        self.clock = patch('time.time', return_value=self.now)
        self.clock.start(); self.addCleanup(self.clock.stop)
        self.fixture = await seed_daily_brief(self.service, self.now)

    async def read(self, path='/api/v1/zones/a/context'):
        response = await self.client.get(path)
        self.assertEqual(200, response.status, await response.text())
        return await response.json()

    async def control(self, action, **fields):
        return await fixture_control(self.service, self.fixture, {'action': action, **fields})

    async def test_real_owner_evidence_produces_a_bound_candidate(self):
        report = await self.read()
        candidate = report['daily_brief']['candidate']
        self.assertIsNotNone(candidate, report['daily_brief'])
        self.assertEqual(self.fixture['pattern_id'], candidate['pattern_id'])
        self.assertEqual(12, candidate['statistics']['activation_count'])
        self.assertEqual(6, candidate['statistics']['distinct_day_count'])
        self.assertEqual(6, candidate['temporal']['training_events'])
        self.assertEqual(6, candidate['temporal']['later_events'])
        self.assertEqual({'zone_id': 'a', 'revision': report['revision']}, candidate['basis'])
        self.assertEqual({'allowed': False, 'actions': []}, candidate['execution'])

    async def test_get_head_export_do_not_collect_inspect_or_change_any_table(self):
        before = await self.control('snapshot')
        normal = await self.read()
        for path in ('/api/v1/zones/a/context', '/api/v1/zones/a/context/export'):
            response = await self.client.head(path)
            self.assertEqual(200, response.status)
            self.assertEqual(b'', await response.read())
        exported = await self.read('/api/v1/zones/a/context/export')
        self.assertEqual(normal['daily_brief'], exported['daily_brief'])
        self.assertNotIn('evidence', normal)
        self.assertEqual(12, len(exported['evidence']))
        self.assertEqual(before, await self.control('snapshot'))

    async def test_existing_feedback_route_withholds_without_changing_observed_counts(self):
        report = await self.read()
        for decision, count in (('rejected', 'dismissed'), ('later', 'deferred')):
            response = await self.client.post('/api/v1/zones/a/feedback',
                json={'pattern_id': self.fixture['pattern_id'], 'decision': decision})
            self.assertEqual(200, response.status)
            updated = await response.json()
            self.assertIsNone(updated['daily_brief']['candidate'])
            self.assertEqual(1, updated['daily_brief']['excluded'][count])
            self.assertEqual(report['event_count'], updated['event_count'])
        await self.control('feedback', decision='accepted')
        candidate = (await self.read())['daily_brief']['candidate']
        self.assertEqual('review_requested', candidate['state'])
        self.assertFalse(candidate['execution']['allowed'])

    async def test_disconnect_withholds_without_inventing_no_activity(self):
        await self.control('connection', ready=False)
        report = await self.read()
        self.assertEqual('disconnected', report['collection_state'])
        self.assertIsNone(report['daily_brief']['candidate'])
        self.assertEqual(12, report['event_count'])
        await self.control('connection', ready=True)
        self.assertIsNotNone((await self.read())['daily_brief']['candidate'])

    async def test_source_unavailable_then_returned_off_is_not_absence_evidence(self):
        await self.control('source', state='unavailable')
        report = await self.read()
        self.assertIsNone(report['daily_brief']['candidate'])
        self.assertEqual(12, report['event_count'])
        await self.control('source', state='off')
        self.assertIsNotNone((await self.read())['daily_brief']['candidate'])

    async def test_revocation_keeps_retained_evidence_and_blocks_highlight(self):
        await self.control('learning', enabled=False)
        report = await self.read()
        self.assertEqual('off', report['collection_state'])
        self.assertIsNone(report['daily_brief']['candidate'])
        self.assertEqual(12, report['event_count'])
        self.assertFalse(report['config']['learning'])

    async def test_pausing_uses_current_revision_and_never_resumes_learning(self):
        previous = (await self.read())['revision']
        await self.control('pause')
        report = await self.read()
        self.assertGreater(report['revision'], previous)
        self.assertEqual(report['revision'], report['daily_brief']['revision'])
        self.assertIsNone(report['daily_brief']['candidate'])
        self.assertEqual('paused', report['collection_state'])

    async def test_second_zone_and_unknown_zone_do_not_leak_first_zone_evidence(self):
        foreign = await self.read('/api/v1/zones/b/context')
        self.assertEqual('b', foreign['daily_brief']['zone_id'])
        self.assertIsNone(foreign['daily_brief']['candidate'])
        self.assertEqual(0, foreign['event_count'])
        self.assertEqual({'dismissed': 0, 'deferred': 0}, foreign['daily_brief']['excluded'])
        self.assertNotIn(self.fixture['pattern_id'], str(foreign))
        response = await self.client.get('/api/v1/zones/unknown/context')
        self.assertEqual(400, response.status)

    async def test_absent_coverage_withholds_even_when_a_pattern_exists(self):
        # Only corrupt this disposable fixture; no new production mutation API.
        with closing(sqlite3.connect(self.service.selections.path)) as db, db:
            db.execute('DELETE FROM coverage_checks WHERE zone_id=?', ('a',))
        before = stored_digest(self.service)
        report = await self.read()
        self.assertEqual(1, len(report['patterns']))
        self.assertIsNone(report['daily_brief']['candidate'])
        self.assertEqual('unknown', report['daily_brief']['coverage_state'])
        self.assertEqual(before, stored_digest(self.service))

    async def test_ingress_and_apply_guards_are_unchanged(self):
        before = stored_digest(self.service)
        self.assertEqual(409, (await self.client.post('/api/v1/transactions/synthetic/apply')).status)
        self.service.settings = replace(self.service.settings, ingress_allowed_peers=('172.30.32.2',))
        for path in ('/api/v1/zones/a/context', '/api/v1/zones/a/context/export'):
            response = await self.client.get(path)
            self.assertEqual(403, response.status)
        self.assertEqual(before, stored_digest(self.service))
