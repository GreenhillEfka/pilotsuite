import unittest
from pilotsuite.core.ha_references import entity_references
class ReferenceTests(unittest.TestCase):
 def test_services_are_not_entities_and_entity_lists_are(self):
  cfg={"action":"light.turn_on","target":{"entity_id":["light.a","light.b"]},"data":{"x":"sensor.fake"}}
  self.assertEqual({"light.a","light.b"},entity_references(cfg))
 def test_templates_are_not_guessed_as_static_dependencies(self):
  self.assertEqual(set(),entity_references({"value_template":"{{ states('sensor.temp') }}" }))
if __name__=="__main__": unittest.main()
