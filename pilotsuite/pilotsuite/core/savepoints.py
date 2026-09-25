"""PilotSuite configuration savepoints, owned by PlanStore, never HA backups.

Only zone definitions, selection decisions, roles and detector settings are saved.
Restore is an additive, preview-bound SQLite transaction, always paused and without
learning consent. Evidence, review text, HA configuration, secrets and app binaries
are neither exported nor replaced. The source database must already be healthy.
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import re
import sqlite3
import stat
import uuid
from contextlib import closing
from datetime import UTC, datetime

from pilotsuite import VERSION
from .context import ContextStore, ROLE_KINDS, validate_detector
from .selections import InvalidSelection, SelectionConflict, SelectionStore
from .zones import ZoneStore

SCHEMA = "pilotsuite-config-savepoint-v1"
MAX_BYTES = 4 * 1024 * 1024
MAX_POINTS = 64
ID_RE = re.compile(r"[0-9a-f]{32}")
HASH_RE = re.compile(r"[0-9a-f]{64}")


def encoded(value):
    try:
        data = json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, RecursionError, UnicodeError) as exc:
        raise InvalidSelection("Speicherpunkt enthält ungültige Daten") from exc
    if len(data) > MAX_BYTES:
        raise InvalidSelection("Speicherpunkt überschreitet die Größenbegrenzung")
    return data


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def validate_zones(zones):
    if not isinstance(zones, list) or len(zones) > 100:
        raise InvalidSelection("Ungültiger Speicherpunktumfang")
    seen = set()
    for zone in zones:
        if not isinstance(zone, dict) or set(zone) != {"zone_id", "revision", "definition", "decisions", "roles", "detector"}:
            raise InvalidSelection("Unbekanntes Speicherpunktformat")
        zid = zone["zone_id"]
        SelectionStore._zone(zid)
        if zid in seen or type(zone["revision"]) is not int or not 0 <= zone["revision"] < 2**52:
            raise InvalidSelection("Doppelte Zone oder ungültige Revision")
        seen.add(zid)
        ZoneStore.validate(zone["definition"])
        decisions, roles = zone["decisions"], zone["roles"]
        if not isinstance(decisions, dict) or len(decisions) > 10000 or any(
                not isinstance(e, str) or not 1 <= len(e) <= 255 or d not in {"relevant", "ignored", "unreviewed"}
                for e, d in decisions.items()):
            raise InvalidSelection("Ungültige Quellenauswahl")
        if not isinstance(roles, dict) or not set(roles) <= set(ROLE_KINDS) or any(
                not isinstance(ids, list) or len(ids) > 20 or any(
                    not isinstance(e, str) or not 1 <= len(e) <= 255 for e in ids)
                for ids in roles.values()):
            raise InvalidSelection("Ungültige Rollen")
        validate_detector(zone["detector"])
    encoded(zones)
    return zones


def capture(db):
    # The schema contract is deliberate: newer databases cannot be restored by an old binary.
    if db.execute("PRAGMA user_version").fetchone()[0] != 8:
        raise InvalidSelection("Datenbankschema nicht unterstützt; native App-Sicherung verwenden")
    zones = []
    for zid, definition in db.execute("SELECT zone_id, definition FROM habitus_zones ORDER BY zone_id"):
        selected = SelectionStore._read(db, zid)
        config = ContextStore.read(db, zid)
        zones.append({"zone_id": zid, "revision": selected["revision"],
                      "definition": json.loads(definition), "decisions": selected["decisions"],
                      "roles": config["roles"], "detector": config["detector"]})
    return validate_zones(zones)


async def finish_thread(fn, *args):
    """Keep caller's locks until a disk/DB operation completes even on disconnect."""
    task = asyncio.create_task(asyncio.to_thread(fn, *args))
    try:
        return await asyncio.shield(task)
    except asyncio.CancelledError:
        try:
            await task
        finally:
            raise


