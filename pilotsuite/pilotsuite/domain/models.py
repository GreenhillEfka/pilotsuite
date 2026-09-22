"""Small serializable domain records."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Neuron:
    entity_id: str
    area_id: str
    kind: str
    value: float | str | bool | None
    unit: str | None
    quality: str
    observed_at: str | None
    name: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Mood:
    name: str
    score: float | None
    evidence: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["evidence"] = list(self.evidence)
        return value


@dataclass(frozen=True, slots=True)
class Suggestion:
    id: str
    rule_id: str
    title: str
    explanation: str
    confidence: float | None
    risk: str
    scope: tuple[str, ...]
    evidence: tuple[dict[str, Any], ...]
    severity: float = 0.0
    proposed_actions: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["scope"] = list(self.scope)
        value["evidence"] = list(self.evidence)
        value["proposed_actions"] = list(self.proposed_actions)
        return value
