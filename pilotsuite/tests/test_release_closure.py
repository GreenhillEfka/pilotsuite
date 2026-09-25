"""Regression checks from the full-source Alpha.26 release review; no HA writes."""
import copy
import unittest
from unittest.mock import AsyncMock

from pilotsuite.core.automation_import import import_automation
from pilotsuite.core.automation_diff import semantic_diff
from pilotsuite.core.automation_transform import transformed_config, verify_takeover
from pilotsuite.core.foundation import build_foundation, _stable_key
from pilotsuite.core.helper_reconciliation import reconcile_helpers
from pilotsuite.core.setup_journey import setup_journey
from pilotsuite.core.lighting_policy import lighting_target, should_adjust
from pilotsuite.core.comfort_policy import media_intent, climate_intent
from pilotsuite.core.selections import InvalidSelection


class ReleaseClosureTests(unittest.TestCase):
    def snapshot(self, config=None):
        return import_automation('automation.room', config or {'alias':'Room','actions':[]},
                                 zone_id='room', zone_revision=2, inventory_ids={'light.room'})

    def test_snapshot_and_projection_have_detached_source_data(self):
        config={'alias':'Room','actions':[{'action':'light.turn_on','target':{'entity_id':'light.room'}}]}
        before=copy.deepcopy(config)
        snapshot=self.snapshot(config)
        config['actions'][0]['action']='light.turn_off'
        snapshot['projection']['actions'].append({'stop':'example'})
        self.assertEqual(before,snapshot['source']['config'])
        self.assertEqual(['light.room'],snapshot['projection']['zone_references'])

    def test_import_reports_templates_indirect_targets_and_disabled_steps(self):
        result=self.snapshot({'alias':'Room','actions':[{'action':'light.turn_on',
            'target':{'area_id':'room'},'data':{'brightness':"{{ states('sensor.value') }}"},'enabled':False}]})
        self.assertEqual(['disabled_steps_included_as_structure','indirect_references_not_resolved',
                          'templates_not_evaluated'],result['limitations'])
        self.assertFalse(result['persisted'])
        self.assertEqual([],result['projection']['external_references'])

    def test_import_rejects_large_nonfinite_and_recursive_data(self):
        recursive={}; recursive['loop']=recursive
        for config in ({'alias':'x'*140000},{'value':float('nan')},recursive):
            with self.subTest(kind=type(config)), self.assertRaises(InvalidSelection):
                self.snapshot(config)

    def test_metadata_is_preserved_but_not_mislabeled_unknown(self):
        snapshot=self.snapshot({'alias':'Room','description':'keep','actions':[], 'future':{'x':1}})
        desired={'actions':[{'stop':'test'}]}
        diff=semantic_diff(snapshot,desired)
        self.assertEqual(['future'],diff['preserved_unknown_fields'])
        desired['actions'].clear()
        self.assertEqual([{'stop':'test'}],diff['changes'][0]['after'])
        self.assertEqual('Room',transformed_config(snapshot,{'actions':[]})['alias'])

    def test_transform_cannot_ignore_unknown_edits_or_ambiguous_shapes(self):
        with self.assertRaises(ValueError): transformed_config(self.snapshot(),{'variables':{'x':2}})
        with self.assertRaises(ValueError):
            transformed_config(self.snapshot({'trigger':[], 'triggers':[]}),{'triggers':[]})
        with self.assertRaises(ValueError):
            transformed_config(self.snapshot({'use_blueprint':{'path':'example.yaml'}}),{'mode':'restart'})

    def test_config_match_without_entity_identity_is_not_verification(self):
        snapshot=self.snapshot()
        config=transformed_config(snapshot,{'mode':'restart'})
        result=verify_takeover(snapshot,config,{'mode':'restart'})
        self.assertFalse(result['verified']); self.assertFalse(result['rollback_required'])
        self.assertTrue(verify_takeover(snapshot,config,{'mode':'restart'},actual_entity_id='automation.room')['verified'])
        self.assertFalse(verify_takeover(snapshot,config,{'mode':'restart'},actual_entity_id='automation.other')['verified'])

    def test_names_do_not_collide_after_normalizing_or_truncating(self):
        names=['Room','room','HZ Weird !','HZ Weird ?','x'*60+'a','x'*60+'b']
        self.assertEqual(len(names),len({_stable_key(n) for n in names}))
        self.assertEqual('hz_room',_stable_key('hz_room'))

    def test_ignored_stale_mistyped_and_unavailable_sources_cannot_mean_ready(self):
        original={'zone_id':'z','revision':2,'items':[{'entity_id':'input_boolean.room',
            'decision':'relevant','suggested_role':'input_boolean','state':'off'}]}
        report={'effective_roles':{'presence':['input_boolean.room']}}
        self.assertEqual('ready',build_foundation(original,report)['modules']['presence']['state'])
        variants=[{'decision':'ignored'},{'decision':'unreviewed'},{'suggested_role':'temperature'},
                  {'state':'unavailable'},{'state':None}]
        for change in variants:
            inventory=copy.deepcopy(original);inventory['items'][0].update(change)
            result=build_foundation(inventory,report)
            self.assertEqual('needs_sources',result['modules']['presence']['state'])
            self.assertEqual(['input_boolean.room'],result['missing_sources'])
        self.assertEqual('needs_sources',build_foundation({**original,'items':[]},report)['modules']['presence']['state'])
        self.assertEqual('relevant',original['items'][0]['decision'])

    def test_empty_setup_and_registry_absence_never_mean_ready(self):
        journey=setup_journey({})
        self.assertEqual('attention',journey['steps'][0]['state'])
        self.assertEqual('unverified',journey['steps'][1]['state'])
        foundation={'zone_id':'z','revision':1,'helper_plan':[{'domain':'timer','key':'pilotsuite_z_timer'}]}
        for catalog in ([],[{'entity_id':'timer.pilotsuite_z_timer'}]):
            result=reconcile_helpers(foundation,catalog)
            self.assertEqual(0,result['counts']['create']);self.assertEqual(0,result['counts']['reuse'])
            self.assertFalse(result['execution']['allowed'])

    def test_nonfinite_values_never_become_light_or_climate_targets(self):
        for value in (float('nan'),float('inf'),float('-inf'),True,None,'50'):
            self.assertIsNone(lighting_target(outdoor_lux=value,occupied=True)['target'])
            self.assertFalse(should_adjust(10,value))
            self.assertEqual('unknown',climate_intent(occupied=True,temperature=value,target=21)['intent'])
        self.assertFalse(should_adjust(10,90,deadband=-1))
        self.assertEqual('none',media_intent(occupied='off',atmosphere='relax')['intent'])


class ImportBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import tempfile
        from pathlib import Path
        from pilotsuite.core.settings import Settings
        from pilotsuite.service import PilotSuiteService
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.service=PilotSuiteService(Settings(Path(self.temp.name),Path(self.temp.name)/'options.json'))
        self.inventory={'zone_id':'z','revision':1,'items':[{'entity_id':'sensor.room'}]}
        self.service.selection_inventory=AsyncMock(return_value=self.inventory)
        self.service.client.automation_config=AsyncMock(return_value={'alias':'Room','actions':[]})

    async def test_revision_conflict_prevents_network_call(self):
        from pilotsuite.core.selections import SelectionConflict
        with self.assertRaises(SelectionConflict):
            await self.service.import_existing_automation('z','automation.room',0)
        self.service.client.automation_config.assert_not_awaited()

    async def test_existing_review_lock_blocks_parallel_import(self):
        from pilotsuite.ha.client import HomeAssistantError
        async with self.service._automation_review_lock:
            with self.assertRaises(HomeAssistantError):
                await self.service.import_existing_automation('z','automation.room',1)
        self.service.client.automation_config.assert_not_awaited()

    async def test_network_does_not_hold_projection_lock_and_changed_inventory_discards(self):
        from pilotsuite.core.selections import SelectionConflict
        async def read(_):
            self.assertFalse(self.service._projection_lock.locked())
            self.inventory['items'].append({'entity_id':'sensor.new'})
            return {'alias':'Room','actions':[]}
        self.service.client.automation_config.side_effect=read
        with self.assertRaises(SelectionConflict):
            await self.service.import_existing_automation('z','automation.room',1)

    async def test_boolean_revision_is_not_valid_integer(self):
        with self.assertRaises(InvalidSelection):
            await self.service.import_existing_automation('z','automation.room',True)
        self.service.client.automation_config.assert_not_awaited()
