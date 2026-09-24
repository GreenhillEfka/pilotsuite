"""Bounded, read-only daily brief derived from existing zone projections."""
from __future__ import annotations
from copy import deepcopy


def build_daily_brief(inventory, report):
    """Return one explainable zone brief without collecting or mutating evidence."""
    zone_id = inventory.get("zone_id")
    revision = inventory.get("revision")
    if not isinstance(zone_id, str) or not zone_id or type(revision) is not int or revision < 0:
        raise ValueError("invalid zone projection")

    collection = report.get("collection_state", "off")
    enabled = bool(report.get("enabled", False))
    reviews = report.get("reviews") if isinstance(report.get("reviews"), list) else []
    candidates = report.get("candidates") if isinstance(report.get("candidates"), list) else []

    observations = []
    role_counts = {}
    for item in candidates[:40]:
        role = item.get("suggested_role")
        if isinstance(role, str) and role:
            role_counts[role] = role_counts.get(role, 0) + 1
    if role_counts:
        observations.append({"kind": "inventory", "summary": ", ".join(
            f"{count}× {role}" for role, count in sorted(role_counts.items()))})
    else:
        observations.append({"kind": "inventory", "summary": "Keine bestätigten Beobachtungsquellen in der Zone."})

    reasons = []
    if not enabled:
        reasons.append("Die Zone ist pausiert.")
    if collection in {"off", "paused", "disconnected", "no_source"}:
        reasons.append({
            "off": "Lernen ist ausgeschaltet.",
            "paused": "Beobachtung ist pausiert.",
            "disconnected": "Die Home-Assistant-Verbindung ist nicht bereit.",
            "no_source": "Es gibt keine freigegebene Lernquelle.",
        }[collection])

    current = []
    excluded = {"dismissed": 0, "deferred": 0}
    for review in reviews:
        state = review.get("state")
        if state == "dismissed":
            excluded["dismissed"] += 1
            continue
        if state == "deferred":
            excluded["deferred"] += 1
            continue
        if review.get("zone_id") != zone_id or review.get("revision") != revision:
            continue
        if state not in {"unreviewed", "review_requested"}:
            continue
        if not review.get("sources"):
            continue
        current.append(review)

    candidate = None
    if enabled and collection == "collecting" and current:
        chosen = sorted(current, key=lambda r: (str(r.get("title", "")), str(r.get("pattern_id", ""))))[0]
        candidate = {
            "pattern_id": chosen.get("pattern_id"),
            "title": chosen.get("title") or "Bestehendes Muster prüfen",
            "state": chosen.get("state"),
            "navigation": "pattern_workbench",
            "execution": {"allowed": False, "actions": []},
        }
    elif not reasons:
        reasons.append("Kein aktuelles, ausreichend zugeordnetes Muster ist für eine Prüfung begründet.")

    coverage = report.get("coverage") if isinstance(report.get("coverage"), dict) else {}
    sampled = coverage.get("sampled_slots")
    impaired = coverage.get("impaired_slots")
    if not isinstance(sampled, int) or sampled <= 0:
        reasons.append("Die Beobachtbarkeit ist nicht ausreichend belegt.")
    elif isinstance(impaired, int) and impaired > 0:
        reasons.append("Teile des Beobachtungsfensters sind eingeschränkt.")

    return deepcopy({
        "schema": "pilotsuite-daily-brief-v1",
        "zone_id": zone_id,
        "revision": revision,
        "observations": observations[:8],
        "candidate": candidate,
        "withheld_reasons": reasons[:8],
        "excluded": excluded,
        "limits": [
            "Korrelation ist kein Kausalitätsnachweis.",
            "Sensorzustand und physische Messfrische sind getrennt zu bewerten.",
            "Der Alltagsbrief führt keine Home-Assistant-Aktion aus.",
        ],
        "execution": {"allowed": False, "actions": []},
    })
