"""PilotSuite-owned selection preferences; never writes Home Assistant data."""

from __future__ import annotations

import asyncio
import json
import re
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path
from typing import Any


class InvalidSelection(ValueError):
    pass


class SelectionConflict(RuntimeError):
    pass


class SelectionStore:
    """Atomic patch writes with revision checks and an in-transaction journal.

    Missing rows mean unreviewed. Rows survive entity disappearance; no inferred
    rename or delete may transfer an explicit decision to a different entity.
    """

    def __init__(self, data_dir: Path, journal_limit: int = 5000):
        self.path = data_dir / "selections.sqlite3"
        self.journal_limit = max(1, journal_limit)

    def prune_journal(self, db: sqlite3.Connection) -> None:
        db.execute('DELETE FROM selection_journal WHERE id NOT IN (SELECT id FROM selection_journal ORDER BY id DESC LIMIT ?)', (self.journal_limit,))

    async def initialize(self) -> None:
        await asyncio.to_thread(self._initialize)

    def _initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as db, db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version > 4:
                raise RuntimeError("Selection database schema is newer than this release")
            if version == 4:
                return
            if version:
                backup = self.path.with_name(f"selections.v{version}.{uuid.uuid4().hex}.bak")
                with closing(sqlite3.connect(backup)) as target:
                    db.backup(target)
            elif db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchone():
                raise RuntimeError("Unrecognized selection database; refusing to overwrite")
            db.execute('BEGIN IMMEDIATE')
            if version == 0:
                db.execute('CREATE TABLE zones (zone_id TEXT PRIMARY KEY, revision INTEGER NOT NULL)')
                db.execute("CREATE TABLE selections (zone_id TEXT NOT NULL, entity_id TEXT NOT NULL, decision TEXT NOT NULL CHECK(decision IN ('relevant','ignored','unreviewed')), PRIMARY KEY(zone_id, entity_id))")
                db.execute('CREATE TABLE selection_journal (id INTEGER PRIMARY KEY, zone_id TEXT NOT NULL, revision INTEGER NOT NULL, changes TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
            if version <= 1:
                db.execute('CREATE TABLE selection_modes (zone_id TEXT PRIMARY KEY, active INTEGER NOT NULL CHECK(active IN (0,1)))')
            if version <= 2:
                db.execute('CREATE TABLE habitus_zones (zone_id TEXT PRIMARY KEY, definition TEXT NOT NULL)')
                db.execute('CREATE TABLE zone_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            db.execute('CREATE TABLE zone_context (zone_id TEXT PRIMARY KEY, config TEXT NOT NULL)')
            db.execute('CREATE TABLE activity_evidence (zone_id TEXT NOT NULL, entity_id TEXT NOT NULL, occurred REAL NOT NULL, origin TEXT NOT NULL, PRIMARY KEY(zone_id, entity_id, occurred))')
            db.execute('CREATE TABLE pattern_feedback (zone_id TEXT NOT NULL, pattern_id TEXT NOT NULL, decision TEXT NOT NULL, updated REAL NOT NULL, PRIMARY KEY(zone_id, pattern_id))')
            # Consent is never inferred; old automatic modes no longer bypass decisions.
            db.execute('UPDATE selection_modes SET active=1')
            db.execute('PRAGMA user_version=4')

    @staticmethod
    def _zone(zone_id: str) -> None:
        if not isinstance(zone_id, str) or not zone_id.strip() or len(zone_id) > 128:
            raise InvalidSelection("zone_id must be a non-empty string of at most 128 characters")

    async def get(self, zone_id: str) -> dict[str, Any]:
        self._zone(zone_id)
        return await asyncio.to_thread(self._get, zone_id)

    @staticmethod
    def _read(db: sqlite3.Connection, zone_id: str) -> dict[str, Any]:
        row = db.execute("SELECT revision FROM zones WHERE zone_id=?", (zone_id,)).fetchone()
        records = db.execute("SELECT entity_id, decision FROM selections WHERE zone_id=? ORDER BY entity_id", (zone_id,)).fetchall()
        mode = db.execute("SELECT active FROM selection_modes WHERE zone_id=?", (zone_id,)).fetchone()
        return {"zone_id": zone_id, "revision": row[0] if row else 0,
                "decisions": dict(records), "active": True}

    def _get(self, zone_id: str) -> dict[str, Any]:
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("BEGIN")
            return self._read(db, zone_id)

    async def patch(self, zone_id: str, revision: int, changes: Any, active: bool | None = None) -> dict[str, Any]:
        self._zone(zone_id)
        if type(revision) is not int or revision < 0:
            raise InvalidSelection("revision must be a nonnegative integer")
        if active is False:
            raise InvalidSelection("Only confirmed entities may be evaluated")
        if active is not None and type(active) is not bool:
            raise InvalidSelection("active must be a boolean")
        if not isinstance(changes, dict) or len(changes) > 500 or (not changes and active is None):
            raise InvalidSelection("changes must contain 1 to 500 decisions, or an explicit activation change")
        for entity_id, decision in changes.items():
            if not isinstance(entity_id, str) or len(entity_id) > 255 or not re.fullmatch(r"[a-z0-9_]+\.[a-z0-9_]+", entity_id):
                raise InvalidSelection("invalid entity_id")
            if not isinstance(decision, str) or decision not in {"relevant", "ignored", "unreviewed"}:
                raise InvalidSelection("decision must be relevant, ignored or unreviewed")
        return await asyncio.to_thread(self._patch, zone_id, revision, dict(changes), active)

    def _patch(self, zone_id: str, revision: int, changes: dict[str, str], active: bool | None) -> dict[str, Any]:
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            previous = self._read(db, zone_id)
            if previous["revision"] != revision:
                raise SelectionConflict("Selection changed in another session; reload before saving")
            delta = {key: value for key, value in changes.items()
                     if previous["decisions"].get(key, "unreviewed") != value}
            mode_changed = active is not None and active != previous["active"]
            if not delta and not mode_changed:
                return previous
            db.execute("INSERT INTO zones VALUES (?, ?) ON CONFLICT(zone_id) DO UPDATE SET revision=excluded.revision", (zone_id, revision + 1))
            for entity_id, decision in delta.items():
                db.execute("INSERT INTO selections VALUES (?, ?, ?) ON CONFLICT(zone_id, entity_id) DO UPDATE SET decision=excluded.decision", (zone_id, entity_id, decision))
            journal = {key: {"before": previous["decisions"].get(key, "unreviewed"), "after": value} for key, value in delta.items()}
            if mode_changed:
                db.execute("INSERT INTO selection_modes VALUES (?, ?) ON CONFLICT(zone_id) DO UPDATE SET active=excluded.active", (zone_id, int(active)))
                journal["$active"] = {"before": previous["active"], "after": active}
            db.execute("INSERT INTO selection_journal(zone_id, revision, changes) VALUES (?, ?, ?)", (zone_id, revision + 1, json.dumps(journal, sort_keys=True)))
            self.prune_journal(db)
            return self._read(db, zone_id)
