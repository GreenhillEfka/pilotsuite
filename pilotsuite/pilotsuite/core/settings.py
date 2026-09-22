"""Runtime settings loaded from Home Assistant's options file."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class Settings:
    data_dir: Path
    options_path: Path
    log_level: str = "info"
    golden_zone_area_ids: tuple[str, ...] = ("erdkeller",)
    refresh_interval_seconds: int = 30
    audit_retention: int = 5000
    host: str = "0.0.0.0"
    port: int = 8099
    ha_ws_url: str = "ws://supervisor/core/websocket"
    supervisor_token: str = ""

    @classmethod
    def load(cls) -> "Settings":
        data_dir = Path(os.getenv("PILOTSUITE_DATA_DIR", "/data"))
        options_path = Path(os.getenv("PILOTSUITE_OPTIONS", "/data/options.json"))
        options = _read_options(options_path)

        area_ids = options.get("golden_zone_area_ids", ["erdkeller"])
        if not isinstance(area_ids, list):
            area_ids = ["erdkeller"]
        normalized_areas = tuple(
            sorted({str(item).strip() for item in area_ids if str(item).strip()})
        ) or ("erdkeller",)

        return cls(
            data_dir=data_dir,
            options_path=options_path,
            log_level=_log_level(options.get("log_level", "info")),
            golden_zone_area_ids=normalized_areas,
            refresh_interval_seconds=_bounded_int(
                options.get("refresh_interval_seconds"), 30, 10, 3600
            ),
            audit_retention=_bounded_int(
                options.get("audit_retention"), 5000, 100, 50000
            ),
            host=os.getenv("PILOTSUITE_HOST", "0.0.0.0"),
            port=_bounded_int(os.getenv("PILOTSUITE_PORT"), 8099, 1, 65535),
            ha_ws_url=os.getenv(
                "PILOTSUITE_HA_WS_URL", "ws://supervisor/core/websocket"
            ),
            supervisor_token=os.getenv("SUPERVISOR_TOKEN", ""),
        )


def _read_options(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return {}
        value = json.loads(raw)
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(number, maximum))


def _log_level(value: Any) -> str:
    normalized = str(value).lower()
    return normalized if normalized in {"trace", "debug", "info", "warning", "error"} else "info"

