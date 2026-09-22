from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pilotsuite.core.audit import AuditLog
from pilotsuite.core.plans import PlanStore, ReadOnlyRelease
from pilotsuite.domain.policies import evaluate_plan


class PolicyTests(unittest.TestCase):
    def test_every_plan_is_denied_in_alpha(self) -> None:
        decision = evaluate_plan(
            {"actions": [{"domain": "light", "service": "turn_on"}]}
        )
        self.assertFalse(decision["allowed"])
        self.assertEqual("read_only_release", decision["code"])


class AuditAndPlanTests(unittest.IsolatedAsyncioTestCase):
    async def test_audit_redacts_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            audit = AuditLog(Path(temp_dir), retention=100)
            await audit.append(
                "test",
                details={"token": "sensitive", "nested": {"password": "hidden"}},
            )
            record = (await audit.tail(1))[0]
            self.assertEqual("<redacted>", record["details"]["token"])
            self.assertEqual("<redacted>", record["details"]["nested"]["password"])

    async def test_plan_is_persisted_but_apply_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            audit = AuditLog(path, retention=100)
            store = PlanStore(path, audit)
            plan = await store.create(
                {
                    "description": "Test",
                    "scope": ["erdkeller"],
                    "actions": [{"domain": "fan", "service": "turn_on"}],
                }
            )
            self.assertEqual("denied", plan["state"])
            with self.assertRaises(ReadOnlyRelease):
                await store.apply(plan["id"])


if __name__ == "__main__":
    unittest.main()

