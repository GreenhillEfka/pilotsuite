import unittest
from pilotsuite.core.presence_foundation import presence_contract,takeover_classification

class PresenceFoundationTests(unittest.TestCase):
    def test_timer_never_proves_vacancy(self):
        f={"modules":{"presence":{"logical_sources":["input_boolean.room_presence"],"raw_sources":["binary_sensor.motion"]}},
           "helper_plan":[{"domain":"timer","key":"pilotsuite_room_anwesenheitsnachlauf"}]}
        c=presence_contract(f)
        self.assertEqual("input_boolean.room_presence",c["logical_owner"])
        self.assertIn("unknown",c["state_machine"])
        self.assertTrue(any("re-check" in rule for rule in c["rules"]))
        self.assertFalse(c["execution"]["allowed"])
    def test_takeover_stays_conservative(self):
        c={"logical_owner":"input_boolean.room_presence","raw_sources":["binary_sensor.motion"],"timer_key":"x"}
        self.assertEqual("reuse",takeover_classification(["input_boolean.room_presence","binary_sensor.motion"],c)["state"])
        self.assertEqual("inspect",takeover_classification(["input_boolean.room_presence"],c)["state"])
        self.assertEqual("supplement",takeover_classification([],c)["state"])

if __name__=="__main__": unittest.main()
