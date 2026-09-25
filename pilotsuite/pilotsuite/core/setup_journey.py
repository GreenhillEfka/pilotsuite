"""State-of-the-art UX projection: one progressive zone setup, no hidden execution."""
from __future__ import annotations

def setup_journey(foundation, *, imported_automations=()):
    modules=foundation.get("modules",{})
    reconciliation=foundation.get("helper_reconciliation",{})
    steps=[
      {"id":"sources","title":"Quellen & Rollen","state":"ready" if all(v.get("state")=="ready" for v in modules.values()) else "attention",
       "summary":"Mehrfachquellen, logische Raumzustände und Mess-/Aktorrollen prüfen."},
      {"id":"helpers","title":"Zonenbasis","state":"attention" if reconciliation.get("counts",{}).get("conflict",0) else
       "ready" if reconciliation.get("counts",{}).get("create",0)==0 else "planned",
       "summary":"Vorhandene Helfer wiederverwenden; nur eindeutig fehlende ergänzen."},
      {"id":"existing_logic","title":"Bestehende Logik","state":"ready" if imported_automations else "optional",
       "summary":"Automationen importieren, Modulverantwortung und Reparaturbedarf sichtbar machen."},
      {"id":"comfort","title":"Komfortregeln","state":"planned",
       "summary":"Anwesenheit, Tageslicht, Atmosphäre, Medien und Klima gemeinsam abstimmen."},
      {"id":"apply","title":"Übernehmen","state":"locked",
       "summary":"Semantischen Diff prüfen, sichern, freigeben, anwenden und verifizieren."},
    ]
    return {"schema":"pilotsuite-zone-setup-journey-v1","steps":steps,
            "principles":["progressive_disclosure","explain_before_apply","reuse_before_create",
                          "one_responsible_control_path","manual_override_first"],
            "execution":{"allowed":False,"actions":[]}}
