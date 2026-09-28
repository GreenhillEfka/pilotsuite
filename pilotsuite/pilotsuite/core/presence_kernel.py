"""Deterministic, deadline-owned presence kernel and synthetic scenario replay.

The kernel owns explanation state only. It proposes bounded actions but never calls
Home Assistant. Execution authority belongs to existing callers, never to the kernel.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import math
from typing import Any

from .selections import InvalidSelection

STATES = {"occupied", "grace", "vacant", "unknown"}
SOURCE_STATES = {"on", "off", "unknown"}
SCENARIOS = {
    "continuous_then_clear": "Dauerpräsenz, Nachlauf und Ablauf",
    "pulse_refresh": "Bewegungsimpuls erneuert den Nachlauf",
    "restart_during_grace": "Neustart verlängert den Nachlauf nicht",
    "unknown_source": "Unklare Quelle verhindert falsche Abwesenheit",
    "dependency_unknown": "Unklare Gruppenabhängigkeit bleibt unbekannt",
}


def timestamp(value):
    """Parse only explicit, finite timezone-aware observation instants."""
    if not isinstance(value, str):
        return None
    try:
        stamp = datetime.fromisoformat(value)
        number = stamp.timestamp() if stamp.tzinfo is not None else None
        return number if number is not None and math.isfinite(number) else None
    except (ValueError, TypeError, OverflowError, OSError):
        return None


@dataclass(frozen=True)
class PresenceCheckpoint:
    state: str = "unknown"
    generation: int = 0
    deadline: float | None = None
    last_activity_at: float | None = None
    reason: str = "not_observed"


@dataclass(frozen=True)
class PresenceTransition:
    checkpoint: PresenceCheckpoint
    proposed_actions: tuple[str, ...]
    explanation: str


def validate_checkpoint(value: PresenceCheckpoint | dict[str, Any] | None) -> PresenceCheckpoint:
    if value is None:
        return PresenceCheckpoint()
    if isinstance(value, PresenceCheckpoint):
        point = value
    elif isinstance(value, dict) and set(value) == {
            "state", "generation", "deadline", "last_activity_at", "reason"}:
        point = PresenceCheckpoint(**value)
    else:
        raise InvalidSelection("Ungültiger Präsenz-Zwischenstand")
    if point.state not in STATES or type(point.generation) is not int or point.generation < 0:
        raise InvalidSelection("Ungültiger Präsenz-Zwischenstand")
    for stamp in (point.deadline, point.last_activity_at):
        if stamp is not None and (isinstance(stamp, bool) or not isinstance(stamp, (int, float))
                                  or not math.isfinite(stamp)):
            raise InvalidSelection("Ungültiger Präsenz-Zeitbezug")
    if not isinstance(point.reason, str) or not point.reason or len(point.reason) > 80:
        raise InvalidSelection("Ungültiger Präsenzgrund")
    return point


def _next(previous: PresenceCheckpoint, *, state: str, deadline: float | None,
          last_activity_at: float | None, reason: str) -> PresenceCheckpoint:
    changed = (previous.state, previous.deadline, previous.last_activity_at, previous.reason) != (
        state, deadline, last_activity_at, reason)
    return PresenceCheckpoint(state, previous.generation + int(changed), deadline,
                              last_activity_at, reason)


def advance_presence(previous, *, continuous, pulse=False, dependencies_confirmed=True,
                     manual_cancel=False, now, grace_seconds=300, restart=False):
    """Advance one checkpoint without I/O or inferred authority.

    ``continuous`` contains already-normalized required source states.  A pulse is
    activity evidence, not a claim of continuous occupancy.  ``restart`` is an
    explanation marker only and therefore cannot renew a durable deadline.
    """
    point = validate_checkpoint(previous)
    if (isinstance(now, bool) or not isinstance(now, (int, float)) or not math.isfinite(now) or
            type(grace_seconds) is not int or not 1 <= grace_seconds <= 86400 or
            type(pulse) is not bool or type(dependencies_confirmed) is not bool or
            type(manual_cancel) is not bool or type(restart) is not bool or
            not isinstance(continuous, (list, tuple)) or not continuous or
            any(value not in SOURCE_STATES for value in continuous)):
        raise InvalidSelection("Ungültige Präsenzbeobachtung")
    now = float(now)
    if manual_cancel:
        current = _next(point, state="unknown", deadline=None,
                        last_activity_at=point.last_activity_at,
                        reason="manual_cancel_requires_policy")
        return PresenceTransition(current, (), "Manueller Abbruch ist keine Abwesenheitsmessung.")
    if not dependencies_confirmed:
        current = _next(point, state="unknown", deadline=point.deadline,
                        last_activity_at=point.last_activity_at,
                        reason="source_dependencies_unknown")
        return PresenceTransition(current, (), "Gruppen und Mitglieder werden nicht als unabhängige Belege gezählt.")
    if "on" in continuous:
        current = _next(point, state="occupied", deadline=None,
                        last_activity_at=now, reason="continuous_presence")
        return PresenceTransition(current, ("timer.cancel", "owner.on"),
                                  "Eine bestätigte Dauerquelle belegt aktuelle Präsenz.")
    if "unknown" in continuous:
        current = _next(point, state="unknown", deadline=point.deadline,
                        last_activity_at=point.last_activity_at, reason="required_source_unknown")
        return PresenceTransition(current, (), "Mindestens eine erforderliche Quelle ist unklar; frei wird nicht behauptet.")
    if pulse:
        current = _next(point, state="grace", deadline=now + grace_seconds,
                        last_activity_at=now, reason="activity_pulse")
        return PresenceTransition(current, ("timer.start", "owner.on"),
                                  "Ein Aktivitätsimpuls erneuert den Nachlauf, beweist aber keine Dauerpräsenz.")
    if point.deadline is not None:
        if point.deadline > now:
            reason = "restart_preserves_deadline" if restart else "grace_deadline_pending"
            current = _next(point, state="grace", deadline=point.deadline,
                            last_activity_at=point.last_activity_at, reason=reason)
            return PresenceTransition(current, ("owner.on",),
                                      "Der bestehende Nachlauf bleibt unverändert; er wird nicht neu gestartet.")
        current = _next(point, state="vacant", deadline=None,
                        last_activity_at=point.last_activity_at, reason="deadline_elapsed_all_clear")
        return PresenceTransition(current, ("owner.off",),
                                  "Der gespeicherte Nachlauf ist abgelaufen und alle erforderlichen Quellen sind klar.")
    if point.state == "occupied":
        current = _next(point, state="grace", deadline=now + grace_seconds,
                        last_activity_at=point.last_activity_at, reason="all_clear_starts_grace")
        return PresenceTransition(current, ("timer.start", "owner.on"),
                                  "Nach belegter Präsenz startet bei klaren Quellen genau ein Nachlauf.")
    if point.state == "vacant":
        current = _next(point, state="vacant", deadline=None,
                        last_activity_at=point.last_activity_at, reason="all_clear_remains_vacant")
        return PresenceTransition(current, (), "Alle Quellen bleiben klar; der freie Zustand bleibt bestehen.")
    current = _next(point, state="unknown", deadline=None,
                    last_activity_at=point.last_activity_at, reason="no_recent_presence_basis")
    return PresenceTransition(current, (), "Ohne vorherigen Präsenzbeleg wird beim Start kein neuer Nachlauf erfunden.")


def checkpoint_dict(point: PresenceCheckpoint) -> dict[str, Any]:
    return asdict(validate_checkpoint(point))


def replay_scenario(name: str, *, grace_seconds: int = 300) -> dict[str, Any]:
    if name not in SCENARIOS:
        raise InvalidSelection("Unbekanntes Präsenzszenario")
    point = PresenceCheckpoint()
    if name == "continuous_then_clear":
        observations = [
            (0, {"continuous": ["on"]}),
            (30, {"continuous": ["off"]}),
            (331, {"continuous": ["off"]}),
        ]
    elif name == "pulse_refresh":
        observations = [
            (0, {"continuous": ["off"], "pulse": True}),
            (250, {"continuous": ["off"], "pulse": True}),
            (400, {"continuous": ["off"]}),
            (551, {"continuous": ["off"]}),
        ]
    elif name == "restart_during_grace":
        observations = [
            (0, {"continuous": ["on"]}),
            (10, {"continuous": ["off"]}),
            (100, {"continuous": ["off"], "restart": True}),
            (311, {"continuous": ["off"]}),
        ]
    elif name == "unknown_source":
        observations = [
            (0, {"continuous": ["on", "off"]}),
            (20, {"continuous": ["off", "unknown"]}),
            (400, {"continuous": ["off", "unknown"]}),
        ]
    else:
        observations = [(0, {"continuous": ["off", "off"], "dependencies_confirmed": False})]
    steps = []
    for at, observation in observations:
        transition = advance_presence(point, now=at, grace_seconds=grace_seconds, **observation)
        point = transition.checkpoint
        steps.append({"at_seconds": at, **checkpoint_dict(point),
                      "proposed_actions": list(transition.proposed_actions),
                      "explanation": transition.explanation})
    return {"id": name, "title": SCENARIOS[name], "grace_seconds": grace_seconds,
            "steps": steps, "limitations": [
                "Synthetisches Szenario; keine Haushaltsbeobachtung.",
                "Vorgeschlagene Aktionen werden nicht ausgeführt.",
                "Präsenzzustand und Ausführungsrecht bleiben getrennt.",
            ]}
