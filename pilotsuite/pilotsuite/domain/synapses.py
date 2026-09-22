"""Versioned rules turning moods into non-executing suggestions."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from typing import Any

from .models import Mood, Suggestion


RULESET_VERSION = "erdkeller-3"


def build_suggestions(
    moods: Iterable[Mood], area_ids: tuple[str, ...], *, zone_name: str | None = None
) -> list[Suggestion]:
    mood_map = {mood.name: mood for mood in moods}
    suggestions: list[Suggestion] = []
    rules = (
        (
            "humidity-high",
            "humidity_high",
            0.35,
            "Feuchte im Erdkeller prüfen",
            "Die mittlere relative Feuchte liegt über dem konservativen Beobachtungsbereich.",
            "medium",
        ),
        (
            "humidity-low",
            "humidity_low",
            0.50,
            "Ungewöhnlich trockene Erdkellerluft prüfen",
            "Die mittlere relative Feuchte ist für den Erdkeller ungewöhnlich niedrig.",
            "low",
        ),
        (
            "temperature-high",
            "temperature_high",
            0.50,
            "Erhöhte Erdkellertemperatur prüfen",
            "Die mittlere Temperatur liegt über dem ersten Beobachtungsbereich.",
            "low",
        ),
        (
            "temperature-low",
            "temperature_low",
            0.50,
            "Frostnähe im Erdkeller prüfen",
            "Die mittlere Temperatur nähert sich dem Frostbereich.",
            "medium",
        ),
        (
            "data-quality",
            "uncertainty",
            0.25,
            "Sensordaten im Erdkeller prüfen",
            "Ein relevanter Anteil der aufgelösten Entitäten liefert keine belastbaren Zustände.",
            "low",
        ),
    )
    for rule_id, mood_name, threshold, title, explanation, risk in rules:
        mood = mood_map.get(mood_name)
        if mood is None or mood.score is None or mood.score < threshold:
            continue
        stable_id = _stable_id(rule_id, area_ids)
        suggestions.append(
            Suggestion(
                id=stable_id,
                rule_id=f"{RULESET_VERSION}:{rule_id}",
                title=(f"{zone_name}: " + {'humidity-high': 'Hohe Feuchte prüfen', 'humidity-low': 'Niedrige Feuchte prüfen', 'temperature-high': 'Erhöhte Temperatur prüfen', 'temperature-low': 'Frostnähe prüfen', 'data-quality': 'Sensordaten prüfen'}[rule_id]) if zone_name else title,
                explanation=explanation.replace('für den Erdkeller', 'für das Erdkeller-Regelprofil') if zone_name else explanation,
                confidence=None,
                severity=mood.score,
                risk=risk,
                scope=area_ids,
                evidence=mood.evidence,
                proposed_actions=(),
            )
        )
    return suggestions


def _stable_id(rule_id: str, area_ids: tuple[str, ...]) -> str:
    source = f"{RULESET_VERSION}:{rule_id}:{','.join(sorted(set(area_ids)))}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
