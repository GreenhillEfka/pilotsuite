from __future__ import annotations

import unittest

from pilotsuite.domain.neurons import build_neurons


class NeuronTests(unittest.TestCase):
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

