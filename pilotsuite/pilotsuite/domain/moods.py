"""Transparent, deterministic context scores for the Golden Zone."""

from __future__ import annotations

from collections.abc import Iterable
from statistics import fmean
from typing import Any
import math

from .models import Mood, Neuron


def calculate_moods(neurons: Iterable[Neuron], *, connected: bool, profile: str = 'cellar') -> list[Mood]:
    observations = list(neurons)
    humidity = _numeric(observations, "humidity")
    temperature = _numeric(observations, "temperature")
    climate = [n for n in observations if n.kind in {"temperature", "humidity"}]
    valid_ids = {n.entity_id for n in humidity + temperature}
    unavailable = [n for n in climate if n.entity_id not in valid_ids]

    high_humidity = _high_score(humidity, warning=65.0, critical=80.0)
    low_humidity = _low_score(humidity, warning=45.0, critical=30.0)
    high_temperature = _high_score(temperature, warning=18.0, critical=25.0)
    low_temperature = _low_score(temperature, warning=5.0, critical=0.0)
    uncertainty = len(unavailable) / len(climate) if climate else None
    missing_kinds = [kind for kind, values in (("humidity", humidity), ("temperature", temperature)) if not values]
    system_health = 1.0 if connected else 0.0
    alert = max(high_humidity, low_humidity, high_temperature, low_temperature)
    stability = max(0.0, 1.0 - max(alert, uncertainty or 0, 1.0 - system_health))
    if missing_kinds:
        stability = None

    values = [
        Mood("humidity_high", high_humidity if humidity else None, _evidence(humidity, "mean_humidity")),
        Mood("humidity_low", low_humidity if humidity else None, _evidence(humidity, "mean_humidity")),
        Mood(
            "temperature_high",
            high_temperature if temperature else None,
            _evidence(temperature, "mean_temperature"),
        ),
        Mood(
            "temperature_low",
            low_temperature if temperature else None,
            _evidence(temperature, "mean_temperature"),
        ),
        Mood(
            "uncertainty",
            _round(uncertainty) if uncertainty is not None else None,
            (
                {
                    "unavailable": len(unavailable),
                    "missing_required_kinds": missing_kinds,
                    "total": len(climate),
                    "scope": "observed_climate_sensors",
                    "entity_ids": [item.entity_id for item in unavailable],
                },
            ),
        ),
        Mood("alert", _round(alert) if humidity or temperature else None),
        Mood("stable", _round(stability) if stability is not None else None),
        Mood(
            "system_health",
            system_health,
            ({"home_assistant_connected": connected},),
        ),
    ]
    if profile == 'observe':
        # No cellar-specific comfort thresholds in a general-purpose zone.
        values = [m if m.name in {'uncertainty', 'system_health'} else Mood(m.name, None) for m in values]
    return values


def _numeric(neurons: list[Neuron], kind: str) -> list[Neuron]:
    return [
        neuron
        for neuron in neurons
        if neuron.kind == kind and neuron.quality == "good"
        and not isinstance(neuron.value, bool)
        and isinstance(neuron.value, (int, float))
        and math.isfinite(neuron.value)
        and neuron.unit == ("°C" if kind == "temperature" else "%")
    ]


def _mean(neurons: list[Neuron]) -> float | None:
    return fmean(float(item.value) for item in neurons) if neurons else None


def _high_score(neurons: list[Neuron], warning: float, critical: float) -> float:
    value = _mean(neurons)
    if value is None or value <= warning:
        return 0.0
    if value >= critical:
        return 1.0
    return _round((value - warning) / (critical - warning))


def _low_score(neurons: list[Neuron], warning: float, critical: float) -> float:
    value = _mean(neurons)
    if value is None or value >= warning:
        return 0.0
    if value <= critical:
        return 1.0
    return _round((warning - value) / (warning - critical))


def _evidence(neurons: list[Neuron], key: str) -> tuple[dict[str, Any], ...]:
    value = _mean(neurons)
    if value is None:
        return ()
    return (
        {
            key: _round(value),
            "entity_ids": [item.entity_id for item in neurons],
            "sample_count": len(neurons),
        },
    )


def _round(value: float) -> float:
    return round(max(0.0, min(value, 1.0)) if value <= 1.0 else value, 3)
