"""Progressive setup shows observed preparation, never inferred authorization."""
from __future__ import annotations


def setup_journey(foundation, *, imported_automations=()):
    modules = foundation.get("modules", {})
    counts = foundation.get("helper_reconciliation", {}).get("counts", {})
    steps = [
        {"id": "sources", "title": "Quellen & Rollen",
         "state": "ready" if modules and all(v.get("state") == "ready" for v in modules.values()) else "attention",
         "summary": "Zuordnung prüfen. Fehlende optionale Module müssen nicht eingerichtet werden."},
        {"id": "helpers", "title": "Zonenbasis",
         "state": "attention" if counts.get("conflict") else "unverified",
         "summary": "Registertreffer sind Hinweise. Helferkonfiguration und Besitz sind noch ungeprüft."},
        {"id": "existing_logic", "title": "Bestehende Logik",
         "state": "attention" if imported_automations else "optional",
         "summary": "Einlesen ist keine Übernahme. Zuordnung, Verhalten und Konflikte separat prüfen."},
        {"id": "comfort", "title": "Komfortregeln", "state": "planned",
         "summary": "Licht-, Musik- und Klimaregeln sind vorbereitet, noch nicht mit Geräten verbunden."},
        {"id": "apply", "title": "Übernehmen", "state": "locked",
         "summary": "In dieser Version gesperrt. Es werden keine Helfer oder Automationen verändert."},
    ]
    return {"schema": "pilotsuite-zone-setup-journey-v1", "steps": steps,
            "principles": ["progressive_disclosure", "explain_before_apply", "reuse_before_create",
                           "one_responsible_control_path", "manual_override_first"],
            "execution": {"allowed": False, "actions": []}}
