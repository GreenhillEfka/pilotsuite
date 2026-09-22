"""Normalize Home Assistant states into explainable observations."""

from __future__ import annotations

from typing import Any

from .models import Neuron


NUMERIC_DEVICE_CLASSES = {
    "apparent_power",
    "atmospheric_pressure",
    "carbon_dioxide",
    "carbon_monoxide",
    "current",
    "data_rate",
    "distance",
    "duration",
    "energy",
    "frequency",
    "gas",
    "humidity",
    "illuminance",
    "moisture",
    "monetary",
    "nitrogen_dioxide",
    "nitrogen_monoxide",
    "nitrous_oxide",
    "ozone",
    "pm1",
    "pm10",
    "pm25",
    "power",
    "precipitation",
    "pressure",
    "signal_strength",
    "sound_pressure",
    "speed",
    "sulphur_dioxide",
    "temperature",
    "volatile_organic_compounds",
    "voltage",
    "volume",
    "water",
    "weight",
    "wind_speed",
}


def build_neurons(scope: dict[str, Any]) -> list[Neuron]:
    result: list[Neuron] = []
    for item in scope.get("entities", []):
        if not isinstance(item, dict):
            continue
        entity_id = item.get("entity_id")
        area_id = item.get("area_id")
        state = item.get("state", {})
        registry = item.get("registry", {})
        if not isinstance(entity_id, str) or not isinstance(area_id, str):
            continue
        if not isinstance(state, dict) or not isinstance(registry, dict):
            continue
        attrs = state.get("attributes", {})
        attrs = attrs if isinstance(attrs, dict) else {}
        raw_state = state.get("state")
        device_class = attrs.get("device_class") or registry.get("device_class")
        domain = entity_id.split(".", 1)[0]
        kind = str(device_class or domain)
        quality = _quality(raw_state)
        value = _value(raw_state, str(device_class or ""), domain, quality)
        name = str(
            registry.get("name")
            or attrs.get("friendly_name")
            or registry.get("original_name")
            or entity_id
        )
        result.append(
            Neuron(
                entity_id=entity_id,
                area_id=area_id,
                kind=kind,
                value=value,
                unit=_optional_string(attrs.get("unit_of_measurement")),
                quality=quality,
                observed_at=_optional_string(state.get("last_updated")),
                name=name,
            )
        )
    return sorted(result, key=lambda neuron: neuron.entity_id)


def _quality(raw_state: Any) -> str:
    if raw_state is None:
        return "missing"
    normalized = str(raw_state).lower()
    if normalized in {"unknown", "unavailable", "none", ""}:
        return normalized or "missing"
    return "good"


def _value(
    raw_state: Any, device_class: str, domain: str, quality: str
) -> float | str | bool | None:
    if quality != "good":
        return None
    normalized = str(raw_state)
    if domain == "binary_sensor" or normalized.lower() in {"on", "off"}:
        return normalized.lower() == "on"
    if device_class in NUMERIC_DEVICE_CLASSES or domain in {"sensor", "number"}:
        try:
            return float(normalized)
        except ValueError:
            return normalized
    return normalized


def _optional_string(value: Any) -> str | None:
    return str(value) if value is not None else None

