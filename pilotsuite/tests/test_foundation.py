import unittest
from pilotsuite.core.foundation import build_foundation

class FoundationTests(unittest.TestCase):
    def test_cross_context_is_explainable_and_read_only(self):
        inventory={"zone_id":"hz_living","revision":7,"items":[
          {"entity_id":"input_boolean.living_presence"},
          {"entity_id":"sensor.lux"},{"entity_id":"light.main"},
          {"entity_id":"climate.room"},{"entity_id":"sensor.temp"},
          {"entity_id":"sensor.rh"},{"entity_id":"media_player.room"}]}
        report={"effective_roles":{"presence":["input_boolean.living_presence"],"illuminance":["sensor.lux"],
          "light":["light.main"],"climate":["climate.room"],"temperature":["sensor.temp"],
          "humidity":["sensor.rh"],"media":["media_player.room"]},"config":{"roles":{}}}
        result=build_foundation(inventory,report)
        self.assertTrue(all(v["state"]=="ready" for v in result["modules"].values()))
        self.assertTrue(all(c["state"]=="ready" for c in result["correlations"]))
        self.assertEqual({"allowed":False,"actions":[]},result["execution"])
        self.assertFalse(any(h["domain"]=="input_boolean" for h in result["helper_plan"]))
        self.assertTrue(any(h["domain"]=="timer" for h in result["helper_plan"]))

    def test_missing_roles_plan_helpers_without_inventing_sources(self):
        result=build_foundation({"zone_id":"HZ Weird !","revision":1,"items":[]},
                                {"effective_roles":{},"config":{"roles":{}}})
        self.assertEqual("needs_sources",result["modules"]["presence"]["state"])
        self.assertEqual([],result["modules"]["presence"]["sources"])
        self.assertEqual(["input_boolean","timer","input_select"],
                         [h["domain"] for h in result["helper_plan"]])
        self.assertTrue(all(c["state"]=="blocked" for c in result["correlations"]))
        self.assertEqual("pilotsuite_hz_weird_anwesenheit",result["helper_plan"][0]["key"])

if __name__=="__main__":
    unittest.main()
