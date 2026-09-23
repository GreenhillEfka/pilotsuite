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
from .learning_views import temporal_settings, time_bucket, coverage_report, context_report
from .attribution import ALLOWED_ORIGINS
from .selections import InvalidSelection, SelectionConflict

ROLE_KINDS = {'temperature': {'temperature'}, 'humidity': {'humidity'},
              'illuminance': {'illuminance'}, 'light': {'light'},
              'presence': {'motion', 'occupancy', 'presence'}, 'reference_temperature': {'temperature'}}
RETENTION = 14 * 86400
MAX_EVIDENCE = 5000
ACTIVITY_RULE_ID = 'activity-v1'
MIN_EVENTS = 5
MIN_DAYS = 3

DEFAULT_DETECTOR = {'min_events': MIN_EVENTS, 'min_days': MIN_DAYS}


def validate_detector(value):
    if (not isinstance(value, dict) or not set(DEFAULT_DETECTOR) <= set(value)
            or set(value) - (set(DEFAULT_DETECTOR) | {'timezone', 'day_mode'})):
        raise InvalidSelection('Detector requires min_events and min_days; unknown fields rejected')
    temporal_settings(value)
    if type(value['min_events']) is not int or not 5 <= value['min_events'] <= 100:
        raise InvalidSelection('min_events must be an integer between 5 and 100')
    if type(value['min_days']) is not int or not 3 <= value['min_days'] <= 14:
        raise InvalidSelection('min_days must be an integer between 3 and 14')
    result = dict(value)
    if result.get('timezone') == 'UTC': result.pop('timezone')
    if result.get('day_mode') == 'all': result.pop('day_mode')
    return result


