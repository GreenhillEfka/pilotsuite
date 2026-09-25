import unittest
from pilotsuite.core.provisioning import provision_request, provisioning_preview
from pilotsuite.core.selections import InvalidSelection, SelectionConflict

class ProvisioningTests(unittest.TestCase):
    def setUp(self):
        self.inventory={"zone_id":"hz_living","revision":4}
        self.foundation={"revision":4,"helper_plan":[
          {"domain":"timer","key":"pilotsuite_hz_living_anwesenheitsnachlauf"},
          {"domain":"input_select","key":"pilotsuite_hz_living_atmosphaere"}]}

    def test_preview_is_closed_and_names_rollback_boundary(self):
        p=provisioning_preview(self.inventory,self.foundation)
        self.assertFalse(p["execution"]["allowed"])
        self.assertEqual("preview_only",p["transaction"]["state"])
        self.assertIn("same_verified_transaction",p["transaction"]["rollback"])

    def test_request_is_revision_bound_and_plan_bound(self):
        req=provision_request(self.inventory,self.foundation,{"revision":4,"helpers":[
          {"domain":"timer","key":"pilotsuite_hz_living_anwesenheitsnachlauf"}]})
        self.assertEqual((("timer","pilotsuite_hz_living_anwesenheitsnachlauf"),),req.helpers)
        with self.assertRaises(SelectionConflict):
            provision_request(self.inventory,self.foundation,{"revision":3,"helpers":[]})
        with self.assertRaises(InvalidSelection):
            provision_request(self.inventory,self.foundation,{"revision":4,"helpers":[
              {"domain":"timer","key":"foreign_timer"}]})

if __name__=="__main__": unittest.main()
