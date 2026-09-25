#!/usr/bin/env python3
"""Read-only source identity check. Does not certify CI, backups or deployment."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALPHA = re.compile(r"0\.1\.0-alpha\.([1-9][0-9]*)")
MARKERS = {
    "pilotsuite/config.yaml": r"^version:\s*(\S+)\s*$",
    "pilotsuite/pilotsuite/__init__.py": r'^VERSION = "([^"]+)"$',
    "pilotsuite/Dockerfile": r'^ARG BUILD_VERSION="([^"]+)"$',
    "pilotsuite/DOCS.md": r"^- Release: `([^`]+)`$",
}


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def inspect_release(root: Path, ref: str) -> dict:
    # Resolve once: subsequent reads cannot mix moving branch tips or working files.
    commit = git(root, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")
    read = lambda path: git(root, "show", f"{commit}:{path}")
    version = read("VERSION")
    if not ALPHA.fullmatch(version):
        raise ValueError("unsupported alpha version")
    for path, pattern in MARKERS.items():
        matches = re.findall(pattern, read(path), re.MULTILINE)
        if matches != [version]:
            raise ValueError(f"release marker mismatch: {path}")
    for path in ("CHANGELOG.md", "pilotsuite/CHANGELOG.md"):
        if not re.search(rf"^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$",
                         read(path), re.MULTILINE):
            raise ValueError(f"missing versioned changelog: {path}")
    return {"version": version, "commit": commit,
            "tree": git(root, "rev-parse", f"{commit}^{{tree}}"),
            "app_tree": git(root, "rev-parse", f"{commit}:pilotsuite")}


def preflight(root: Path, candidate: str, published: str) -> dict:
    current = inspect_release(root, candidate)
    previous_commit = git(root, "rev-parse", "--verify", "--end-of-options",
                          f"{published}^{{commit}}")
    # Historical releases can have old marker defects; compare their canonical VERSION.
    previous_version = git(root, "show", f"{previous_commit}:VERSION")
    previous = ALPHA.fullmatch(previous_version)
    if not previous or int(ALPHA.fullmatch(current["version"])[1]) <= int(previous[1]):
        raise ValueError("candidate must be newer than the last published release")
    git(root, "merge-base", "--is-ancestor", previous_commit, current["commit"])
    return {"source_check": "passed", "candidate": current,
            "previous_release": {"version": previous_version, "commit": previous_commit},
            "deployment_authorized": False,
            "remaining_gates": ["exact-commit CI", "completed scoped backup and rollback",
                                "Store version/source match", "live and Ingress acceptance"]}



def check_source(root: Path, candidate: str, published: str) -> dict:
    """CI permits unchanged published app trees, never silent version reuse."""
    current = inspect_release(root, candidate)
    previous_commit = git(root, "rev-parse", "--verify", "--end-of-options",
                          f"{published}^{{commit}}")
    previous_version = git(root, "show", f"{previous_commit}:VERSION")
    if current["version"] != previous_version:
        return preflight(root, current["commit"], previous_commit)
    git(root, "merge-base", "--is-ancestor", previous_commit, current["commit"])
    previous_tree = git(root, "rev-parse", f"{previous_commit}:pilotsuite")
    if current["app_tree"] != previous_tree:
        raise ValueError("changed application tree reuses a published version")
    return {"source_check": "unchanged_published_application", "candidate": current,
            "previous_release": {"version": previous_version, "commit": previous_commit},
            "deployment_authorized": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, help="committed release candidate")
    parser.add_argument("--published", required=True, help="last published release commit, not installed version")
    parser.add_argument("--allow-unchanged", action="store_true",
                        help="CI only: allow an identical published app tree")
    args = parser.parse_args()
    try:
        check = check_source if args.allow_unchanged else preflight
        result = check(ROOT, args.candidate, args.published)
    except (ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Release source check failed: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
