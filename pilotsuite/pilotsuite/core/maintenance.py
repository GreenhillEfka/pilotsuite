"""Version/update presentation. Native HA owns installation and full app recovery."""
from __future__ import annotations

import re
import math
from pathlib import Path

from pilotsuite import VERSION

APP_SLUG = "0d79c5e8_pilotsuite"
APP_PATH = f"/hassio/addon/{APP_SLUG}/info"
BACKUP_PATH = "/config/backup/overview"
HELPERS_PATH = "/config/helpers"
VERSION_RE = re.compile(r"[0-9A-Za-z.+_-]{1,80}")


def release_history():
    """Bundled release notes, not a fabricated installation history."""
    bundled = Path(__file__).resolve().parents[1] / "CHANGELOG.md"
    development = Path(__file__).resolve().parents[2] / "CHANGELOG.md"
    source = bundled if bundled.is_file() else development
    try:
        text = source.read_text(encoding="utf-8")[:128000]
    except OSError:
        return []
    matches = list(re.finditer(r"^## \[([^\]]+)\](?: - ([0-9-]+))?\s*$", text, re.MULTILINE))
    rows = []
    for i, match in enumerate(matches[:3]):
        version = match[1]
        if not VERSION_RE.fullmatch(version):
            continue
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        rows.append({"version": version, "date": match[2], "running": version == VERSION,
                     "notes": text[match.end():end].strip()[:8000]})
    return rows


def update_view(registry, states, *, fresh):
    """Authenticate identity with platform + unique ID; never with a display name."""
    matches = [row for row in registry if row.get("platform") == "hassio"
               and row.get("unique_id") == APP_SLUG + "_version_latest"
               and row.get("entity_id", "").startswith("update.") and not row.get("disabled_by")]
    result = {"state": "unknown", "installed_version": VERSION, "latest_version": None,
              "source": "ha_update_entity", "install_mode": "native_home_assistant_confirmation",
              "app_path": APP_PATH, "install_available": False}
    if not fresh or len(matches) != 1:
        return result
    state = states.get(matches[0]["entity_id"], {})
    attrs = state.get("attributes", {})
    if not isinstance(attrs, dict):
        return result
    installed, latest = attrs.get("installed_version"), attrs.get("latest_version")
    if any(not isinstance(v, str) or not VERSION_RE.fullmatch(v) for v in (installed, latest)):
        return result
    result.update(entity_id=matches[0]["entity_id"], latest_version=latest)
    if installed != VERSION:
        return dict(result, state="version_mismatch")
    progress = attrs.get("in_progress")
    if type(progress) not in (bool, int, float) or (type(progress) in (int, float) and (not math.isfinite(progress) or not 0 <= progress <= 100)):
        return result
    if progress is True or type(progress) in (int, float) and 0 < progress <= 100:
        return dict(result, state="installing")
    if state.get("state") == "on" and installed != latest:
        return dict(result, state="available", install_available=True)
    if state.get("state") == "off" and latest == installed:
        return dict(result, state="current")
    if state.get("state") == "off" and attrs.get("skipped_version") == latest:
        return dict(result, state="skipped")
    return result
