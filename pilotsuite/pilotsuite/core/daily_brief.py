"""Bounded daily brief; a projection of existing reviews, never a new learner.

Promotion is deliberately narrower than access to the evidence workbench. A
withheld daily candidate does not delete a pattern or change user preference.
"""
from __future__ import annotations

import math
import re
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

MAX_SAFE_INTEGER = 2**53 - 1
MAX_INVENTORY = 2000
MAX_REVIEWS = 200
MAX_SOURCES = 20
ENTITY_ID = re.compile(r"[a-z0-9_]+\.[a-z0-9_]+\Z")
ROLE_NAMES = {
    "motion": "Bewegung", "occupancy": "Präsenz", "presence": "Präsenz",
    "temperature": "Temperatur", "humidity": "Luftfeuchte",
    "illuminance": "Helligkeit", "light": "Licht", "other": "Weitere",
}


def _mapping(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _integer(value: Any, minimum: int = 0) -> bool:
    # bool is an int subclass in Python, but never a count or revision here.
    return type(value) is int and minimum <= value <= MAX_SAFE_INTEGER


def _identity(value: Any) -> bool:
    return (isinstance(value, str) and 0 < len(value) <= 128
            and value == value.strip() and all(c.isprintable() for c in value))


def _ids(value: Any) -> set[str] | None:
    if not isinstance(value, list) or len(value) > MAX_SOURCES:
        return None
    if any(not isinstance(item, str) or len(item) > 255 or not ENTITY_ID.fullmatch(item)
           for item in value):
        return None
    result = set(value)
    return result if len(result) == len(value) else None


def _title(value: Any) -> str:
    if not isinstance(value, str):
        return "Bestehendes Muster prüfen"
    # Bound work as well as output; do not copy arbitrary upstream objects.
    cleaned = "".join(c for c in value[:480] if c.isprintable()).strip()
    return cleaned[:240] or "Bestehendes Muster prüfen"


def _append(items: list[str], message: str) -> None:
    if message not in items:
        items.append(message)


def _coverage(report: dict) -> tuple[str, list[str], list[str], dict]:
    coverage = _mapping(report.get("coverage"))
    keys = ("sampled_slots", "impaired_slots", "unobserved_slots_between_checks")
    if any(not _integer(coverage.get(key)) for key in keys):
        return "unknown", ["Die Beobachtbarkeit ist nicht ausreichend oder widerspruchsfrei belegt."], [], {}
    counts = {key: coverage[key] for key in keys}
    sampled, impaired, gaps = (counts[key] for key in keys)
    if not sampled or impaired >= sampled:
        return "unknown", ["Keine Stichprobe ohne gemeldete Einschränkung belegt die Beobachtbarkeit."], [], counts
    # Older reports omit this optional partition. When present it must agree
    # with the sampled/impaired totals, rather than silently overriding them.
    if "ready_only_slots" in coverage:
        ready_only = coverage["ready_only_slots"]
        if not _integer(ready_only) or ready_only + impaired != sampled:
            return "unknown", ["Die Zählungen der Zonenstichproben widersprechen sich."], [], counts
        counts["ready_only_slots"] = ready_only
    cautions = []
    if impaired:
        cautions.append("Ein Teil der Zonenstichproben meldet Einschränkungen; keine lückenlose Beobachtung.")
    if gaps:
        cautions.append("Zwischen Prüfungen fehlen Stichproben; daraus folgt keine Abwesenheit oder Inaktivität.")
    return "partial" if cautions else "sampled", [], cautions, counts


def _inventory(items: list) -> tuple[dict, dict]:
    by_id: dict[str, dict] = {}
    seen: set[str] = set()
    for raw in items[:MAX_INVENTORY]:
        item = _mapping(raw)
        identity = item.get("entity_id")
        if not isinstance(identity, str) or len(identity) > 255 or not ENTITY_ID.fullmatch(identity):
            continue
        if identity in seen:
            # Conflicting duplicates must not become current by list order.
            by_id.pop(identity, None)
            continue
        seen.add(identity)
        by_id[identity] = item
    counts: dict[str, int] = {}
    for item in by_id.values():
        if item.get("decision") != "relevant":
            continue
        role = item.get("suggested_role")
        label = ROLE_NAMES.get(role, ROLE_NAMES["other"]) if isinstance(role, str) else ROLE_NAMES["other"]
        counts[label] = counts.get(label, 0) + 1
    return by_id, counts


def _evidence(review: dict) -> tuple[dict | None, dict | None]:
    """Validate existing evidence shape and alignment, not detection thresholds."""
    stats = _mapping(review.get("statistics"))
    events, days = stats.get("activation_count"), stats.get("distinct_day_count")
    window = _mapping(stats.get("window_local"))
    start, end = window.get("start_hour"), window.get("end_hour")
    timezone, day_group = stats.get("timezone"), stats.get("day_group")
    if (not _integer(events, 1) or not _integer(days, 1) or days > events
            or not _integer(start) or not _integer(end) or not 0 <= start < end <= 24
            or day_group not in ("all", "weekday", "weekend")
            or not isinstance(timezone, str) or len(timezone) > 128):
        return None, None
    try:
        ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        return None, None
    temporal = _mapping(review.get("temporal_check"))
    if (temporal.get("state") != "reobserved"
            or temporal.get("timezone") != timezone
            or temporal.get("day_group") != day_group
            or type(temporal.get("start_hour")) is not int
            or temporal["start_hour"] != start):
        return None, None
    count_keys = ("training_events", "training_days", "later_events", "later_days")
    if any(not _integer(temporal.get(key), 1) for key in count_keys):
        return None, None
    if (temporal["training_days"] > temporal["training_events"]
            or temporal["later_days"] > temporal["later_events"]
            or temporal["training_events"] + temporal["later_events"] > events):
        return None, None
    # A split may cut a local calendar day: never require disjoint day counts.
    # But each section must be a subset of the retained observation days.
    if max(temporal["training_days"], temporal["later_days"]) > days:
        return None, None
    if (temporal["training_events"] + temporal["later_events"] == events
            and temporal["training_days"] + temporal["later_days"] < days):
        return None, None
    bounds = [temporal.get(key) for key in ("start", "split_at", "end")]
    if any(type(value) not in (int, float) or not 0 <= value <= MAX_SAFE_INTEGER
           or not math.isfinite(value) for value in bounds):
        return None, None
    if not bounds[0] < bounds[1] < bounds[2]:
        return None, None
    safe_stats = {"activation_count": events, "distinct_day_count": days,
                  "day_group": day_group, "timezone": timezone,
                  "window_local": {"start_hour": start, "end_hour": end}}
    safe_temporal = {key: temporal[key] for key in count_keys}
    safe_temporal.update(state="reobserved", start=bounds[0], split_at=bounds[1], end=bounds[2])
    return safe_stats, safe_temporal


def _candidate(review: dict, inventory: dict, by_id: dict,
               roles: set[str], collecting: set[str]) -> tuple[dict | None, str | None]:
    execution = _mapping(review.get("execution"))
    preference, state = review.get("preference"), review.get("state")
    if (review.get("schema") != "pilotsuite-review-v1"
            or review.get("risk") != "read_only"
            or execution.get("allowed") is not False or execution.get("actions") != []
            or preference not in (None, "accepted")
            or state != ("review_requested" if preference == "accepted" else "unreviewed")):
        return None, "Ein Prüfbericht hat keine eindeutige, rein lesende Grundlage."
    sources = _ids(review.get("sources"))
    if (not sources or not sources <= roles or not sources <= collecting
            or any(source not in by_id or by_id[source].get("decision") != "relevant"
                   or by_id[source].get("state") not in ("on", "off") for source in sources)):
        return None, "Musterquellen passen nicht vollständig zur bestätigten, derzeit auswertbaren Präsenzgruppe."
    statistics, temporal = _evidence(review)
    if statistics is None:
        return None, "Passende frühere und spätere Musterbelege sind nicht ausreichend bestätigt; eine Lücke beweist keine Inaktivität."
    return {
        "pattern_id": review["pattern_id"], "title": _title(review.get("title")),
        "state": state, "preference": preference, "navigation": "pattern_workbench",
        "basis_kind": "retained_review", "source_ids": sorted(sources),
        "basis": {"zone_id": inventory["zone_id"], "revision": inventory["revision"]},
        "statistics": statistics, "temporal": temporal,
        "execution": {"allowed": False, "actions": []},
    }, None


def build_daily_brief(inventory: dict, report: dict) -> dict:
    """Return a detached, deterministic brief without I/O, writes or clock reads."""
    inventory = _mapping(inventory)
    zone_id, revision = inventory.get("zone_id"), inventory.get("revision")
    if not _identity(zone_id) or not _integer(revision):
        raise ValueError("invalid zone projection")
    report = _mapping(report)
    config = _mapping(report.get("config"))
    reasons: list[str] = []
    if not _integer(report.get("revision")) or report["revision"] != revision:
        reasons.append("Der Zonenbericht gehört nicht zur aktuellen Auswahlrevision.")
    if report.get("zone_id", zone_id) != zone_id:
        reasons.append("Der Zonenbericht gehört nicht zur ausgewählten Zone.")
    if inventory.get("enabled") is not True or report.get("enabled") is not True:
        reasons.append("Die Zone ist pausiert oder nicht eindeutig aktiviert.")
    if config.get("learning") is not True:
        reasons.append("Lernen ist ausgeschaltet oder nicht eindeutig freigegeben; aufbewahrte Belege bleiben erhalten.")
    collection = report.get("collection_state")
    if collection != "collecting":
        states = {"off": "Lernen ist ausgeschaltet.", "paused": "Beobachtung ist pausiert.",
                  "disconnected": "Die Home-Assistant-Verbindung ist nicht bereit.",
                  "no_source": "Es gibt keine freigegebene Lernquelle."}
        reasons.append(states.get(collection, "Der Sammlungszustand ist nicht bestätigt.")
                       if isinstance(collection, str) else "Der Sammlungszustand ist nicht bestätigt.")
    roles = _ids(_mapping(config.get("roles")).get("presence"))
    collecting = _ids(report.get("collecting_sources"))
    if report.get("eligible") is not True or not roles or not collecting:
        reasons.append("Die bestätigte Präsenzgruppe und ihre auswertbaren Quellen sind nicht vollständig belegt.")
    coverage_state, coverage_reasons, cautions, coverage = _coverage(report)
    reasons.extend(coverage_reasons)
    raw_items, raw_reviews = inventory.get("items"), report.get("reviews")
    if not isinstance(raw_items, list) or not isinstance(raw_reviews, list):
        reasons.append("Inventar oder Prüfberichte liegen nicht in einer auswertbaren Form vor.")
    items = raw_items if isinstance(raw_items, list) else []
    reviews = raw_reviews if isinstance(raw_reviews, list) else []
    truncated = len(items) > MAX_INVENTORY or len(reviews) > MAX_REVIEWS
    if truncated:
        reasons.append("Die begrenzte Projektion ist unvollständig; daraus wird kein Kandidat ausgewählt.")
    by_id, role_counts = _inventory(items)
    confirmed_count = sum(role_counts.values())
    summary = (", ".join(f"{count}× {role}" for role, count in sorted(role_counts.items()))
               if role_counts else "Keine bestätigten Entitäten im ausgewerteten Zoneninventar.")
    observations = [{"kind": "inventory", "summary": summary,
                     "confirmed_entities": confirmed_count, "truncated": len(items) > MAX_INVENTORY}]

    # Scope before preference: never count another zone's rejection or deferral.
    groups: dict[str, list[dict]] = {}
    unusable: list[str] = []
    for raw in reviews[:MAX_REVIEWS]:
        review = _mapping(raw)
        if (review.get("zone_id") != zone_id or not _integer(review.get("revision"))
                or review["revision"] != revision):
            continue
        identity = review.get("pattern_id")
        if not _identity(identity):
            _append(unusable, "Ein Muster hat keine gültige Identität.")
            continue
        groups.setdefault(identity, []).append(review)
    excluded = {"dismissed": 0, "deferred": 0}
    candidates = []
    for identity in sorted(groups):
        matching = groups[identity]
        if any(r.get("state") == "dismissed" or r.get("preference") == "rejected" for r in matching):
            excluded["dismissed"] += 1
            continue
        if any(r.get("state") == "deferred" or r.get("preference") == "later" for r in matching):
            excluded["deferred"] += 1
            continue
        if len(matching) != 1:
            _append(unusable, "Mehrere Prüfberichte verwenden dieselbe Musteridentität; keine willkürliche Auswahl.")
            continue
        candidate, reason = _candidate(matching[0], inventory, by_id, roles or set(), collecting or set())
        if candidate is not None:
            candidates.append(candidate)
        elif reason:
            _append(unusable, reason)
    chosen = candidates[0] if candidates and not reasons else None
    if chosen is None and not reasons:
        reasons.extend(unusable)
        if not reasons:
            reasons.append("Kein aktuelles, nicht zurückgestelltes Muster ist für den Alltagsbrief ausreichend belegt.")
    if chosen is not None and unusable:
        cautions.append("Weitere Muster wurden wegen unklarer oder unpassender Grundlagen nicht ausgewählt.")
    return {
        "schema": "pilotsuite-daily-brief-v1", "zone_id": zone_id, "revision": revision,
        "observations": observations, "candidate": chosen, "withheld_reasons": reasons[:8],
        "cautions": cautions[:8], "excluded": excluded, "coverage_state": coverage_state,
        "coverage": coverage, "truncated": truncated,
        "limits": [
            "Aufbewahrte Musterbelege, keine Tagesprognose und kein nachgewiesener Komfortgewinn.",
            "Inventar und Zonenstichproben belegen keine physische Messfrische oder lückenlose Anwesenheit.",
            "Korrelation ist kein Kausalitätsnachweis; vorhandene Automationen bleiben gesondert zu prüfen.",
            "Der Alltagsbrief führt keine Home-Assistant-Aktion aus und erteilt keine Freigabe.",
        ],
        "execution": {"allowed": False, "actions": []},
    }
