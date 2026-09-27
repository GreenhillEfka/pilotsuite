"""Deterministic daylight/mood preview; pure suggestions without HA actions."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any

from .selections import InvalidSelection


ATMOSPHERES = {
    "neutral": {"offset": 0, "kelvin": 3500},
    "focus": {"offset": 10, "kelvin": 4200},
    "relax": {"offset": -10, "kelvin": 2700},
    "social": {"offset": 0, "kelvin": 3000},
    "movie": {"offset": -20, "kelvin": 2400},
}
PREVIEW_SCENARIOS = {
    "daylight_transition": "Tageslicht wird dunkler und wieder heller",
    "threshold_chatter": "Schwankung an einer Helligkeitsgrenze",
    "manual_override": "Manuelle Bedienung hat Vorrang",
    "lux_unavailable": "Helligkeitsquelle ist nicht verfügbar",
    "night_vacancy": "Nächtliches Verlassen nach bestätigter Präsenz",
    "capability_limits": "Leuchte ohne Helligkeitssteuerung",
    "brightness_unavailable": "Aktuelle Leuchtenhelligkeit ist unbekannt",
}
BANDS = ("dark", "dim", "daylight", "bright", "very_bright")


@dataclass(frozen=True)
class LightingCheckpoint:
    band: str = "unknown"
    candidate_band: str | None = None
    candidate_since: float | None = None
    last_proposal_at: float | None = None
    last_target: int | None = None


@dataclass(frozen=True)
class LightingTransition:
    checkpoint: LightingCheckpoint
    status: str
    desired_brightness: int | None
    proposed_settings: dict[str, Any]
    explanation: str


def _number(value: Any, *, minimum: float | None = None, maximum: float | None = None) -> bool:
    return (not isinstance(value, bool) and isinstance(value, (int, float)) and
            isfinite(value) and (minimum is None or value >= minimum) and
            (maximum is None or value <= maximum))


def _band(lux: float) -> str:
    if lux >= 10000:
        return "very_bright"
    if lux >= 3000:
        return "bright"
    if lux >= 1000:
        return "daylight"
    if lux >= 300:
        return "dim"
    return "dark"


def lighting_target(*, outdoor_lux, occupied, atmosphere="neutral", minimum=15, maximum=85):
    """Return a bounded desired percentage, never an action."""
    if type(occupied) is not bool or not occupied:
        return {"target": None, "reason": "not_occupied", "execution": {"allowed": False}}
    if not _number(outdoor_lux, minimum=0):
        return {"target": None, "reason": "invalid_daylight", "execution": {"allowed": False}}
    if not all(_number(value, minimum=0, maximum=100) for value in (minimum, maximum)) or minimum > maximum:
        raise InvalidSelection("Ungültige Helligkeitsgrenzen")
    if atmosphere not in ATMOSPHERES:
        return {"target": None, "reason": "invalid_atmosphere", "execution": {"allowed": False}}
    weights = {"very_bright": 0, "bright": .20, "daylight": .40, "dim": .65, "dark": 1}
    base = minimum + (maximum - minimum) * weights[_band(float(outdoor_lux))]
    target = max(minimum, min(maximum, base + ATMOSPHERES[atmosphere]["offset"]))
    return {"target": round(target), "reason": "daylight_compensation",
            "inputs": {"outdoor_lux": outdoor_lux, "occupied": occupied,
                       "atmosphere": atmosphere},
            "bounds": {"minimum": minimum, "maximum": maximum},
            "execution": {"allowed": False}}


def should_adjust(current, target, *, deadband=5):
    return (all(_number(value, minimum=0, maximum=100) for value in (current, target)) and
            _number(deadband, minimum=0, maximum=100) and deadband > 0 and
            abs(current - target) >= deadband)


def validate_lighting_checkpoint(value: LightingCheckpoint | dict[str, Any] | None) -> LightingCheckpoint:
    if value is None:
        return LightingCheckpoint()
    if isinstance(value, LightingCheckpoint):
        point = value
    elif isinstance(value, dict) and set(value) == {
            "band", "candidate_band", "candidate_since", "last_proposal_at", "last_target"}:
        point = LightingCheckpoint(**value)
    else:
        raise InvalidSelection("Ungültiger Lichtvorschau-Zwischenstand")
    if point.band not in {*BANDS, "unknown"} or point.candidate_band not in {*BANDS, None}:
        raise InvalidSelection("Ungültiges Helligkeitsband")
    if ((point.candidate_band is None) != (point.candidate_since is None)
            or point.candidate_band == point.band):
        raise InvalidSelection("Inkonsistenter Lichtvorschau-Zwischenstand")
    for stamp in (point.candidate_since, point.last_proposal_at):
        if stamp is not None and not _number(stamp):
            raise InvalidSelection("Ungültiger Lichtvorschau-Zeitbezug")
    if point.last_target is not None and (type(point.last_target) is not int or not 0 <= point.last_target <= 100):
        raise InvalidSelection("Ungültiges letztes Lichtziel")
    return point


def advance_lighting_preview(previous, *, now, presence_state, daylight_lux,
                             daylight_available=True, current_on=True,
                             current_brightness=50, atmosphere="neutral",
                             manual_override=False, night=False, off_when_vacant=False,
                             supports_brightness=True, supports_color_temp=False,
                             minimum_kelvin=2000, maximum_kelvin=6500,
                             minimum=15, maximum=85, stable_seconds=30,
                             minimum_interval=60, deadband=5, maximum_step=15):
    """Advance a synthetic preview checkpoint without I/O, persistence or authority."""
    point = validate_lighting_checkpoint(previous)
    if (not _number(now) or presence_state not in {"occupied", "grace", "vacant", "unknown"}
            or type(daylight_available) is not bool or type(current_on) is not bool
            or type(manual_override) is not bool or type(night) is not bool or type(off_when_vacant) is not bool
            or type(supports_brightness) is not bool or type(supports_color_temp) is not bool
            or atmosphere not in ATMOSPHERES
            or not all(type(value) is int and 1 <= value <= 3600
                       for value in (stable_seconds, minimum_interval, deadband, maximum_step))):
        raise InvalidSelection("Ungültige Lichtvorschau")
    if current_brightness is not None and not _number(current_brightness, minimum=0, maximum=100):
        raise InvalidSelection("Ungültige aktuelle Helligkeit")
    if not all(_number(value, minimum=0, maximum=100) for value in (minimum, maximum)) or minimum > maximum:
        raise InvalidSelection("Ungültige Helligkeitsgrenzen")
    if (type(minimum_kelvin) is not int or type(maximum_kelvin) is not int
            or not 1500 <= minimum_kelvin <= maximum_kelvin <= 10000):
        raise InvalidSelection("Ungültiger Farbtemperaturbereich")
    now = float(now)
    if ((point.candidate_since is not None and point.candidate_since > now)
            or (point.last_proposal_at is not None and point.last_proposal_at > now)):
        raise InvalidSelection("Lichtvorschau-Zeitbezug liegt in der Zukunft")
    if manual_override:
        return LightingTransition(point, "hold", None, {},
                                  "Manuelle Bedienung hat Vorrang; die Vorschau hält an.")
    if presence_state == "unknown":
        return LightingTransition(point, "hold", None, {},
                                  "Unklare Präsenz erlaubt keinen neuen Lichtvorschlag.")
    if presence_state == "vacant":
        if (night or off_when_vacant) and current_on:
            if point.last_proposal_at is not None and now - point.last_proposal_at < minimum_interval:
                return LightingTransition(point, "rate_limited", None, {},
                                          "Der Mindestabstand verhindert einen wiederholten Nachtvorschlag.")
            updated = LightingCheckpoint(point.band, None, None, now, None)
            return LightingTransition(updated, "suggest", None, {"on": False},
                                      "Nach bestätigter Abwesenheit zeigt das freigegebene Abschaltziel einen Vorschlag, keine Ausführung.")
        return LightingTransition(point, "hold", None, {},
                                  "Ohne bestätigte Präsenz wird keine Beleuchtung angehoben.")
    if not daylight_available or not _number(daylight_lux, minimum=0):
        return LightingTransition(point, "hold", None, {},
                                  "Fehlendes Tageslicht ist kein Dunkelheitsbeleg; der Zustand bleibt unverändert.")
    if supports_brightness and current_brightness is None:
        return LightingTransition(point, "input_unavailable", None, {},
                                  "Ohne aktuelle Leuchtenhelligkeit ist keine begrenzte Änderung belegbar.")

    raw_band = _band(float(daylight_lux))
    if point.band != raw_band:
        if point.candidate_band != raw_band:
            updated = LightingCheckpoint(point.band, raw_band, now,
                                         point.last_proposal_at, point.last_target)
            return LightingTransition(updated, "stabilizing", None, {},
                                      "Das neue Helligkeitsband muss erst stabil bleiben.")
        if point.candidate_since is None or now - point.candidate_since < stable_seconds:
            return LightingTransition(point, "stabilizing", None, {},
                                      "Das neue Helligkeitsband ist noch nicht lange genug stabil.")
        point = LightingCheckpoint(raw_band, None, None, point.last_proposal_at, point.last_target)
    elif point.candidate_band is not None:
        point = LightingCheckpoint(point.band, None, None, point.last_proposal_at, point.last_target)

    desired = lighting_target(outdoor_lux=daylight_lux, occupied=True,
                              atmosphere=atmosphere, minimum=minimum, maximum=maximum)["target"]
    if point.last_proposal_at is not None and now - point.last_proposal_at < minimum_interval:
        return LightingTransition(point, "rate_limited", desired, {},
                                  "Der Mindestabstand verhindert schnelle Folgevorschläge.")
    if supports_brightness and current_brightness is not None:
        if not should_adjust(current_brightness, desired, deadband=deadband):
            return LightingTransition(point, "within_deadband", desired, {},
                                      "Die Abweichung liegt innerhalb der Totzone.")
        bounded = round(max(current_brightness - maximum_step,
                            min(current_brightness + maximum_step, desired)))
        settings: dict[str, Any] = {"on": True, "brightness_pct": bounded}
    else:
        settings = {"on": True} if not current_on else {}
    if supports_color_temp:
        settings["color_temp_kelvin"] = max(minimum_kelvin, min(
            maximum_kelvin, ATMOSPHERES[atmosphere]["kelvin"]))
    if not settings:
        return LightingTransition(point, "capability_limited", desired, {},
                                  "Die Zielhelligkeit wird erklärt, aber die Leuchte unterstützt sie nicht.")
    updated = LightingCheckpoint(point.band, None, None, now, desired)
    return LightingTransition(updated, "suggest", desired, settings,
                              "Der Vorschlag ist stabil, zeitlich begrenzt und auf unterstützte Eigenschaften reduziert.")


def replay_lighting_scenario(name: str) -> dict[str, Any]:
    if name not in PREVIEW_SCENARIOS:
        raise InvalidSelection("Unbekanntes Lichtszenario")
    common = {"presence_state": "occupied", "daylight_lux": 1000}
    scenarios = {
        "daylight_transition": [(0, dict(common, daylight_lux=12000)),
            (35, dict(common, daylight_lux=12000)), (50, dict(common, daylight_lux=900)),
            (85, dict(common, daylight_lux=900)), (100, dict(common, daylight_lux=900)),
            (110, dict(common, daylight_lux=1100))],
        "threshold_chatter": [(0, dict(common, daylight_lux=990)),
            (10, dict(common, daylight_lux=1010)), (20, dict(common, daylight_lux=980)),
            (30, dict(common, daylight_lux=1020))],
        "manual_override": [(0, dict(common, daylight_lux=80, manual_override=True))],
        "lux_unavailable": [(0, dict(common, daylight_lux=None, daylight_available=False))],
        "night_vacancy": [(0, dict(common, presence_state="vacant", daylight_lux=0, night=True))],
        "capability_limits": [(0, dict(common, daylight_lux=80, atmosphere="relax",
            supports_brightness=False, supports_color_temp=True)),
            (35, dict(common, daylight_lux=80, atmosphere="relax",
            supports_brightness=False, supports_color_temp=True))],
        "brightness_unavailable": [(0, dict(common, daylight_lux=80,
            current_brightness=None))],
    }
    point = LightingCheckpoint()
    steps = []
    for at, values in scenarios[name]:
        transition = advance_lighting_preview(point, now=at, **values)
        point = transition.checkpoint
        steps.append({"at_seconds": at, **asdict(point), "status": transition.status,
                      "desired_brightness": transition.desired_brightness,
                      "proposed_settings": transition.proposed_settings,
                      "explanation": transition.explanation})
    return {"id": name, "title": PREVIEW_SCENARIOS[name], "steps": steps,
            "policy": {"stable_seconds": 30, "minimum_interval_seconds": 60,
                       "deadband_percentage_points": 5, "maximum_step_percentage_points": 15},
            "limitations": ["Synthetisches Szenario; keine Haushaltsmessung.",
                "Vorgeschlagene Einstellungen werden nicht ausgeführt oder gespeichert.",
                "Lux, Helligkeitsprozent, Atmosphäre und Ausführungsrecht bleiben getrennt."]}
