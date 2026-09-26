#!/usr/bin/env python3
"""Fast repository invariants used locally and in CI."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "pilotsuite"
API_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
DOCUMENTED_ROUTE = re.compile(
    r"^\| `(?P<method>GET|POST|PUT|PATCH|DELETE)` "
    r"\| `(?P<path>/api/v1[^`]*)` \|",
    re.MULTILINE,
)


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
    validate_api_inventory()
    print("PilotSuite repository invariants: OK")


def validate_api_inventory() -> None:
    """Keep the human API inventory aligned with explicit route registrations."""
    registered: list[tuple[str, str]] = []
    for source in (APP / "pilotsuite").rglob("*.py"):
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        constants: dict[str, str] = {}
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)):
                constants[node.targets[0].id] = node.value.value
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr.startswith("add_") and node.args):
                continue
            method = node.func.attr.removeprefix("add_").upper()
            value = node.args[0]
            route = (value.value if isinstance(value, ast.Constant) and isinstance(value.value, str)
                     else constants.get(value.id) if isinstance(value, ast.Name) else None)
            if method not in API_METHODS or not route or not route.startswith("/api/v1"):
                continue
            canonical = re.sub(r"{([A-Za-z_][A-Za-z0-9_]*):[^{}]+}", r"{\1}", route)
            registered.append((method, canonical))

    document = (ROOT / "docs" / "API.md").read_text(encoding="utf-8")
    documented = [match.groups() for match in DOCUMENTED_ROUTE.finditer(document)]
    if len(registered) != len(set(registered)):
        fail("duplicate registered API route")
    if len(documented) != len(set(documented)):
        fail("duplicate documented API route")
    if set(registered) != set(documented):
        missing = sorted(set(registered) - set(documented))
        extra = sorted(set(documented) - set(registered))
        fail(f"docs/API.md route drift; missing={missing!r}, extra={extra!r}")
    print(f"API contract inventory: {len(registered)} method/path pairs")


def scalar(document: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*([^#\n]+?)\s*$", document, re.MULTILINE)
    return match.group(1).strip().strip('"\'') if match else None


if __name__ == "__main__":
    main()
