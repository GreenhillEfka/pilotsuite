#!/usr/bin/env python3
"""Fast repository invariants used locally and in CI."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "pilotsuite"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"0\.1\.0-alpha\.[1-9][0-9]*", version):
        fail(f"unexpected alpha version: {version}")

    repository = (ROOT / "repository.yaml").read_text(encoding="utf-8")
    config = (APP / "config.yaml").read_text(encoding="utf-8")
    if scalar(repository, "name") != "PilotSuite":
        fail("repository name must be PilotSuite")
    if scalar(config, "version") != version:
        fail("VERSION and config.yaml differ")
    if scalar(config, "slug") != "pilotsuite":
        fail("app slug must be pilotsuite")
    if scalar(config, "hassio_api") != "false":
        fail("alpha must not request Supervisor mutation API access")
    if scalar(config, "homeassistant_api") != "true":
        fail("Home Assistant API proxy permission is required")
    if scalar(config, "ingress") != "true":
        fail("Ingress must be enabled")
    forbidden = ["build.yaml", "build.json"]
    for name in forbidden:
        if (APP / name).exists():
            fail(f"deprecated build metadata present: {name}")
    print("PilotSuite repository invariants: OK")


def scalar(document: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*([^#\n]+?)\s*$", document, re.MULTILINE)
    return match.group(1).strip().strip('"\'') if match else None


if __name__ == "__main__":
    main()
