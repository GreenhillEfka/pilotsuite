"""Explainable, read-only zone-foundation plan derived from canonical roles."""
from __future__ import annotations
import re
import hashlib
from .context import ROLE_KINDS

FOUNDATION_MODULES = ("presence", "lighting", "media", "climate")

def _stable_key(zone_id: str) -> str:
    key = re.sub(r"[^a-z0-9_]+", "_", zone_id.lower()).strip("_")
    if key == zone_id and 1 <= len(key) <= 48:
        return key
    # Distinct original IDs must not collapse after normalization/truncation.
    return (key or "zone")[:35] + "_" + hashlib.sha256(zone_id.encode()).hexdigest()[:12]

def build_foundation(inventory, report):
    """Describe reusable HA foundations without creating helpers or actions."""
    roles = report.get("effective_roles") or report.get("config", {}).get("roles", {})
    items = {i.get("entity_id"): i for i in inventory.get("items", []) if isinstance(i, dict)}
    zone_id = inventory.get("zone_id", "")
    key = _stable_key(zone_id)

    rejected = set()
    def selected(role):
        requested = roles.get(role, [])
        if not isinstance(requested, list):
            return []
        selected_ids=[]
        for entity in requested:
            item=items.get(entity) if isinstance(entity,str) else None
            if (not item or item.get("decision") != "relevant"
                    or item.get("suggested_role") not in ROLE_KINDS.get(role,set())
                    or item.get("state") in (None,"unknown","unavailable","")):
                if isinstance(entity,str): rejected.add(entity)
                continue
            selected_ids.append(entity)
        return sorted(set(selected_ids))

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
    missing = sorted(rejected)

    helpers = []
    if not logical_presence:
        helpers.append({"domain":"input_boolean","key":f"pilotsuite_{key}_anwesenheit","name":f"PilotSuite · {key} · Anwesenheit",
                        "purpose":"Einheitlicher, expliziter Raumstatus; Rohsensoren bleiben Belege."})
    helpers.append({"domain":"timer","key":f"pilotsuite_{key}_anwesenheitsnachlauf","name":f"PilotSuite · {key} · Anwesenheitsnachlauf",
                    "purpose":"Nachlauf mit Neustart-/Fristprüfung; Ablauf allein beweist keine Abwesenheit.",
                    "config":{"duration":"00:05:00","restore":True}})
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
    return {"stage":"planning_only", "basis":"confirmed_role_assignment_not_live_acceptance",
            "validated_roles":{role:selected(role) for role in roles if role in ROLE_KINDS},
            "schema":"pilotsuite-zone-foundation-v1","zone_id":zone_id,"revision":inventory.get("revision"),
            "modules":modules,"correlations":[dict(c, implementation="planned", execution_allowed=False) for c in correlations],"helper_plan":helpers,"missing_sources":missing,
            "execution":{"allowed":False,"actions":[]},
            "invariants":["Bestehende passende HA-Logik vor Neuanlage wiederverwenden.",
                          "Ein verantwortlicher Steuerpfad pro physischem Ziel.",
                          "Manuelle Bedienung und explizite Szenen haben Vorrang."]}
