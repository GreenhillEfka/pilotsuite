"""Final deterministic policy gate."""

from __future__ import annotations

from typing import Any

from pilotsuite import READ_ONLY_RELEASE, VERSION


def evaluate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    action_count = len(plan.get("actions", [])) if isinstance(plan.get("actions"), list) else 0
    if READ_ONLY_RELEASE:
        return {
            "allowed": False,
            "code": "read_only_release",
            "reason": f"PilotSuite {VERSION} cannot execute Home Assistant mutations",
            "action_count": action_count,
        }
    return {
        "allowed": False,
        "code": "no_policy_match",
        "reason": "No explicit allow policy matched this plan",
        "action_count": action_count,
    }

