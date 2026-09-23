import asyncio
import json
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import AsyncMock
from aiohttp import ClientConnectionError
from pilotsuite.core.history import normalize, activations, trend_view, retrospective, interval, at
from pilotsuite.core.context import ContextStore
from pilotsuite.core.selections import SelectionStore, InvalidSelection, SelectionConflict
from pilotsuite.core.zones import ZoneStore
from pilotsuite.core.settings import Settings
from pilotsuite.service import PilotSuiteService
from pilotsuite.ha.client import HomeAssistantClient, HomeAssistantError
from test_ha_client import _Socket, _Session

P='binary_sensor.p'

class HistoryProjectionTests(unittest.TestCase):
    def test_raw_units_unknown_and_compressed_response(self):
        roles={'temperature':['sensor.t'],'presence':[P]}
        series=normalize({'sensor.t':[{'lu':100,'s':'68','a':{'unit_of_measurement':'°F'}},{'lu':200,'s':'unknown'}],P:[{'lu':100,'s':'off'},{'lu':150,'s':'on'},{'lu':180,'s':'broken'},{'lu':190,'s':'on'}]},roles,100,300)
        self.assertEqual(20,at(series,'sensor.t',150))
        self.assertIsNone(at(series,'sensor.t',200))
        self.assertIsNone(at(series,'sensor.t',5000))
        self.assertEqual([(150,P)],activations(series,roles,100,300))

    def test_seed_and_attribute_updates_never_become_activations(self):
        roles={'presence':[P]}
        series=normalize({P:[{'lu':100,'s':'on'},{'lu':101,'s':'on'},{'lu':200,'s':'off'},{'lu':401,'s':'on'}]},roles,100,500)
        self.assertEqual([(401,P)],activations(series,roles,100,500))

    def test_group_cooldown_and_day_chunk_duplicates(self):
        roles={'presence':[P,'binary_sensor.q']}
        rows=[{'lu':100,'s':'off'},{'lu':150,'s':'on'},{'lu':151,'s':'off'},{'lu':450,'s':'on'}]
        series=normalize({P:rows+rows,'binary_sensor.q':[{'lu':100,'s':'off'},{'lu':160,'s':'on'}]},roles,100,600)
        self.assertEqual([(150,P),(450,P)],activations(series,roles,100,600))

    def test_statistics_epoch_milliseconds_units_no_activity(self):
        # Keep the millisecond round-trip away from a floating wall-clock boundary:
        # start * 1000 / 1000 can otherwise compare a fraction below start.
        now=1728007200; start=now-7200
        roles={'temperature':['sensor.t']}
        series=normalize({'sensor.t':[{'start':start*1000,'mean':68}]},roles,start,now,statistics=True,metadata={'sensor.t':{'unit_of_measurement':'°F'}})
        self.assertEqual(20,series['sensor.t']['points'][0][1])
        view=trend_view(series,roles,start,now,statistics=True)
        self.assertEqual([],view['references']);self.assertEqual('hourly_source_statistics',view['basis'])
        self.assertEqual([],activations(series,roles,start,now))

    def test_partial_presence_stays_unknown_when_none_on(self):
        roles={'presence':[P,'binary_sensor.q']}
        series=normalize({P:[{'lu':100,'s':'off'}]},roles,100,400)
        view=trend_view(series,roles,100,400)
        self.assertIsNone(view['references'][0]['points'][0]['value'])
        self.assertEqual(1,view['references'][0]['points'][0]['valid'])

    def test_graphs_bounded_and_gaps_remain_null(self):
        series={'sensor.t':{'kind':'temperature','unit':'°C','points':[(100,20)]}}
        view=trend_view(series,{'temperature':['sensor.t']},100,100+30*86400)
        self.assertLessEqual(len(view['sources'][0]['points']),481)
        self.assertIsNone(view['sources'][0]['points'][-1][1])

    def test_holdout_later_evidence_cannot_train_pattern(self):
        base=1728000000
        events=[(base+d*86400+8*3600+i*600,P) for d in range(3) for i in range(2)]
        events += [(base+8*86400+8*3600,P)]
        report=retrospective(events,{'min_events':5,'min_days':3},base,base+10*86400)
        self.assertEqual(6,report['checks'][0]['training_events'])
        self.assertEqual(1,report['checks'][0]['later_events'])
        report=retrospective(events,{'min_events':7,'min_days':3},base,base+10*86400)
        self.assertEqual([],report['checks'])

    def test_invalid_intervals(self):
        now=time.time()
        for a,b in [('2026-01-01',now),(now,now),(now-31*86400,now),(now-100,now+20),(float('nan'),now)]:
            with self.assertRaises(InvalidSelection):interval(a,b,now)

class ImportTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.selections=SelectionStore(Path(self.tmp.name));await self.selections.initialize()
        self.zones=ZoneStore(self.selections);await self.zones.bootstrap(('a',))
        await self.selections.patch('a',0,{P:'relevant'})
        self.context=ContextStore(self.selections);self.now=time.time();self.roles={'presence':[P]}
        await self.context.configure('a',1,self.roles,True,now=self.now-100)

    async def rev(self):return (await self.selections.get('a'))['revision']
    async def run_import(self,events,**kwargs):
        return await self.context.import_history('a',await self.rev(),self.roles,events,self.now-86400,self.now-10,now=self.now,**kwargs)

    async def test_import_preconsent_repeat_restart_and_live_overlap(self):
        old=self.now-8000
        await self.context.record('a',P,self.now-50,'unknown',now=self.now)
        receipt=await self.run_import([(old,P),(self.now-60,P)])
        self.assertEqual(1,receipt['accepted'])
        self.assertEqual(0,(await self.run_import([(old,P),(old+5,P)]))['accepted'])
        report=await ContextStore(self.selections).report('a',now=self.now)
        self.assertEqual(2,report['event_count']);self.assertEqual(1,report['historical_event_count'])
        self.assertEqual(2,len(report['history_imports']))
        self.assertEqual(['ha_history','live'],[e['recording_source'] for e in report['evidence']])
        self.assertEqual([],report['coverage_samples']);self.assertEqual([],report['context_evidence'])

    async def test_revocation_and_revision_conflict_reject_atomically(self):
        revision=await self.rev()
        await self.context.configure('a',revision,self.roles,False)
        with self.assertRaises(SelectionConflict):
            await self.context.import_history('a',revision,self.roles,[(self.now-8000,P)],self.now-86400,self.now-10,now=self.now)
        with self.assertRaises(InvalidSelection):await self.run_import([(self.now-8000,P)])
        self.assertEqual(0,(await self.context.report('a'))['event_count'])

    async def test_unreviewed_source_and_paused_zone_reject(self):
        await self.selections.patch('a',await self.rev(),{P:'unreviewed'})
        with self.assertRaises(InvalidSelection):await self.run_import([(self.now-8000,P)])
        await self.selections.patch('a',await self.rev(),{P:'relevant'})
        zone=(await self.zones.list())[0]
        await self.zones.save({k:(False if k=='enabled' else zone[k]) for k in ('name','profile','enabled','area_ids','extra_entity_ids')},'a',await self.rev())
        with self.assertRaises(InvalidSelection):await self.run_import([(self.now-8000,P)])

    async def test_reset_and_source_change_clear_provenance(self):
        await self.run_import([(self.now-8000,P)])
        await self.context.configure('a',await self.rev(),self.roles,False,reset=True)
        report=await self.context.report('a',now=self.now)
        self.assertEqual([],report['history_imports']);self.assertEqual(0,report['historical_event_count'])
        self.assertFalse(report['config']['learning'])

    async def test_v5_migration_backup_preserves_existing_roles(self):
        with sqlite3.connect(self.selections.path) as db:
            db.execute('DROP TABLE history_provenance');db.execute('DROP TABLE history_imports');db.execute('PRAGMA user_version=5')
        await self.selections.initialize()
        backups=list(Path(self.tmp.name).glob('selections.v5.*.bak'));self.assertEqual(1,len(backups))
        with sqlite3.connect(backups[0]) as db:self.assertEqual(5,db.execute('PRAGMA user_version').fetchone()[0])
        self.assertEqual(self.roles,(await self.context.get('a'))['roles'])
        self.assertEqual(1,(await self.run_import([(self.now-8000,P)]))['accepted'])

class HistoryServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.service=PilotSuiteService(Settings(data_dir=Path(self.tmp.name),options_path=Path(self.tmp.name)/'options.json',golden_zone_area_ids=('a',),supervisor_token=''))
        await self.service.selections.initialize();await self.service.zones.bootstrap(('a',))
        await self.service.selections.patch('a',0,{P:'relevant'})
        await self.service.context.configure('a',1,{'presence':[P]},True)
        self.now=time.time();self.start=self.now-86400;self.end=self.now-10
        self.service.selection_inventory=AsyncMock(return_value={'revision':2,'enabled':True,'items':[{'entity_id':P,'decision':'relevant','suggested_role':'motion'}]})
        self.service.client.history=AsyncMock(return_value={'metadata':{},'records':{P:[{'lu':self.start,'s':'off'},{'lu':self.start+100,'s':'on'}]}})
        self.payload={'start':self.start,'end':self.end,'mode':'states','revision':2}

    async def test_only_selected_sources_fetched_and_imported(self):
        view=await self.service.history_view('a',self.payload)
        self.assertEqual(1,view['raw_activation_count'])
        self.assertEqual([P],self.service.client.history.call_args.args[0])
        self.assertEqual(0,(await self.service.context.report('a'))['event_count'])
        result=await self.service.history_view('a',dict(self.payload,consent=True),import_learning=True)
        self.assertEqual(1,result['receipt']['accepted'])

    async def test_config_change_during_fetch_prevents_import(self):
        async def fetch(*args,**kwargs):
            await self.service.selections.patch('a',2,{P:'ignored'})
            return {'records':{},'metadata':{}}
        self.service.client.history.side_effect=fetch
        with self.assertRaises(SelectionConflict):await self.service.history_view('a',dict(self.payload,consent=True),import_learning=True)
        self.assertEqual(0,(await self.service.context.report('a'))['event_count'])

    async def test_statistics_and_missing_consent_cannot_import(self):
        for extra in ({'consent':False},{'consent':True,'mode':'statistics'}):
            with self.assertRaises(InvalidSelection):await self.service.history_view('a',dict(self.payload,**extra),import_learning=True)
        self.service.client.history.assert_not_called()

    async def test_partial_network_failure_saves_nothing(self):
        self.service.client.history.side_effect=HomeAssistantError('failed')
        with self.assertRaises(InvalidSelection):await self.service.history_view('a',dict(self.payload,consent=True),import_learning=True)
        self.assertEqual([], (await self.service.context.report('a'))['history_imports'])

class HistoryClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_day_chunks_commands_and_entity_scope(self):
        socket=_Socket([{'type':'auth_required'},{'type':'auth_ok'},{'id':1,'success':True,'result':{P:[{'s':'off','lu':10}]}},{'id':2,'success':True,'result':{P:[{'s':'on','lu':90000}]}}])
        client=HomeAssistantClient('ws://example','token');client._session=_Session(socket)
        result=await client.history([P],1,90001)
        self.assertEqual(2,len(result['records'][P]))
        self.assertEqual([P],socket.sent[1]['entity_ids'])
        self.assertEqual('history/history_during_period',socket.sent[2]['type'])
        self.assertFalse(socket.sent[1]['minimal_response'])

    async def test_statistics_metadata_and_hourly_contract(self):
        socket=_Socket([{'type':'auth_required'},{'type':'auth_ok'},{'id':1,'success':True,'result':[{'statistic_id':'sensor.t','unit_of_measurement':'°C'}]},{'id':2,'success':True,'result':{}}])
        client=HomeAssistantClient('ws://example','token');client._session=_Session(socket)
        result=await client.history(['sensor.t'],1,100,statistics=True)
        self.assertEqual('°C',result['metadata']['sensor.t']['unit_of_measurement'])
        self.assertEqual('hour',socket.sent[2]['period'])

    async def test_malformed_statistics_metadata_is_a_domain_error(self):
        for metadata in (None, {}, [{}], ['broken'], [{'statistic_id': 12}]):
            with self.subTest(metadata=metadata):
                socket=_Socket([{'type':'auth_required'},{'type':'auth_ok'},
                                {'id':1,'success':True,'result':metadata}])
                client=HomeAssistantClient('ws://example','token');client._session=_Session(socket)
                with self.assertRaisesRegex(HomeAssistantError,'Unsupported statistics metadata response'):
                    await client.history(['sensor.t'],1,100,statistics=True)

    async def test_transport_failure_becomes_bounded_history_error(self):
        class FailedConnection:
            async def __aenter__(self):
                raise ClientConnectionError('offline')
            async def __aexit__(self, *_):
                return None
        class FailedSession:
            closed = False
            def ws_connect(self, *_args, **_kwargs):
                return FailedConnection()
        client=HomeAssistantClient('ws://example','token');client._session=FailedSession()
        with self.assertRaisesRegex(HomeAssistantError,'history connection failed'):
            await client.history([P],1,100)

    async def test_timeout_becomes_bounded_history_error(self):
        class TimedOutConnection:
            async def __aenter__(self):
                raise TimeoutError
            async def __aexit__(self, *_):
                return None
        class TimedOutSession:
            closed = False
            def ws_connect(self, *_args, **_kwargs):
                return TimedOutConnection()
        client=HomeAssistantClient('ws://example','token');client._session=TimedOutSession()
        with self.assertRaisesRegex(HomeAssistantError,'history request timed out'):
            await client.history([P],1,100)
