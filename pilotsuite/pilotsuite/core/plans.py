"""Dry-run plans and the intentionally closed transaction boundary."""

from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import time
import uuid
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pilotsuite import VERSION
from pilotsuite.domain.policies import evaluate_plan

from .audit import AuditLog, redact
from .selections import InvalidSelection, SelectionConflict
from .review_notes import ReviewNotesMixin, notes_view
from .review_compass import build_review_compass

DRAFT_TEXT_FIELDS = ('title', 'goal', 'trigger', 'conditions', 'exceptions', 'manual_override')
TARGET_DOMAINS = {'light', 'switch', 'fan', 'climate', 'cover', 'media_player'}
MAX_DRAFTS = 100


class InvalidPlan(ValueError):
    pass


class ReadOnlyRelease(RuntimeError):
    pass


class PlanStore(ReviewNotesMixin):
    def __init__(self, data_dir: Path, audit: AuditLog, context=None) -> None:
        self._path = data_dir / "plans.jsonl"
        self._audit = audit
        self._lock = asyncio.Lock()
        self._context = context
        data_dir.mkdir(parents=True, exist_ok=True)

    async def drafts(self, zone_id, inventory):
        return await asyncio.to_thread(self._drafts, zone_id, inventory)

    def _draft_basis(self, db, zone_id, inventory):
        if not db.execute('SELECT 1 FROM habitus_zones WHERE zone_id=?', (zone_id,)).fetchone():
            raise InvalidSelection('Unknown zone')
        selected = self._context.selections._read(db, zone_id)
        if selected['revision'] != inventory['revision']:
            raise SelectionConflict('Zone changed; reload before reviewing drafts')
        report = self._context._report_in_transaction(db, zone_id, time.time())
        targets = {i['entity_id'] for i in inventory['items']
                   if selected['decisions'].get(i['entity_id']) == 'relevant'
                   and i['entity_id'].split('.')[0] in TARGET_DOMAINS}
        return selected['revision'], {p['id']: p for p in report['patterns']}, targets, report

    @staticmethod
    def _draft_view(row, basis):
        revision, patterns, targets = basis[:3]
        pattern = patterns.get(row[2])
        fields = json.loads(row[7])
        source_status = ('pattern_missing' if pattern is None else
                         'zone_changed' if row[3] != revision else 'current')
        missing = [key for key in ('goal', 'trigger', 'conditions', 'manual_override') if not fields[key].strip()]
        if not fields['target_ids']: missing.append('target_ids')
        unavailable = sorted(set(fields['target_ids']) - targets)
        return {'id': row[0], 'zone_id': row[1], 'pattern_id': row[2],
                'source_revision': row[3], 'revision': row[4], 'created_at': row[5],
                'updated_at': row[6], 'fields': fields, 'source_status': source_status,
                'state': 'needs_review' if source_status != 'current' or unavailable else
                         'incomplete' if missing else 'ready_for_review',
                'missing_fields': missing, 'unavailable_targets': unavailable,
                # Derived now, never persisted or treated as an execution plan.
                'current_pattern': pattern,
                'automation_check': 'not_checked', 'risk': 'not_assessed',
                'execution': {'allowed': False, 'reason': 'draft_only', 'actions': []}}

    def _draft_with_notes(self, db, row, basis, inventory):
        draft = self._draft_view(row, basis)
        draft['review_notes'] = notes_view(db, draft, basis[0])
        draft['review_compass'] = build_review_compass(draft, inventory, basis[3])
        return draft

    def _drafts(self, zone_id, inventory):
        with closing(sqlite3.connect(self._context.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            basis = self._draft_basis(db, zone_id, inventory)
            rows = db.execute('SELECT * FROM routine_drafts WHERE zone_id=? ORDER BY updated DESC, id', (zone_id,)).fetchall()
            return [self._draft_with_notes(db, row, basis, inventory) for row in rows]

    async def create_draft(self, zone_id, pattern_id, zone_revision, inventory):
        if not isinstance(pattern_id, str) or not pattern_id or len(pattern_id) > 128:
            raise InvalidSelection('Invalid pattern identity')
        if type(zone_revision) is not int or zone_revision != inventory['revision']:
            raise SelectionConflict('Zone changed; reload before creating a draft')
        return await asyncio.to_thread(self._create_draft, zone_id, pattern_id, inventory)

    def _create_draft(self, zone_id, pattern_id, inventory):
        with closing(sqlite3.connect(self._context.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            basis = self._draft_basis(db, zone_id, inventory)
            if pattern_id not in basis[1]:
                raise InvalidSelection('Pattern expired or unknown; reload')
            existing = db.execute('SELECT * FROM routine_drafts WHERE zone_id=? AND pattern_id=?', (zone_id, pattern_id)).fetchone()
            if existing: return self._draft_with_notes(db, existing, basis, inventory)
            if db.execute('SELECT COUNT(*) FROM routine_drafts').fetchone()[0] >= MAX_DRAFTS:
                raise InvalidSelection('Draft limit reached; remove an unneeded draft first')
            fields = {key: '' for key in DRAFT_TEXT_FIELDS}
            fields.update(title='Neue Routine', target_ids=[])
            stamp = datetime.now(UTC).isoformat()
            row = (str(uuid.uuid4()), zone_id, pattern_id, basis[0], 1, stamp, stamp, json.dumps(fields))
            db.execute('INSERT INTO routine_drafts VALUES (?,?,?,?,?,?,?,?)', row)
            return self._draft_with_notes(db, row, basis, inventory)

    async def save_draft(self, zone_id, draft_id, payload, inventory):
        if (not isinstance(payload, dict) or set(payload) != {'revision', 'zone_revision', 'fields', 'refresh_source'}
                or type(payload['revision']) is not int or payload['revision'] < 1
                or type(payload['refresh_source']) is not bool):
            raise InvalidSelection('Draft requires revision, zone_revision, fields and refresh_source')
        if type(payload['zone_revision']) is not int or payload['zone_revision'] != inventory['revision']:
            raise SelectionConflict('Zone changed; reload before saving the draft')
        fields = payload['fields']
        if not isinstance(fields, dict) or set(fields) != set(DRAFT_TEXT_FIELDS) | {'target_ids'}:
            raise InvalidSelection('Invalid draft fields; executable actions are not supported')
        if any(not isinstance(fields[key], str) or len(fields[key]) > (120 if key == 'title' else 1000)
               for key in DRAFT_TEXT_FIELDS) or not fields['title'].strip():
            raise InvalidSelection('Draft title/text missing or too long')
        ids = fields['target_ids']
        if not isinstance(ids, list) or len(ids) > 20 or any(not isinstance(e, str) or len(e) > 255 for e in ids):
            raise InvalidSelection('Invalid target list')
        normalized = {key: fields[key].strip() for key in DRAFT_TEXT_FIELDS}
        normalized['target_ids'] = sorted(set(ids))
        return await asyncio.to_thread(self._save_draft, zone_id, draft_id, payload['revision'],
                                       normalized, payload['refresh_source'], inventory)

    def _save_draft(self, zone_id, draft_id, revision, fields, refresh_source, inventory):
        with closing(sqlite3.connect(self._context.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            basis = self._draft_basis(db, zone_id, inventory)
            row = db.execute('SELECT * FROM routine_drafts WHERE id=? AND zone_id=?', (draft_id, zone_id)).fetchone()
            if not row: raise InvalidSelection('Unknown draft in this zone')
            if row[4] != revision:
                raise SelectionConflict('Draft changed in another session; reload before saving')
            old_targets = set(json.loads(row[7])['target_ids'])
            if set(fields['target_ids']) - old_targets - basis[2]:
                raise InvalidSelection('New targets must be confirmed relevant entities in this zone')
            if refresh_source and row[2] not in basis[1]:
                raise InvalidSelection('Pattern expired; source cannot be refreshed')
            source_revision = basis[0] if refresh_source else row[3]
            db.execute('UPDATE routine_drafts SET revision=?, source_revision=?, updated=?, fields=? WHERE id=?',
                       (revision+1, source_revision, datetime.now(UTC).isoformat(), json.dumps(fields), draft_id))
            return self._draft_with_notes(db, db.execute('SELECT * FROM routine_drafts WHERE id=?', (draft_id,)).fetchone(), basis, inventory)

    async def delete_draft(self, zone_id, draft_id, revision, review_revision=None):
        if type(revision) is not int or revision < 1: raise InvalidSelection('Invalid draft revision')
        if review_revision is not None and (type(review_revision) is not int or review_revision < 0):
            raise InvalidSelection('Invalid review revision')
        await asyncio.to_thread(self._delete_draft, zone_id, draft_id, revision, review_revision)

    def _delete_draft(self, zone_id, draft_id, revision, review_revision=None):
        with closing(sqlite3.connect(self._context.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT revision FROM routine_drafts WHERE id=? AND zone_id=?', (draft_id, zone_id)).fetchone()
            if not row: raise InvalidSelection('Unknown draft in this zone')
            if row[0] != revision: raise SelectionConflict('Draft changed; reload before removing')
            notes = db.execute('SELECT revision FROM routine_review_notes WHERE draft_id=?', (draft_id,)).fetchone()
            current_review = notes[0] if notes else 0
            if (review_revision is None and current_review) or (review_revision is not None and review_revision != current_review):
                raise SelectionConflict('Review notes changed; reload before removing the draft')
            db.execute('DELETE FROM routine_review_notes WHERE draft_id=?', (draft_id,))
            db.execute('DELETE FROM routine_drafts WHERE id=?', (draft_id,))

    async def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        scope = payload.get("scope", [])
        actions = payload.get("actions", [])
        if not isinstance(scope, list) or not all(isinstance(item, str) for item in scope):
            raise InvalidPlan("scope must be a list of strings")
        if not isinstance(actions, list) or not all(isinstance(item, dict) for item in actions):
            raise InvalidPlan("actions must be a list of objects")
        plan = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
            "release": VERSION,
            "description": str(payload.get("description", "Dry-run plan"))[:500],
            "scope": sorted(set(scope)),
            "actions": redact(actions),
            "state": "denied",
        }
        plan["policy"] = evaluate_plan(plan)
        encoded = json.dumps(plan, separators=(",", ":"), sort_keys=True)
        async with self._lock:
            await asyncio.to_thread(self._append_sync, encoded)
        await self._audit.append(
            "plan.created",
            outcome="denied",
            details={"plan_id": plan["id"], "policy": plan["policy"]},
            correlation_id=plan["id"],
        )
        return plan

    async def apply(self, plan_id: str) -> None:
        await self._audit.append(
            "transaction.apply_rejected",
            outcome="denied",
            details={"plan_id": plan_id, "release": VERSION},
            correlation_id=plan_id,
        )
        raise ReadOnlyRelease(
            f"PilotSuite {VERSION} cannot execute Home Assistant mutations"
        )

    def _append_sync(self, encoded: str) -> None:
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
            handle.flush()
            os.fsync(handle.fileno())
