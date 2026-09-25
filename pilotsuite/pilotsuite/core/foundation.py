"""Explainable, read-only zone-foundation plan derived from canonical roles."""
from __future__ import annotations
import re

FOUNDATION_MODULES = ("presence", "lighting", "media", "climate")

def _stable_key(zone_id: str) -> str:
    key = re.sub(r"[^a-z0-9_]+", "_", zone_id.lower()).strip("_")
    return (key or "zone")[:48]

def build_foundation(inventory, report):
    """Describe reusable HA foundations without creating helpers or actions."""
    roles = report.get("effective_roles") or report.get("config", {}).get("roles", {})
    items = {i.get("entity_id"): i for i in inventory.get("items", []) if isinstance(i, dict)}
    zone_id = inventory.get("zone_id", "")
    key = _stable_key(zone_id)

    def selected(role):
        return [e for e in roles.get(role, []) if isinstance(e, str)]

    presence = selected("presence")
    lux = selected("illuminance")
    daylight = selected("daylight_binary")
    lights = selected("light")
    temperature = selected("temperature")
    humidity = selected("humidity")
    climate = selected("climate")
    media = selected("media")
    atmosphere = selected("atmosphere")

    logical_presence = [e for e in presence if e.startswith("input_boolean.")]
    raw_presence = [e for e in presence if not e.startswith("input_boolean.")]
    missing = sorted({e for group in roles.values() if isinstance(group, list) for e in group if e not in items})

    helpers = []
    if not logical_presence:
        helpers.append({"domain":"input_boolean","key":f"pilotsuite_{key}_anwesenheit","name":f"PilotSuite · {key} · Anwesenheit",
                        "purpose":"Einheitlicher, expliziter Raumstatus; Rohsensoren bleiben Belege."})
    helpers.append({"domain":"timer","key":f"pilotsuite_{key}_anwesenheitsnachlauf","name":f"PilotSuite · {key} · Anwesenheitsnachlauf",
                    "purpose":"Nachlauf mit Neustart-/Fristprüfung; Ablauf allein beweist keine Abwesenheit."})
    if not atmosphere:
        helpers.append({"domain":"input_select","key":f"pilotsuite_{key}_atmosphaere","name":f"PilotSuite · {key} · Atmosphäre",
                        "purpose":"Expliziter Nutzerwunsch; keine automatisch behauptete Emotion."})

    modules = {
      "presence":{"state":"ready" if presence else "needs_sources",
                  "sources":presence,"logical_sources":logical_presence,"raw_sources":raw_presence},
      "lighting":{"state":"ready" if lights and (lux or daylight) else "needs_sources",
                  "lights":lights,"illuminance":lux,"daylight_binary":daylight},
      "media":{"state":"ready" if media else "needs_sources","players":media},
      "climate":{"state":"ready" if climate and temperature else "needs_sources",
                 "controllers":climate,"temperature":temperature,"humidity":humidity},
    }
    correlations = [
      {"id":"presence-light-time-atmosphere","state":"ready" if presence and lights and (lux or daylight) else "blocked",
       "inputs":{"presence":presence,"illuminance":lux,"daylight_binary":daylight,"lights":lights,"atmosphere":atmosphere},
       "limits":["Anwesenheit ist keine Schaltfreigabe.","Eigenlicht ist kein unabhängiges Tageslichtsignal."]},
      {"id":"climate-temperature-humidity-time","state":"ready" if climate and temperature else "blocked",
       "inputs":{"climate":climate,"temperature":temperature,"humidity":humidity},
       "limits":["Sollwert, Isttemperatur und Heizaktivität bleiben getrennt.","Relative Feuchte allein belegt keine Entfeuchtung."]},
      {"id":"presence-media-atmosphere-time","state":"ready" if presence and media else "blocked",
       "inputs":{"presence":presence,"media":media,"atmosphere":atmosphere},
       "limits":["Keine Musik ist ein gültiges Ergebnis.","Laufende Mediennutzung hat Vorrang vor Vorschlägen."]},
    ]
    return {"schema":"pilotsuite-zone-foundation-v1","zone_id":zone_id,"revision":inventory.get("revision"),
            "modules":modules,"correlations":correlations,"helper_plan":helpers,"missing_sources":missing,
            "execution":{"allowed":False,"actions":[]},
            "invariants":["Bestehende passende HA-Logik vor Neuanlage wiederverwenden.",
                          "Ein verantwortlicher Steuerpfad pro physischem Ziel.",
                          "Manuelle Bedienung und explizite Szenen haben Vorrang."]}
