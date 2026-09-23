"""PlanStore review notes: user assessment, never evidence or action permission."""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import sqlite3
import time
from contextlib import closing
from datetime import UTC, datetime

from .selections import InvalidSelection, SelectionConflict

MAX_REVIEW_NOTES = 20
MAX_NOTE_LENGTH = 2000
REVIEW_DISPOSITIONS = frozenset({'open', 'needs_change', 'reviewed'})
MAX_INSPECTION_AGE_SECONDS = 30


def validate_note_request(payload, *, deleting=False):
    expected = {'revision', 'zone_revision', 'review_revision', 'automation_id'}
    if not deleting:
        expected |= {'config_fingerprint', 'disposition', 'text'}
    if not isinstance(payload, dict) or set(payload) != expected:
        raise InvalidSelection('Invalid review-note fields')
    for key in ('revision', 'zone_revision', 'review_revision'):
        minimum = 1 if key == 'revision' else 0
        if type(payload[key]) is not int or not minimum <= payload[key] <= 2**53-1:
            raise InvalidSelection('Invalid review-note revision')
    entity = payload['automation_id']
    if (not isinstance(entity, str) or len(entity) > 255
            or not re.fullmatch(r'automation\.[a-z0-9_]+', entity)):
        raise InvalidSelection('Invalid review automation')
    result = dict(payload)
    if not deleting:
        fingerprint = payload['config_fingerprint']
        if not isinstance(fingerprint, str) or not re.fullmatch(r'[0-9a-f]{64}', fingerprint):
            raise InvalidSelection('A configuration fingerprint is required')
        if not isinstance(payload['disposition'], str) or payload['disposition'] not in REVIEW_DISPOSITIONS:
            raise InvalidSelection('Review disposition must be open, needs_change or reviewed')
        text = payload['text']
        if (not isinstance(text, str) or len(text) > MAX_NOTE_LENGTH
                or any(ord(c) < 32 and c not in '\n\t\r' for c in text)
                or any(0xD800 <= ord(c) <= 0xDFFF for c in text)):
            raise InvalidSelection('Invalid review text; maximum 2000 characters')
        result['text'] = text.strip()
    return result


def scope_fingerprint(draft):
    """Bind references, not changing evidence counters or heuristic scores."""
    value = {'pattern_id': draft['pattern_id'],
             'source_ids': sorted((draft.get('current_pattern') or {}).get('sources', [])),
             'target_ids': sorted(draft['fields']['target_ids'])}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def stored_notes(db, draft_id):
    row = db.execute('SELECT revision, records FROM routine_review_notes WHERE draft_id=?', (draft_id,)).fetchone()
    return (row[0], json.loads(row[1])) if row else (0, {})


def notes_view(db, draft, zone_revision):
    revision, records = stored_notes(db, draft['id'])
    items = []
    for entity in sorted(records):
        note = records[entity]
        reasons = []
        if note['draft_revision'] != draft['revision']:
            reasons.append('draft_changed')
        if note['zone_revision'] != zone_revision or draft['source_status'] == 'zone_changed':
            reasons.append('zone_changed')
        if draft['source_status'] == 'pattern_missing':
            reasons.append('pattern_missing')
        if draft['unavailable_targets']:
            reasons.append('targets_unavailable')
        if note['scope_fingerprint'] != scope_fingerprint(draft):
            reasons.append('scope_changed')
        # No HA I/O on listing. A saved hash cannot certify the current HA config.
        items.append(dict(note, stale=bool(reasons), stale_reasons=reasons,
                          config_status='not_rechecked'))
    return {'schema': 'pilotsuite-review-notes-v1', 'revision': revision, 'items': items,
            'limit': MAX_REVIEW_NOTES, 'execution': {'allowed': False, 'actions': []}}


