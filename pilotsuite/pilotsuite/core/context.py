"""Roles, opt-in bounded activity evidence and independent feedback in one DB."""
from __future__ import annotations
import asyncio
import hashlib
import json
import sqlite3
import time
from collections import Counter, defaultdict
from contextlib import closing
from datetime import datetime, UTC
from .selections import InvalidSelection, SelectionConflict

ROLE_KINDS = {'temperature': {'temperature'}, 'humidity': {'humidity'},
              'illuminance': {'illuminance'}, 'light': {'light'},
              'presence': {'motion', 'occupancy', 'presence'}, 'reference_temperature': {'temperature'}}
RETENTION = 14 * 86400
MAX_EVIDENCE = 5000
MIN_EVENTS = 5
MIN_DAYS = 3

DEFAULT_DETECTOR = {'min_events': MIN_EVENTS, 'min_days': MIN_DAYS}


def validate_detector(value):
    if not isinstance(value, dict) or set(value) != set(DEFAULT_DETECTOR):
        raise InvalidSelection('Detector requires min_events and min_days')
    if type(value['min_events']) is not int or not 5 <= value['min_events'] <= 100:
        raise InvalidSelection('min_events must be an integer between 5 and 100')
    if type(value['min_days']) is not int or not 3 <= value['min_days'] <= 14:
        raise InvalidSelection('min_days must be an integer between 3 and 14')
    return dict(value)


