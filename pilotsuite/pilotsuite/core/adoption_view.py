"""UI-safe explainers for imported automation adoption."""
from __future__ import annotations

def adoption_summary(snapshot, mapping=None, diff=None):
    mapping=mapping or {}; diff=diff or {}
    matched=[k for k,v in (mapping.get("modules") or {}).items() if v.get("state")=="matched"]
    changes=[x.get("field") for x in diff.get("changes",[]) if isinstance(x,dict)]
    external=snapshot.get("projection",{}).get("external_references",[])
    return {"schema":"pilotsuite-adoption-summary-v1","title":snapshot.get("title"),
            "automation_id":snapshot.get("entity_id"),"modules":matched,
            "external_dependencies":external,"proposed_change_fields":changes,
            "messages":[
              "Home Assistant bleibt Ausführungsverantwortlicher bis zur verifizierten Übernahme.",
              "Unbekannte Felder der Originalautomation bleiben erhalten.",
              "Manuelle Freigabe, Backup und Rückleseprüfung sind Pflicht."
            ],"execution":{"allowed":False,"actions":[]}}