class ContextStore:
    def __init__(self, selections):
        self.selections = selections
        self.path = selections.path

    @staticmethod
    def read(db, zone_id):
        row = db.execute('SELECT config FROM zone_context WHERE zone_id=?', (zone_id,)).fetchone()
        value = json.loads(row[0]) if row else {'roles': {}, 'learning': False, 'consented_at': None}
        value.setdefault('detector', dict(DEFAULT_DETECTOR))
        value.setdefault('context_learning', False)
        value.setdefault('context_consented_at', None)
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

    async def configure(self, zone_id, revision, roles, learning, *, reset=False, now=None, detector=None, context_learning=None):
        if type(revision) is not int or revision < 0 or type(learning) is not bool or type(reset) is not bool:
            raise InvalidSelection('invalid context flags or revision')
        if not isinstance(roles, dict) or not set(roles) <= set(ROLE_KINDS) or any(not isinstance(v, list) or len(v)>20 or any(not isinstance(e, str) or not e or len(e)>255 for e in v) for v in roles.values()):
            raise InvalidSelection('invalid role mapping')
        if context_learning is not None and type(context_learning) is not bool:
            raise InvalidSelection('context_learning must be boolean')
        if context_learning and not learning:
            raise InvalidSelection('Context learning requires activity learning consent')
        if detector is not None: validate_detector(detector)
        roles = {k: sorted(set(v)) for k,v in roles.items()}
        if set(roles.get('temperature', [])) & set(roles.get('reference_temperature', [])):
            raise InvalidSelection('Main and reference temperature must be different sensors')
        if learning and not roles.get('presence'):
            raise InvalidSelection('Select a relevant presence or motion source before consenting')
        return await asyncio.to_thread(self._configure, zone_id, revision, roles, learning, reset, time.time() if now is None else now, detector, context_learning)

    def _configure(self, zone_id, revision, roles, learning, reset, now, detector, context_learning):
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
            context_enabled = (old['context_learning'] if context_learning is None else context_learning) and learning and not reset
            context_changed = any(old['roles'].get(k) != roles.get(k) for k in ('light', 'illuminance'))
            if reset or source_changed:
                db.execute('DELETE FROM coverage_checks WHERE zone_id=?', (zone_id,))
            if reset or source_changed or context_changed:
                db.execute('DELETE FROM activity_context WHERE zone_id=?', (zone_id,))
            value = {'context_learning': context_enabled,
                     'context_consented_at': (now if context_enabled and (not old['context_learning'] or source_changed or context_changed) else old['context_consented_at']) if not reset else None,
                     'roles': roles, 'detector': validate_detector({**old['detector'], **detector}) if detector is not None else old['detector'], 'learning': learning and not reset,
                     'consented_at': now if learning and (source_changed or not old['learning']) and not reset else old['consented_at']}
            if reset: value['consented_at'] = None
            db.execute('INSERT INTO zone_context VALUES (?,?) ON CONFLICT(zone_id) DO UPDATE SET config=excluded.config', (zone_id, json.dumps(value)))
            db.execute('INSERT INTO zones VALUES (?,?) ON CONFLICT(zone_id) DO UPDATE SET revision=excluded.revision', (zone_id, revision+1))
            # Do not retain deleted learning evidence or individual identities in the journal.
            db.execute('INSERT INTO selection_journal(zone_id, revision, changes) VALUES (?,?,?)', (zone_id, revision+1, json.dumps({'$context': {'roles': roles, 'learning': value['learning'], 'reset': reset, 'detector': value['detector'], 'context_learning': value['context_learning']}})))
            self.selections.prune_journal(db)
            return value

    @staticmethod
    def prune(db, now):
        db.execute('DELETE FROM activity_evidence WHERE occurred < ?', (now-RETENTION,))
        db.execute('DELETE FROM activity_evidence WHERE rowid NOT IN (SELECT rowid FROM activity_evidence ORDER BY occurred DESC LIMIT ?)', (MAX_EVIDENCE,))
        db.execute('DELETE FROM activity_context WHERE occurred < ? OR NOT EXISTS (SELECT 1 FROM activity_evidence e WHERE e.zone_id=activity_context.zone_id AND e.occurred=activity_context.occurred)', (now-RETENTION,))
        db.execute('DELETE FROM coverage_checks WHERE slot < ?', (now-RETENTION,))
        db.execute('DELETE FROM coverage_checks WHERE rowid NOT IN (SELECT rowid FROM coverage_checks ORDER BY slot DESC LIMIT 50000)')
        db.execute('DELETE FROM pattern_feedback WHERE rowid NOT IN (SELECT rowid FROM pattern_feedback ORDER BY updated DESC LIMIT 2000)')

    async def record(self, zone_id, entity_id, occurred, origin, *, now=None, context=None):
        return await asyncio.to_thread(self._record, zone_id, entity_id, occurred, origin, time.time() if now is None else now, context)

    def _record(self, zone_id, entity_id, occurred, origin, now, context):
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
            origin = origin if origin in ALLOWED_ORIGINS else 'unknown'
            db.execute('INSERT OR IGNORE INTO activity_evidence VALUES (?,?,?,?)', (zone_id, entity_id, occurred, origin))
            if cfg['context_learning'] and context is not None and occurred >= (cfg['context_consented_at'] or now):
                db.execute('INSERT OR REPLACE INTO activity_context VALUES (?,?,?)', (zone_id, occurred, json.dumps(context)))
            self.prune(db, now)
            return True

    async def checkpoint(self, zone_id, state, *, now=None):
        if state not in ('ready', 'disconnected', 'no_source', 'partial_source', 'paused'):
            raise InvalidSelection('invalid collection checkpoint')
        await asyncio.to_thread(self._checkpoint, zone_id, state, time.time() if now is None else now)

    def _checkpoint(self, zone_id, state, now):
        with closing(sqlite3.connect(self.path)) as db, db:
            if not self.read(db, zone_id)['learning']: return
            db.execute('INSERT OR IGNORE INTO coverage_checks VALUES (?,?,?)', (zone_id, int(now//300)*300, state))
            self.prune(db, now)

    async def report(self, zone_id, *, now=None):
        return await asyncio.to_thread(self._report, zone_id, time.time() if now is None else now)

    def _report(self, zone_id, now):
        with closing(sqlite3.connect(self.path)) as db, db:
            self.prune(db, now)
            cfg = self.read(db, zone_id)
            rows = db.execute('SELECT entity_id, occurred, origin FROM activity_evidence WHERE zone_id=? ORDER BY occurred', (zone_id,)).fetchall()
            feedback = dict(db.execute('SELECT pattern_id,decision FROM pattern_feedback WHERE zone_id=?', (zone_id,)))
            detector = cfg['detector']
            local_zone, day_mode = temporal_settings(detector)
            buckets = defaultdict(list)
            for entity, occurred, origin in rows:
                if entity in cfg['roles'].get('presence', []):
                    key, _ = time_bucket(occurred, detector)
                    buckets[key].append((occurred, origin))
            min_events, min_days = detector['min_events'], detector['min_days']
            patterns, windows = [], []
            for (day_group, bucket), events in sorted(buckets.items()):
                days = sorted({time_bucket(t, detector)[1] for t,_ in events})
                windows.append({'day_group': day_group, 'timezone': local_zone.key, 'start_hour': bucket*2, 'end_hour': bucket*2+2,
                                'events': len(events), 'days': len(days),
                                'missing_events': max(0, min_events-len(events)),
                                'missing_days': max(0, min_days-len(days))})
                if len(events) < min_events or len(days) < min_days: continue
                identity = f'activity-v1:{zone_id}:{cfg["roles"].get("presence")}:{bucket}'
                if day_group != 'all': identity += ':' + day_group
                if detector != DEFAULT_DETECTOR:
                    identity += ':' + json.dumps(detector, sort_keys=True)
                pid = hashlib.sha256(identity.encode()).hexdigest()[:24]
                origins = dict(Counter(origin for _,origin in events))
                patterns.append({'id': pid, 'title': f'Wiederkehrende Aktivierungen {bucket*2:02d}–{bucket*2+2:02d} Uhr {local_zone.key} ({day_group})',
                                 'algorithm': ACTIVITY_RULE_ID, 'parameters': dict(detector),
                                 'sources': cfg['roles'].get('presence', []),
                                 'statistics': {'activation_count': len(events), 'distinct_day_count': len(days),
                                                'days_local': days, 'timezone': local_zone.key, 'day_group': day_group,
                                                'days_utc': sorted({datetime.fromtimestamp(t, UTC).date().isoformat() for t,_ in events}), 'observed_zone_activations': len(rows),
                                                'origins': origins, 'window_local': {'start_hour': bucket*2, 'end_hour': bucket*2+2},
                                                'window_utc': {'start_hour': bucket*2, 'end_hour': bucket*2+2} if local_zone.key == 'UTC' else None},
                                 'confidence': None, 'confidence_basis': 'not_estimated',
                                 'rule_strength': {'rule_id': ACTIVITY_RULE_ID, 'threshold_met': True,
                                                   'event_ratio': round(len(events)/min_events, 3),
                                                   'day_ratio': round(len(days)/min_days, 3),
                                                   'minimum_events': min_events, 'minimum_days': min_days},
                                 'risk': 'read_only', 'preference': feedback.get(pid),
                                 # Deprecated alpha aliases; remove only with an
                                 # announced API-version transition.
                                 'events': len(events), 'days': days, 'observed_total': len(rows),
                                 'origins': origins, 'feedback': feedback.get(pid),
                                 'proposal': 'Prüfen, ob dieses Zeitfenster eine relevante Routine beschreibt. Keine Automation wird erstellt.'})
            return {'config': cfg, 'event_count': len(rows), 'retention_days': 14, 'limit': MAX_EVIDENCE,
                    'progress': {'required_events': min_events, 'required_days': min_days,
                                 'window_hours': 2, 'windows': windows,
                                 'first_evidence_at': datetime.fromtimestamp(rows[0][1], UTC).isoformat() if rows else None,
                                 'last_evidence_at': datetime.fromtimestamp(rows[-1][1], UTC).isoformat() if rows else None,
                                 'observed_days': len({time_bucket(row[1], detector)[1] for row in rows}),
                                 'observed_days_utc': len({datetime.fromtimestamp(row[1], UTC).date() for row in rows})},
                    'coverage': coverage_report(db.execute('SELECT slot, state FROM coverage_checks WHERE zone_id=? ORDER BY slot', (zone_id,)).fetchall()),
                    'coverage_samples': [{'slot': slot, 'state': state} for slot,state in db.execute('SELECT slot,state FROM coverage_checks WHERE zone_id=? ORDER BY slot', (zone_id,))],
                    'context_windows': context_report([(t, json.loads(p)) for t,p in db.execute('SELECT occurred,payload FROM activity_context WHERE zone_id=? ORDER BY occurred', (zone_id,))], detector),
                    'context_evidence': [{'occurred': datetime.fromtimestamp(t, UTC).isoformat(), 'context': json.loads(p)} for t,p in db.execute('SELECT occurred,payload FROM activity_context WHERE zone_id=? ORDER BY occurred', (zone_id,))],
                    'time_basis': local_zone.key, 'day_mode': day_mode, 'patterns': patterns, 'evidence': [{'source': e, 'occurred': datetime.fromtimestamp(t, UTC).isoformat(), 'origin': o} for e,t,o in rows],
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
