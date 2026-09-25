import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from pilotsuite.core.audit import AuditLog
from pilotsuite.core.plans import PlanStore
from pilotsuite.core.provisioning import provision_request, provisioning_preview, desired_helper, exact_timer
from pilotsuite.core.selections import InvalidSelection, SelectionConflict
from pilotsuite.core.settings import Settings
from pilotsuite.ha.client import HomeAssistantError
from pilotsuite.service import PilotSuiteService

class ProvisioningContractTests(unittest.TestCase):
    def setUp(self):
        self.inventory={"zone_id":"hz_living","revision":4,"items":[]}
        self.foundation={"zone_id":"hz_living","revision":4,"helper_plan":[
          {"domain":"timer","key":"pilotsuite_hz_living_anwesenheitsnachlauf","name":"PilotSuite · hz_living · Anwesenheitsnachlauf",
           "config":{"duration":"00:05:00","restore":True}},
          {"domain":"input_select","key":"pilotsuite_hz_living_atmosphaere"}]}

    def test_preview_opens_only_timer_and_names_unknown_outcome_rule(self):
        p=provisioning_preview(self.inventory,self.foundation)
        self.assertTrue(p["execution"]["allowed"])
        self.assertEqual(["timer"],[a["domain"] for a in p["execution"]["actions"]])
        self.assertEqual("read_back_never_blind_retry",p["transaction"]["unknown_outcome"])

    def test_request_requires_explicit_confirmation_and_exact_revision(self):
        payload={"revision":4,"helpers":[{"domain":"timer","key":"pilotsuite_hz_living_anwesenheitsnachlauf"}],"confirm":True}
        req=provision_request(self.inventory,self.foundation,payload)
        self.assertEqual((("timer","pilotsuite_hz_living_anwesenheitsnachlauf"),),req.helpers)
        with self.assertRaises(InvalidSelection):
            provision_request(self.inventory,self.foundation,{**payload,"confirm":False})
        with self.assertRaises(SelectionConflict):
            provision_request(self.inventory,self.foundation,{**payload,"revision":3})

    def test_exact_timer_requires_identity_and_configuration(self):
        helper=desired_helper(self.foundation,"timer","pilotsuite_hz_living_anwesenheitsnachlauf")
        row={"id":helper["key"],"name":helper["name"],"duration":"00:05:00","restore":True}
        self.assertTrue(exact_timer(row,helper))
        self.assertFalse(exact_timer({**row,"restore":False},helper))

class ProvisioningExecutionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        settings=Settings(data_dir=Path(self.tmp.name),options_path=Path(self.tmp.name)/"options.json",
                          refresh_interval_seconds=3600,supervisor_token="")
        self.service=PilotSuiteService(settings)
        self.inventory={"zone_id":"hz_living","revision":4,"items":[],"missing":[],"enabled":True}
        self.service.selection_inventory=AsyncMock(return_value=self.inventory)
        self.service.context.report=AsyncMock(return_value={"config":{"roles":{}}})
        self.service.plans.helper_transaction=AsyncMock(side_effect=["tx-1","tx-1","tx-1"])
        self.key="pilotsuite_hz_living_anwesenheitsnachlauf"
        self.row={"id":self.key,"name":"PilotSuite · hz_living · Anwesenheitsnachlauf",
                  "duration":"00:05:00","restore":True}
        self.payload={"revision":4,"helpers":[{"domain":"timer","key":self.key}],"confirm":True}

    async def asyncTearDown(self):
        await self.service.client.close()
        self.tmp.cleanup()

    async def test_lost_create_response_is_resolved_by_independent_readback_without_retry(self):
        self.service.client.helper_collection=AsyncMock(side_effect=[[],[self.row]])
        self.service.client.helper_create_timer=AsyncMock(side_effect=HomeAssistantError("lost"))
        result=await self.service.provision_helper("hz_living",self.payload)
        self.assertEqual("created_verified",result["state"])
        self.service.client.helper_create_timer.assert_awaited_once()
        self.assertFalse(result["created"] is False)

    async def test_concurrent_zone_edit_aborts_before_write(self):
        self.service.selection_inventory=AsyncMock(side_effect=[self.inventory,{**self.inventory,"revision":5}])
        self.service.client.helper_collection=AsyncMock(return_value=[])
        self.service.client.helper_create_timer=AsyncMock()
        with self.assertRaises(SelectionConflict):
            await self.service.provision_helper("hz_living",self.payload)
        self.service.client.helper_create_timer.assert_not_awaited()

    async def test_preexisting_foreign_configuration_is_never_overwritten_or_deleted(self):
        self.service.client.helper_collection=AsyncMock(return_value=[{**self.row,"restore":False}])
        self.service.client.helper_create_timer=AsyncMock()
        self.service.client.helper_delete_timer=AsyncMock()
        with self.assertRaises(SelectionConflict):
            await self.service.provision_helper("hz_living",self.payload)
        self.service.client.helper_create_timer.assert_not_awaited()
        self.service.client.helper_delete_timer.assert_not_awaited()

    async def test_confirmed_create_with_bad_readback_rolls_back_only_created_identity(self):
        self.service.client.helper_collection=AsyncMock(side_effect=[[],[{**self.row,"restore":False}],[]])
        self.service.client.helper_create_timer=AsyncMock(return_value=self.row)
        self.service.client.helper_delete_timer=AsyncMock()
        with self.assertRaises(HomeAssistantError):
            await self.service.provision_helper("hz_living",self.payload)
        self.service.client.helper_delete_timer.assert_awaited_once_with(self.key)

class ProvisioningJournalTests(unittest.IsolatedAsyncioTestCase):
    async def test_transaction_journal_survives_store_recreation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            first=PlanStore(path,AuditLog(path,100))
            txid=await first.helper_transaction("approved",{"outcome":"pending","key":"x"})
            second=PlanStore(path,AuditLog(path,100))
            content=(path/"helper_transactions.jsonl").read_text()
            self.assertIn(txid,content)
            self.assertIn('"event":"approved"',content)

if __name__=="__main__": unittest.main()