class ContextStore:
    def __init__(self, selections):
        self.selections = selections
        self.path = selections.path

    @staticmethod
    def read(db, zone_id):
        row = db.execute('SELECT config FROM zone_context WHERE zone_id=?', (zone_id,)).fetchone()
        value = json.loads(row[0]) if row else {'roles': {}, 'learning': False, 'consented_at': None}
        value.setdefault('detector', dict(DEFAULT_DETECTOR))
        return value

    async def maintain(self):
        await asyncio.to_thread(self._maintain)

    def _maintain(self):
        with closing(sqlite3.connect(self.path)) as db, db:
            self.prune(db, time.time())

    async def get(self, zone_id):
        return await asyncio.to_thread(self._get, zone_id)

    def _get(self, zone_id):
        with closing(sqlite3.connect(self.path)) as db:
            return self.read(db, zone_id)

    async def configure(self, zone_id, revision, roles, learning, *, reset=False, now=None, detector=None):
        if type(revision) is not int or revision < 0 or type(learning) is not bool or type(reset) is not bool:
            raise InvalidSelection('invalid context flags or revision')
        if not isinstance(roles, dict) or not set(roles) <= set(ROLE_KINDS) or any(not isinstance(v, list) or len(v)>20 or any(not isinstance(e, str) or not e or len(e)>255 for e in v) for v in roles.values()):
            raise InvalidSelection('invalid role mapping')
        if detector is not None: detector = validate_detector(detector)
        roles = {k: sorted(set(v)) for k,v in roles.items()}
        if set(roles.get('temperature', [])) & set(roles.get('reference_temperature', [])):
            raise InvalidSelection('Main and reference temperature must be different sensors')
        if learning and not roles.get('presence'):
            raise InvalidSelection('Select a relevant presence or motion source before consenting')
        return await asyncio.to_thread(self._configure, zone_id, revision, roles, learning, reset, time.time() if now is None else now, detector)

    def _configure(self, zone_id, revision, roles, learning, reset, now, detector):
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM habitus_zones WHERE zone_id=?', (zone_id,)).fetchone():
                raise InvalidSelection('unknown zone')
            if self.selections._read(db, zone_id)['revision'] != revision:
                raise SelectionConflict('Zone changed; reload before saving roles or consent')
            old = self.read(db, zone_id)
            source_changed = old['roles'].get('presence') != roles.get('presence')
            if reset or source_changed:
                db.execute('DELETE FROM activity_evidence WHERE zone_id=?', (zone_id,))
                db.execute('DELETE FROM pattern_feedback WHERE zone_id=?', (zone_id,))
            value = {'roles': roles, 'detector': detector if detector is not None else old['detector'], 'learning': learning and not reset,
                     'consented_at': now if learning and (source_changed or not old['learning']) and not reset else old['consented_at']}
            if reset: value['consented_at'] = None
            db.execute('INSERT INTO zone_context VALUES (?,?) ON CONFLICT(zone_id) DO UPDATE SET config=excluded.config', (zone_id, json.dumps(value)))
            db.execute('INSERT INTO zones VALUES (?,?) ON CONFLICT(zone_id) DO UPDATE SET revision=excluded.revision', (zone_id, revision+1))
            # Do not retain deleted learning evidence or individual identities in the journal.
            db.execute('INSERT INTO selection_journal(zone_id, revision, changes) VALUES (?,?,?)', (zone_id, revision+1, json.dumps({'$context': {'roles': roles, 'learning': value['learning'], 'reset': reset, 'detector': value['detector']}})))
            self.selections.prune_journal(db)
            return value

    @staticmethod
    def prune(db, now):
        db.execute('DELETE FROM activity_evidence WHERE occurred < ?', (now-RETENTION,))
        db.execute('DELETE FROM activity_evidence WHERE rowid NOT IN (SELECT rowid FROM activity_evidence ORDER BY occurred DESC LIMIT ?)', (MAX_EVIDENCE,))
        db.execute('DELETE FROM pattern_feedback WHERE rowid NOT IN (SELECT rowid FROM pattern_feedback ORDER BY updated DESC LIMIT 2000)')

    async def record(self, zone_id, entity_id, occurred, origin, *, now=None):
        return await asyncio.to_thread(self._record, zone_id, entity_id, occurred, origin, time.time() if now is None else now)

    def _record(self, zone_id, entity_id, occurred, origin, now):
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE'); self.prune(db, now)
            cfg = self.read(db, zone_id)
            if not cfg['learning'] or entity_id not in cfg['roles'].get('presence', []) or occurred < (cfg['consented_at'] or now) or not now-120 <= occurred <= now+5:
                return False
            definition = db.execute('SELECT definition FROM habitus_zones WHERE zone_id=?', (zone_id,)).fetchone()
            if not definition or not json.loads(definition[0])['enabled'] or self.selections._read(db, zone_id)['decisions'].get(entity_id) != 'relevant':
                return False
            last = db.execute('SELECT MAX(occurred) FROM activity_evidence WHERE zone_id=?', (zone_id,)).fetchone()[0]
            if last is not None and occurred-last < 300: return False
            origin = origin if origin in ('user_context', 'derived_context') else 'unknown'
            db.execute('INSERT OR IGNORE INTO activity_evidence VALUES (?,?,?,?)', (zone_id, entity_id, occurred, origin))
            self.prune(db, now)
            return True

    async def report(self, zone_id, *, now=None):
        return await asyncio.to_thread(self._report, zone_id, time.time() if now is None else now)

    def _report(self, zone_id, now):
        with closing(sqlite3.connect(self.path)) as db, db:
            self.prune(db, now)
            cfg = self.read(db, zone_id)
            rows = db.execute('SELECT entity_id, occurred, origin FROM activity_evidence WHERE zone_id=? ORDER BY occurred', (zone_id,)).fetchall()
            feedback = dict(db.execute('SELECT pattern_id,decision FROM pattern_feedback WHERE zone_id=?', (zone_id,)))
            buckets = defaultdict(list)
            for entity, occurred, origin in rows:
                if entity in cfg['roles'].get('presence', []):
                    buckets[datetime.fromtimestamp(occurred, UTC).hour//2].append((occurred, origin))
            detector = cfg['detector']
            min_events, min_days = detector['min_events'], detector['min_days']
            patterns, windows = [], []
            for bucket, events in sorted(buckets.items()):
                days = sorted({datetime.fromtimestamp(t, UTC).date().isoformat() for t,_ in events})
                windows.append({'start_hour': bucket*2, 'end_hour': bucket*2+2,
                                'events': len(events), 'days': len(days),
                                'missing_events': max(0, min_events-len(events)),
                                'missing_days': max(0, min_days-len(days))})
                if len(events) < min_events or len(days) < min_days: continue
                identity = f'activity-v1:{zone_id}:{cfg["roles"].get("presence")}:{bucket}'
                if detector != DEFAULT_DETECTOR:
                    identity += ':' + json.dumps(detector, sort_keys=True)
                pid = hashlib.sha256(identity.encode()).hexdigest()[:24]
                patterns.append({'id': pid, 'title': f'Wiederkehrende Aktivierungen {bucket*2:02d}–{bucket*2+2:02d} Uhr UTC',
                                 'algorithm': 'activity-v1', 'parameters': dict(detector),
                                 'sources': cfg['roles'].get('presence', []), 'events': len(events), 'days': days,
                                 'observed_total': len(rows), 'confidence': None, 'feedback': feedback.get(pid),
                                 'origins': dict(Counter(origin for _,origin in events)),
                                 'proposal': 'Prüfen, ob dieses Zeitfenster eine relevante Routine beschreibt. Keine Automation wird erstellt.'})
            return {'config': cfg, 'event_count': len(rows), 'retention_days': 14, 'limit': MAX_EVIDENCE,
                    'progress': {'required_events': min_events, 'required_days': min_days,
                                 'window_hours': 2, 'windows': windows,
                                 'first_evidence_at': datetime.fromtimestamp(rows[0][1], UTC).isoformat() if rows else None,
                                 'last_evidence_at': datetime.fromtimestamp(rows[-1][1], UTC).isoformat() if rows else None,
                                 'observed_days': len({datetime.fromtimestamp(row[1], UTC).date() for row in rows})},
                    'time_basis': 'UTC', 'patterns': patterns, 'evidence': [{'source': e, 'occurred': datetime.fromtimestamp(t, UTC).isoformat(), 'origin': o} for e,t,o in rows],
                    'limitations': 'Nur beobachtete Aktivierungen, keine Anwesenheitsdauer oder Wahrscheinlichkeit. Ausfälle und inaktive Lernzeiten sind unbeobachtet; Herkunft ist kein Beweis menschlicher Bedienung.'}

    async def feedback(self, zone_id, pattern_id, decision):
        if decision not in ('accepted', 'rejected', 'later'):
            raise InvalidSelection('invalid feedback')
        report = await self.report(zone_id)
        if pattern_id not in {p['id'] for p in report['patterns']}:
            raise InvalidSelection('Pattern expired or unknown; reload')
        await asyncio.to_thread(self._feedback, zone_id, pattern_id, decision)

    def _feedback(self, zone_id, pattern_id, decision):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('INSERT INTO pattern_feedback VALUES (?,?,?,?) ON CONFLICT(zone_id,pattern_id) DO UPDATE SET decision=excluded.decision, updated=excluded.updated', (zone_id, pattern_id, decision, time.time()))
            self.prune(db, time.time())
