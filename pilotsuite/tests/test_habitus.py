from __future__ import annotations

import unittest

from pilotsuite.domain.models import Neuron
from pilotsuite.domain.moods import calculate_moods
from pilotsuite.domain.synapses import build_suggestions


def neuron(entity_id: str, kind: str, value: float | None, quality: str = "good") -> Neuron:
    return Neuron(
        entity_id=entity_id,
        area_id="erdkeller",
        kind=kind,
        value=value,
        unit="%" if kind == "humidity" else "°C",
        quality=quality,
        observed_at=None,
        name=entity_id,
    )


class HabitusTests(unittest.TestCase):
    def test_high_humidity_produces_explainable_suggestion(self) -> None:
        moods = calculate_moods(
            [
                neuron("sensor.humidity_a", "humidity", 78.0),
                neuron("sensor.humidity_b", "humidity", 76.0),
                neuron("sensor.temperature", "temperature", 12.0),
            ],
            connected=True,
        )
        mood_map = {item.name: item for item in moods}
        self.assertGreater(mood_map["humidity_high"].score, 0.35)
        suggestions = build_suggestions(moods, ("erdkeller",))
        humidity = next(item for item in suggestions if "humidity-high" in item.rule_id)
        self.assertTrue(humidity.evidence)
        self.assertEqual(("erdkeller",), humidity.scope)
        self.assertEqual((), humidity.proposed_actions)

    def test_missing_states_increase_uncertainty(self) -> None:
        moods = calculate_moods(
            [
                neuron("sensor.a", "humidity", None, "unavailable"),
                neuron("sensor.b", "temperature", 10.0),
            ],
            connected=True,
        )
        mood_map = {item.name: item.score for item in moods}
        self.assertEqual(0.5, mood_map["uncertainty"])
        self.assertEqual(0.5, mood_map["stable"])


if __name__ == "__main__":
    unittest.main()