class ReviewNotesMixin:
    """Methods of the canonical PlanStore, using its existing context/database.

    No independent instance, database, migration owner, learner or action gate.
    ``inspection`` is a server-derived report, never the HTTP request payload.
    """

    def _review_draft(self, db, zone_id, draft_id, inventory):
        basis = self._draft_basis(db, zone_id, inventory)
        row = db.execute('SELECT * FROM routine_drafts WHERE id=? AND zone_id=?', (draft_id, zone_id)).fetchone()
        if not row:
            raise InvalidSelection('Unknown draft in this zone')
        return self._draft_view(row, basis), basis

    @staticmethod
    def _review_guard(db, draft, inventory, payload):
        revision, records = stored_notes(db, draft['id'])
        if (payload['revision'] != draft['revision']
                or payload['zone_revision'] != inventory['revision']
                or payload['review_revision'] != revision):
            raise SelectionConflict('Draft, zone or notes changed; reload before saving')
        return revision, records

    async def review_notes(self, zone_id, draft_id, inventory, payload=None, *, deleting=False):
        if payload is not None:
            payload = validate_note_request(payload, deleting=deleting)
        return await asyncio.to_thread(self._review_notes, zone_id, draft_id, inventory, payload)

    def _review_notes(self, zone_id, draft_id, inventory, payload):
        with closing(sqlite3.connect(self._context.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            draft, _ = self._review_draft(db, zone_id, draft_id, inventory)
            if payload is not None:
                self._review_guard(db, draft, inventory, payload)
            return notes_view(db, draft, inventory['revision'])

    async def save_review_note(self, zone_id, draft_id, payload, inventory, inspection, inspected_monotonic):
        payload = validate_note_request(payload)
        return await asyncio.to_thread(self._save_review_note, zone_id, draft_id, payload,
                                       inventory, inspection, inspected_monotonic)

    def _save_review_note(self, zone_id, draft_id, payload, inventory, inspection, inspected_monotonic):
        with closing(sqlite3.connect(self._context.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            draft, _ = self._review_draft(db, zone_id, draft_id, inventory)
            revision, records = self._review_guard(db, draft, inventory, payload)
            if draft['source_status'] != 'current' or draft['unavailable_targets'] or not draft['fields']['target_ids']:
                raise SelectionConflict('Current pattern and confirmed targets must be reviewed first')
            # Check after obtaining the SQLite write lock, including queue time.
            age = time.monotonic() - inspected_monotonic
            if not 0 <= age <= MAX_INSPECTION_AGE_SECONDS:
                raise SelectionConflict('Inspection expired; inspect again before saving')
            detail = inspection.get('inspection', {})
            expected_basis = {'source_ids': sorted(draft['current_pattern']['sources']),
                              'target_ids': sorted(draft['fields']['target_ids'])}
            if (inspection.get('draft_id') != draft_id or inspection.get('zone_id') != zone_id
                    or inspection.get('draft_revision') != draft['revision']
                    or inspection.get('zone_revision') != inventory['revision']
                    or inspection.get('basis') != expected_basis
                    or detail.get('entity_id') != payload['automation_id']
                    or detail.get('config_fingerprint') != payload['config_fingerprint']
                    or not isinstance(inspection.get('checked_at'), str)):
                raise SelectionConflict('Inspection basis changed; inspect again before saving')
            entity = payload['automation_id']
            if entity not in records and len(records) >= MAX_REVIEW_NOTES:
                raise InvalidSelection('Review-note limit reached; remove an unneeded note first')
            records[entity] = {
                'automation_id': entity, 'draft_revision': draft['revision'],
                'zone_revision': inventory['revision'], 'scope_fingerprint': scope_fingerprint(draft),
                'config_fingerprint': payload['config_fingerprint'],
                'disposition': payload['disposition'], 'text': payload['text'],
                'checked_at': inspection['checked_at'], 'updated_at': datetime.now(UTC).isoformat(),
            }
            self._write_review_notes(db, draft_id, revision+1, records)
            return notes_view(db, draft, inventory['revision'])

    async def delete_review_note(self, zone_id, draft_id, payload, inventory):
        payload = validate_note_request(payload, deleting=True)
        return await asyncio.to_thread(self._delete_review_note, zone_id, draft_id, payload, inventory)

    def _delete_review_note(self, zone_id, draft_id, payload, inventory):
        with closing(sqlite3.connect(self._context.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            draft, _ = self._review_draft(db, zone_id, draft_id, inventory)
            revision, records = self._review_guard(db, draft, inventory, payload)
            if payload['automation_id'] not in records:
                raise InvalidSelection('Unknown review note')
            del records[payload['automation_id']]
            # Keep the empty row: delete/recreate must not reuse revision zero (ABA).
            self._write_review_notes(db, draft_id, revision+1, records)
            return notes_view(db, draft, inventory['revision'])

    @staticmethod
    def _write_review_notes(db, draft_id, revision, records):
        db.execute('INSERT INTO routine_review_notes VALUES (?,?,?) '
                   'ON CONFLICT(draft_id) DO UPDATE SET revision=excluded.revision, records=excluded.records',
                   (draft_id, revision, json.dumps(records, ensure_ascii=True, sort_keys=True)))
