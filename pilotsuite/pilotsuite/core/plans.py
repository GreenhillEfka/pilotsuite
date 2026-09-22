"""Dry-run plans and the intentionally closed transaction boundary."""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pilotsuite import VERSION
from pilotsuite.domain.policies import evaluate_plan

from .audit import AuditLog, redact


class InvalidPlan(ValueError):
    pass


class ReadOnlyRelease(RuntimeError):
    pass


class PlanStore:
    def __init__(self, data_dir: Path, audit: AuditLog) -> None:
        self._path = data_dir / "plans.jsonl"
        self._audit = audit
        self._lock = asyncio.Lock()
        data_dir.mkdir(parents=True, exist_ok=True)

    async def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        scope = payload.get("scope", [])
        actions = payload.get("actions", [])
        if not isinstance(scope, list) or not all(isinstance(item, str) for item in scope):
            raise InvalidPlan("scope must be a list of strings")
        if not isinstance(actions, list) or not all(isinstance(item, dict) for item in actions):
            raise InvalidPlan("actions must be a list of objects")
        plan = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
            "release": VERSION,
            "description": str(payload.get("description", "Dry-run plan"))[:500],
            "scope": sorted(set(scope)),
            "actions": redact(actions),
            "state": "denied",
        }
        plan["policy"] = evaluate_plan(plan)
        encoded = json.dumps(plan, separators=(",", ":"), sort_keys=True)
        async with self._lock:
            await asyncio.to_thread(self._append_sync, encoded)
        await self._audit.append(
            "plan.created",
            outcome="denied",
            details={"plan_id": plan["id"], "policy": plan["policy"]},
            correlation_id=plan["id"],
        )
        return plan

    async def apply(self, plan_id: str) -> None:
        await self._audit.append(
            "transaction.apply_rejected",
            outcome="denied",
            details={"plan_id": plan_id, "release": VERSION},
            correlation_id=plan_id,
        )
        raise ReadOnlyRelease(
            f"PilotSuite {VERSION} cannot execute Home Assistant mutations"
        )

    def _append_sync(self, encoded: str) -> None:
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
            handle.flush()
            os.fsync(handle.fileno())

