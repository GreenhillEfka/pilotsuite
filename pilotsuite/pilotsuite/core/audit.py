"""Append-only, redacted PilotSuite audit records."""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SENSITIVE_KEYS = {"token", "secret", "password", "authorization", "api_key"}


class AuditLog:
    def __init__(self, data_dir: Path, retention: int) -> None:
        self._path = data_dir / "audit.jsonl"
        self._retention = retention
        self._lock = asyncio.Lock()
        data_dir.mkdir(parents=True, exist_ok=True)

    async def append(
        self,
        event: str,
        *,
        outcome: str = "ok",
        details: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            "outcome": outcome,
            "correlation_id": correlation_id,
            "details": redact(details or {}),
        }
        encoded = json.dumps(record, separators=(",", ":"), sort_keys=True)
        async with self._lock:
            await asyncio.to_thread(self._append_sync, encoded)
        return record

    async def tail(self, limit: int = 100) -> list[dict[str, Any]]:
        bounded = max(1, min(limit, 500))
        async with self._lock:
            return await asyncio.to_thread(self._tail_sync, bounded)

    def _append_sync(self, encoded: str) -> None:
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self._trim_sync()

    def _tail_sync(self, limit: int) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        lines = self._path.read_text(encoding="utf-8").splitlines()[-limit:]
        result: list[dict[str, Any]] = []
        for line in lines:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                result.append(value)
        return result

    def _trim_sync(self) -> None:
        lines = self._path.read_text(encoding="utf-8").splitlines()
        if len(lines) <= self._retention:
            return
        kept = lines[-self._retention :]
        fd, temporary_name = tempfile.mkstemp(
            prefix="audit-", suffix=".jsonl", dir=self._path.parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write("\n".join(kept) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, self._path)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "<redacted>" if key.lower() in SENSITIVE_KEYS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return [redact(item) for item in value]
    return value