class SavepointsMixin:
    # `_path`, `_context` and `_lock` belong to the existing PlanStore.
    @property
    def savepoint_dir(self):
        return self._path.parent / "savepoints"

    def _point_paths(self):
        directory = self.savepoint_dir
        if directory.is_symlink():
            raise InvalidSelection("Unsicheres Speicherpunktverzeichnis")
        if not directory.exists():
            return []
        paths = []
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.name.endswith(".json"):
                    paths.append(directory / entry.name)
                    if len(paths) > MAX_POINTS:
                        raise InvalidSelection("Zu viele Speicherpunkte; keine automatische Löschung")
        return paths

    @staticmethod
    def _point_meta(point):
        return {k: point[k] for k in ("id", "schema", "created_at", "version", "label", "reason", "sha256")} | {
            "zone_count": len(point["zones"]), "valid": True, "scope": "pilotsuite_zone_configuration"}

    def _read_point(self, point_id):
        if not isinstance(point_id, str) or not ID_RE.fullmatch(point_id):
            raise InvalidSelection("Ungültige Speicherpunkt-ID")
        self._point_paths()
        path = self.savepoint_dir / (point_id + ".json")
        try:
            with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), "rb") as stream:
                info = os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
                    raise InvalidSelection("Ungültige Speicherpunktdatei")
                raw = stream.read(MAX_BYTES + 1)
            point = json.loads(raw)
            if not isinstance(point, dict) or set(point) != {
                    "id", "schema", "created_at", "version", "label", "reason", "sha256", "zones"}:
                raise InvalidSelection("Ungültiges Speicherpunktformat")
            expected = point.pop("sha256")
            if not isinstance(expected, str) or not hmac.compare_digest(digest(point), expected):
                raise InvalidSelection("Speicherpunkt-Prüfsumme stimmt nicht")
            point["sha256"] = expected
            if point["schema"] != SCHEMA or point["id"] != point_id:
                raise InvalidSelection("Speicherpunktformat oder Identität passt nicht")
            if not isinstance(point["label"], str) or len(point["label"]) > 100:
                raise InvalidSelection("Ungültiger Speicherpunktname")
            stamp = datetime.fromisoformat(point["created_at"])
            if stamp.tzinfo is None:
                raise InvalidSelection("Speicherpunktzeit ohne Zeitzone")
            validate_zones(point["zones"])
            return point
        except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
            raise InvalidSelection("Speicherpunkt fehlt, ist beschädigt oder nicht kompatibel") from exc

    def _write_point(self, zones, label, reason):
        paths = self._point_paths()
        if len(paths) >= MAX_POINTS - (1 if reason == "manual" else 0):
            raise InvalidSelection("Speicherpunktlimit erreicht; bestehende Punkte bleiben erhalten")
        validate_zones(zones)
        self.savepoint_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        if self.savepoint_dir.is_symlink():
            raise InvalidSelection("Unsicheres Speicherpunktverzeichnis")
        point = {"id": uuid.uuid4().hex, "schema": SCHEMA, "created_at": datetime.now(UTC).isoformat(),
                 "version": VERSION, "label": label, "reason": reason, "zones": zones}
        point["sha256"] = digest(point)
        raw = encoded(point)
        temp = self.savepoint_dir / (point["id"] + ".tmp")
        dest = temp.with_suffix(".json")
        try:
            with os.fdopen(os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600), "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            # Never overwrite an existing point, even on an unexpected ID collision.
            os.link(temp, dest, follow_symlinks=False)
            temp.unlink()
            fd = os.open(self.savepoint_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            return self._point_meta(self._read_point(point["id"]))
        finally:
            temp.unlink(missing_ok=True)

    async def savepoints(self):
        async with self._lock:
            return await finish_thread(self._list_points)

    def _list_points(self):
        rows = []
        for path in self._point_paths():
            point_id = path.stem
            if not ID_RE.fullmatch(point_id):
                continue
            try:
                rows.append(self._point_meta(self._read_point(point_id)))
            except InvalidSelection:
                rows.append({"id": point_id, "valid": False, "label": "Beschädigt oder inkompatibel", "created_at": ""})
        return sorted(rows, key=lambda row: (row["created_at"], row["id"]), reverse=True)

    async def create_savepoint(self, label):
        if not isinstance(label, str) or not 1 <= len(label.strip()) <= 100:
            raise InvalidSelection("Name muss 1 bis 100 Zeichen enthalten")
        async with self._lock:
            return await finish_thread(self._create_savepoint, label.strip())

    def _create_savepoint(self, label):
        with closing(sqlite3.connect(self._context.path, timeout=10)) as db, db:
            db.execute("BEGIN")
            return self._write_point(capture(db), label, "manual")

    async def preview_restore(self, point_id):
        async with self._lock:
            return await finish_thread(self._preview_restore, point_id)

    def _preview_restore(self, point_id):
        point = self._read_point(point_id)
        with closing(sqlite3.connect(self._context.path, timeout=10)) as db, db:
            db.execute("BEGIN")
            current = capture(db)
        by_id = {z["zone_id"]: z for z in current}
        return {"id": point_id, "sha256": point["sha256"], "basis": digest(current),
                "zones": [{"zone_id": z["zone_id"], "name": z["definition"]["name"],
                           "operation": "replace_configuration" if z["zone_id"] in by_id else "recreate_paused"}
                          for z in point["zones"]],
                "preserved_zone_count": len(set(by_id) - {z["zone_id"] for z in point["zones"]}),
                "consequences": ["Gespeicherte Zonendefinitionen, Auswahl und Rollen werden zurückgesetzt.",
                                 "Betroffene Zonen starten pausiert; Lernen muss neu freigegeben werden.",
                                 "Vorher wird automatisch ein neuer Konfigurations-Speicherpunkt erstellt.",
                                 "Keine Hausautomation, kein HA-Helfer und keine App-Version wird verändert.",
                                 "Lernbelege und Prüftexte werden nicht zurückgespielt; neuere zusätzliche Zonen bleiben erhalten."],
                "ha_execution": False}

    async def restore_savepoint(self, point_id, payload):
        if not isinstance(payload, dict) or set(payload) != {"sha256", "basis", "confirm_paused_restore"}:
            raise InvalidSelection("Vorschau-Prüfsummen und ausdrückliche Bestätigung erforderlich")
        if payload["confirm_paused_restore"] is not True or any(
                not isinstance(payload[k], str) or not HASH_RE.fullmatch(payload[k]) for k in ("sha256", "basis")):
            raise InvalidSelection("Wiederherstellung muss nach Vorschau ausdrücklich bestätigt werden")
        async with self._lock:
            return await finish_thread(self._restore_savepoint, point_id, payload)

    def _restore_savepoint(self, point_id, payload):
        point = self._read_point(point_id)
        if not hmac.compare_digest(point["sha256"], payload["sha256"]):
            raise SelectionConflict("Speicherpunkt geändert; Vorschau erneut laden")
        receipt_key = "config_restore_" + digest([point_id, payload["sha256"], payload["basis"]])
        with closing(sqlite3.connect(self._context.path, timeout=10)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            current = capture(db)
            receipt = db.execute("SELECT value FROM zone_meta WHERE key=?", (receipt_key,)).fetchone()
            if receipt:
                return dict(json.loads(receipt[0]), replayed=True)
            if not hmac.compare_digest(digest(current), payload["basis"]):
                raise SelectionConflict("Konfiguration seit Vorschau geändert; nichts wiederhergestellt")
            before = self._write_point(current, "Vor Wiederherstellung", "before_restore")
            revisions = {z["zone_id"]: z["revision"] for z in current}
            expected = {}
            for zone in point["zones"]:
                zid = zone["zone_id"]
                revision = max(revisions.get(zid, 0), zone["revision"]) + 1
                definition = {**zone["definition"], "enabled": False}
                config = {"roles": zone["roles"], "detector": zone["detector"],
                          "learning": False, "consented_at": None, "context_learning": False,
                          "context_consented_at": None}
                db.execute("INSERT OR REPLACE INTO habitus_zones VALUES (?,?)", (zid, json.dumps(definition)))
                db.execute("INSERT OR REPLACE INTO zones VALUES (?,?)", (zid, revision))
                db.execute("DELETE FROM selections WHERE zone_id=?", (zid,))
                db.executemany("INSERT INTO selections VALUES (?,?,?)", [(zid, e, d) for e, d in zone["decisions"].items()])
                db.execute("INSERT OR REPLACE INTO selection_modes VALUES (?,1)", (zid,))
                db.execute("INSERT OR REPLACE INTO zone_context VALUES (?,?)", (zid, json.dumps(config)))
                db.execute("INSERT INTO selection_journal(zone_id,revision,changes) VALUES (?,?,?)",
                           (zid, revision, json.dumps({"config_restore": point_id, "before": before["id"]})))
                expected[zid] = {**zone, "definition": definition, "revision": revision}
            restored = {z["zone_id"]: z for z in capture(db)}
            if any(restored.get(zid) != value for zid, value in expected.items()):
                raise RuntimeError("Konfigurations-Rückleseprüfung fehlgeschlagen")
            if any(ContextStore.read(db, zid)["learning"] for zid in expected):
                raise RuntimeError("Wiederherstellung darf Lernen nicht aktivieren")
            result = {"restored": len(expected), "paused": True, "before_savepoint": before["id"],
                      "id": point_id, "ha_execution": False, "replayed": False}
            db.execute("INSERT INTO zone_meta VALUES (?,?)", (receipt_key, json.dumps(result)))
            self._context.selections.prune_journal(db)
            return result
