"""Transient lighting readiness brief from canonical zone and HA review owners."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .context import ROLE_KINDS


ROLES = ("light", "illuminance", "daylight_binary", "presence", "atmosphere")
UNUSABLE_STATES = {None, "", "unknown", "unavailable"}


def _ids(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({item for item in value if isinstance(item, str) and item})


def _usable(role: str, configured: list[str], items: dict[str, dict[str, Any]]) -> list[str]:
    return [entity_id for entity_id in configured
            if items.get(entity_id, {}).get("decision") == "relevant"
            and items[entity_id].get("suggested_role") in ROLE_KINDS.get(role, {role})
            and items[entity_id].get("state") not in UNUSABLE_STATES]


def _automation_rows(inspections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for inspection in inspections:
        if not isinstance(inspection, dict):
            continue
        alignment = inspection.get("alignment") if isinstance(inspection.get("alignment"), dict) else {}
        sources = _ids(alignment.get("source_trigger_references"))
        targets = _ids(alignment.get("target_action_references"))
        limitations = _ids(inspection.get("limitations"))
        state = ("direct_path" if sources and targets else "target_writer" if targets else
                 "source_related" if sources else "indirect_or_unresolved")
        rows.append({
            "automation_id": inspection.get("entity_id"),
            "config_fingerprint": inspection.get("config_fingerprint"),
            "state": state,
            "direct_source_references": sources,
            "direct_light_targets": targets,
            "limitations": limitations,
            "duplicate_assessment": "not_determined",
            "risk": "not_assessed",
        })
    return sorted(rows, key=lambda row: (row["state"] != "direct_path", row["automation_id"] or ""))


def build_lighting_decision(*, zone_id: str, revision: int, roles: dict[str, Any],
                            inventory: dict[str, Any], summary: dict[str, Any],
                            transport_ready: bool, inspections: list[dict[str, Any]],
                            role_origins: dict[str, str] | None = None,
                            checked_at: str | None = None) -> dict[str, Any]:
    """Build a deterministic, non-executable brief; inputs are never mutated."""
    items = {row.get("entity_id"): row for row in inventory.get("items", [])
             if isinstance(row, dict) and isinstance(row.get("entity_id"), str)}
    configured = {role: _ids(roles.get(role)) for role in ROLES}
    usable = {role: _usable(role, configured[role], items) for role in ROLES}
    illuminance = summary.get("illuminance") if isinstance(summary.get("illuminance"), dict) else {}
    valid_lux = {row.get("entity_id") for row in illuminance.get("measurements", [])
                 if isinstance(row, dict) and row.get("quality") == "good"
                 and type(row.get("value")) in (int, float)}
    usable["illuminance"] = [entity_id for entity_id in usable["illuminance"]
                              if entity_id in valid_lux]
    origins = role_origins if isinstance(role_origins, dict) else {}
    source_groups = {role: {"configured": configured[role], "currently_usable": usable[role],
                            "configured_count": len(configured[role]),
                            "currently_usable_count": len(usable[role]),
                            "origin": origins.get(role, "explicit")}
                     for role in ROLES}
    daylight = summary.get("daylight_binary") if isinstance(summary.get("daylight_binary"), dict) else {}
    lights = summary.get("light") if isinstance(summary.get("light"), dict) else {}
    automations = _automation_rows(inspections)

    if not transport_ready:
        state, reason, next_step = "blocked", "transport_not_current", {
            "id": "reload_zone", "label": "Zonenstand erneut laden"}
    elif not usable["light"]:
        state, reason, next_step = "blocked", "no_usable_light_target", {
            "id": "configure_sources", "label": "Leuchtenquelle prüfen"}
    elif not (usable["illuminance"] or usable["daylight_binary"]):
        state, reason, next_step = "blocked", "no_usable_brightness_reference", {
            "id": "configure_sources", "label": "Helligkeitsquelle prüfen"}
    else:
        state, reason, next_step = "withheld", "outdoor_daylight_unconfirmed", {
            "id": "run_synthetic_preview", "label": "Regelverhalten mit Testdaten prüfen"}

    return {
        "schema": "pilotsuite-lighting-decision-v1",
        "zone_id": zone_id,
        "revision": revision,
        "checked_at": checked_at or datetime.now(UTC).isoformat(),
        "state": state,
        "reason": reason,
        "source_groups": source_groups,
        "current_zone_observation": {
            "illuminance": {"status": illuminance.get("status", "unknown"),
                            "value": illuminance.get("value"), "unit": illuminance.get("unit"),
                            "aggregation": illuminance.get("aggregation"),
                            "scope": "configured_indoor_zone_sources"},
            "daylight_binary": {"status": daylight.get("status", "unknown"),
                                "active": daylight.get("active"),
                                "scope": "configured_room_or_daylight_indicator"},
            "light": {"status": lights.get("status", "unknown"),
                      "active": lights.get("active"),
                      "scope": "configured_light_state"},
            "transport_snapshot_current": transport_ready,
            "physical_measurement_current": "not_determined",
        },
        "daylight_basis": {
            "outdoor_daylight_confirmed": False,
            "reason": "no_explicit_outdoor_daylight_provenance",
            "indoor_lux_is_outdoor_proof": False,
            "missing_history_is_counterevidence": False,
        },
        "automation_review": {
            "state": "references_found" if automations else "no_references_found",
            "method": "ha_search_related_entity_then_structural_config_read",
            "coverage": "bounded_structural_only",
            "items": automations,
            "duplicate_assessment": "not_determined",
            "safety_assessment": "not_performed",
        },
        "next_step": next_step,
        "persisted": False,
        "execution": {"allowed": False, "reason": "read_only_decision_brief", "actions": []},
        "limitations": [
            "Ein aktueller Transport-Snapshot beweist keine aktuelle physische Messung.",
            "Innen-Lux oder Eigenlicht bestätigen keine Außenhelligkeit.",
            "Eine vorhandene Automation ist weder automatisch ein Duplikat noch eine sichere Lösung.",
            "Es wurde keine Helligkeits-, Risiko- oder Sicherheitsquote berechnet.",
        ],
    }
