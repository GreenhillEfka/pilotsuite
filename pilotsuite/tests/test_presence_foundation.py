import unittest
from pilotsuite.core.presence_foundation import presence_contract,takeover_classification,evaluate_presence

class PresenceFoundationTests(unittest.TestCase):
    def test_positive_source_is_occupied(self):
        d=evaluate_presence({"a":"on","b":"off"},"active")
        self.assertEqual(("occupied",True,"cancel"),(d.state,d.desired_owner,d.timer_action))
    def test_all_clear_starts_grace_not_vacancy(self):
        d=evaluate_presence({"a":"off","b":"off"},"idle")
        self.assertEqual(("grace",True,"start"),(d.state,d.desired_owner,d.timer_action))
    def test_expiry_requires_all_sources_clear(self):
        self.assertEqual("vacant",evaluate_presence({"a":"off","b":"off"},"finished").state)
        d=evaluate_presence({"a":"unavailable","b":"off"},"finished")
        self.assertEqual("unknown",d.state);self.assertIsNone(d.desired_owner)
    def test_restart_active_timer_stays_grace(self):
        self.assertEqual("grace",evaluate_presence({"a":"off"},"active").state)
    def test_contract_and_takeover_are_conservative(self):
        f={"modules":{"presence":{"logical_sources":["input_boolean.room_presence"],"raw_sources":["binary_sensor.motion"]}},
           "helper_plan":[{"domain":"timer","key":"pilotsuite_room_anwesenheitsnachlauf"}]}
        c=presence_contract(f);self.assertTrue(c["execution"]["allowed"]);self.assertIn("unknown",c["state_machine"])
        self.assertEqual("reuse",takeover_classification(["input_boolean.room_presence","binary_sensor.motion"],c)["state"])
        self.assertEqual("inspect",takeover_classification(["input_boolean.room_presence"],c)["state"])
        self.assertEqual("supplement",takeover_classification([],c)["state"])
if __name__=="__main__": unittest.main()
