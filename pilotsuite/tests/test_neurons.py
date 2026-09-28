from __future__ import annotations

import unittest

from pilotsuite.domain.neurons import build_neurons


class NeuronTests(unittest.TestCase):
    @staticmethod
    def binary(raw, device_class='occupancy', entity_id='binary_sensor.synthetic'):
        return {'entity_id': entity_id, 'area_id': 'synthetic', 'registry': {},
                'state': {'state': raw, 'attributes': {'device_class': device_class}}}

    def test_invalid_binary_states_never_become_false_or_good(self):
        for kind in ('occupancy', 'motion', 'presence', 'light', 'door'):
            for raw in ('broken', '0', '1', 'false', 'true', ' off ', False, True, 0, 1, {}, []):
                with self.subTest(kind=kind, raw=raw):
                    neuron = build_neurons({'entities': [self.binary(raw, kind)]})[0]
                    self.assertIsNone(neuron.value)
                    self.assertEqual('invalid', neuron.quality)

    def test_binary_valid_and_missing_states_keep_their_semantics(self):
        for raw, value, quality in [('on', True, 'good'), ('off', False, 'good'),
                ('ON', True, 'good'), ('OFF', False, 'good'), (None, None, 'missing'),
                ('', None, 'missing'), ('unknown', None, 'unknown'),
                ('unavailable', None, 'unavailable'), ('none', None, 'none')]:
            with self.subTest(raw=raw):
                neuron = build_neurons({'entities': [self.binary(raw)]})[0]
                self.assertIs(value, neuron.value)
                self.assertEqual(quality, neuron.quality)

    def test_invalid_member_blocks_false_but_does_not_erase_positive_role_evidence(self):
        from pilotsuite.domain.context import context_summary
        for kind, role in [('occupancy', 'presence'), ('light', 'daylight_binary')]:
            for valid_state, expected in [('off', None), ('on', True)]:
                with self.subTest(kind=kind, valid_state=valid_state):
                    neurons = build_neurons({'entities': [self.binary('broken', kind),
                        self.binary(valid_state, kind, 'binary_sensor.valid')]})
                    summary, _ = context_summary(neurons,
                        {role: ['binary_sensor.synthetic', 'binary_sensor.valid']})
                    self.assertEqual('partial', summary[role]['status'])
                    self.assertEqual(1, summary[role]['valid'])
                    self.assertIs(expected, summary[role]['active'])
                    self.assertIs(expected, summary[role]['reference']['value'])

    def test_unavailable_is_not_coerced_to_zero(self) -> None:
        scope = {
            "entities": [
                {
                    "entity_id": "sensor.erdkeller_humidity",
                    "area_id": "erdkeller",
                    "registry": {},
                    "state": {
                        "state": "unavailable",
                        "attributes": {
                            "device_class": "humidity",
                            "unit_of_measurement": "%",
                        },
                    },
                }
            ]
        }
        neurons = build_neurons(scope)
        self.assertEqual(1, len(neurons))
        self.assertIsNone(neurons[0].value)
        self.assertEqual("unavailable", neurons[0].quality)

    def test_numeric_sensor_is_normalized(self) -> None:
        scope = {
            "entities": [
                {
                    "entity_id": "sensor.erdkeller_temperature",
                    "area_id": "erdkeller",
                    "registry": {"name": "Temperatur"},
                    "state": {
                        "state": "11.7",
                        "last_updated": "2026-09-22T18:00:00+00:00",
                        "attributes": {
                            "device_class": "temperature",
                            "unit_of_measurement": "°C",
                        },
                    },
                }
            ]
        }
        neuron = build_neurons(scope)[0]
        self.assertEqual(11.7, neuron.value)
        self.assertEqual("temperature", neuron.kind)
        self.assertEqual("good", neuron.quality)

    def test_binary_light_sensor_is_not_a_controllable_light_state(self) -> None:
        observed = build_neurons({"entities": [{"entity_id": "binary_sensor.room_bright", "area_id": "room",
            "registry": {}, "state": {"state": "on", "attributes": {"device_class": "light"}}}]})[0]
        self.assertEqual("daylight_binary", observed.kind)
        self.assertIs(observed.value, True)


if __name__ == "__main__":
    unittest.main()
