"""Privacy-bounded attribution of Home Assistant event contexts.

Home Assistant context identifiers are correlation aids, not durable identities.
PilotSuite therefore keeps them only in memory for a short period and persists
only a conservative origin category with consented activity evidence.
"""

from __future__ import annotations

from collections import OrderedDict
from time import monotonic
from typing import Any


USER_CONTEXT = "user_context"
PARENTED_SERVICE_CONTEXT = "parented_service_context"
SERVICE_CONTEXT = "service_context"
DERIVED_CONTEXT = "derived_context"
UNKNOWN = "unknown"
ALLOWED_ORIGINS = {
    USER_CONTEXT,
    PARENTED_SERVICE_CONTEXT,
    SERVICE_CONTEXT,
    DERIVED_CONTEXT,
    UNKNOWN,
}


class EventAttribution:
    """Correlate service and state contexts without retaining their identifiers."""

    def __init__(self, *, ttl_seconds: float = 120, limit: int = 2048) -> None:
        self.ttl_seconds = max(1.0, ttl_seconds)
        self.limit = max(1, limit)
        self._service_contexts: OrderedDict[str, tuple[float, str]] = OrderedDict()

    def clear(self) -> None:
        self._service_contexts.clear()

    def observe_service_event(
        self, event: dict[str, Any], *, now: float | None = None
    ) -> bool:
        """Remember only the opaque context link and a coarse origin category."""
        context = event.get("context")
        if not isinstance(context, dict):
            return False
        context_id = context.get("id")
        if not isinstance(context_id, str) or not context_id:
            return False
        stamp = monotonic() if now is None else now
        self._prune(stamp)
        origin = (
            USER_CONTEXT
            if context.get("user_id")
            else PARENTED_SERVICE_CONTEXT
            if context.get("parent_id")
            else SERVICE_CONTEXT
        )
        self._service_contexts[context_id] = (stamp, origin)
        self._service_contexts.move_to_end(context_id)
        while len(self._service_contexts) > self.limit:
            self._service_contexts.popitem(last=False)
        return True

    def classify_state(
        self, state: dict[str, Any], *, now: float | None = None
    ) -> str:
        context = state.get("context")
        if not isinstance(context, dict):
            return UNKNOWN
        if context.get("user_id"):
            return USER_CONTEXT
        stamp = monotonic() if now is None else now
        self._prune(stamp)
        for key in (context.get("id"), context.get("parent_id")):
            if isinstance(key, str) and key in self._service_contexts:
                return self._service_contexts[key][1]
        return DERIVED_CONTEXT if context.get("parent_id") else UNKNOWN

    def _prune(self, now: float) -> None:
        cutoff = now - self.ttl_seconds
        while self._service_contexts:
            _, (stamp, _) = next(iter(self._service_contexts.items()))
            if stamp >= cutoff:
                break
            self._service_contexts.popitem(last=False)
