"""Logical Habitus zones share the selection database and its revision clock."""
from __future__ import annotations

import asyncio
import json
import sqlite3
import uuid
from contextlib import closing
from .selections import InvalidSelection, SelectionConflict, SelectionStore


class ZoneStore:
    def __init__(self, selections: SelectionStore):
        self.selections = selections

    async def bootstrap(self, area_ids):
        await asyncio.to_thread(self._bootstrap, area_ids)

    def _bootstrap(self, area_ids):
        with closing(sqlite3.connect(self.selections.path)) as db, db:
            # Existing zones need no write lock; keep the durable marker as truth.
            if db.execute("SELECT 1 FROM zone_meta WHERE key='bootstrapped'").fetchone():
                return
            db.execute('BEGIN IMMEDIATE')
            # Another first reader may have initialized while we acquired the lock.
            if db.execute("SELECT 1 FROM zone_meta WHERE key='bootstrapped'").fetchone():
                return
            for area_id in area_ids:
                definition = dict(name=area_id, area_ids=[area_id], extra_entity_ids=[], enabled=True, profile='cellar')
                # Preserve existing area-keyed decisions, revision and selection mode.
                db.execute('INSERT OR IGNORE INTO habitus_zones VALUES (?, ?)', (area_id, json.dumps(definition)))
            db.execute("INSERT INTO zone_meta VALUES ('bootstrapped', '1')")

    async def list(self):
        return await asyncio.to_thread(self._list)

    def _list(self):
        with closing(sqlite3.connect(self.selections.path)) as db:
            return [dict(zone_id=row[0], revision=row[2] or 0, **json.loads(row[1])) for row in db.execute(
                'SELECT h.zone_id, h.definition, z.revision FROM habitus_zones h LEFT JOIN zones z ON h.zone_id=z.zone_id ORDER BY h.zone_id')]

    @staticmethod
    def validate(definition):
        if not isinstance(definition, dict) or set(definition) != {'name', 'area_ids', 'extra_entity_ids', 'enabled', 'profile'}:
            raise InvalidSelection('definition requires name, area_ids, extra_entity_ids, enabled, profile')
        name = definition['name']
        if not isinstance(name, str) or not name.strip() or len(name) > 80:
            raise InvalidSelection('name must contain 1 to 80 characters')
        if type(definition['enabled']) is not bool or definition['profile'] not in ('observe', 'cellar'):
            raise InvalidSelection('invalid enabled flag or profile')
        for key, maximum in [('area_ids', 100), ('extra_entity_ids', 500)]:
            values = definition[key]
            if not isinstance(values, list) or len(values) > maximum or any(not isinstance(v, str) or not v or len(v) > 255 for v in values):
                raise InvalidSelection(f'invalid {key}')
        return {**definition, 'name': name.strip(), 'area_ids': sorted(set(definition['area_ids'])),
                'extra_entity_ids': sorted(set(definition['extra_entity_ids']))}

    async def save(self, definition, zone_id=None, revision=None, *, setup=None, relevant=None):
        definition = self.validate(definition)
        if zone_id is not None and (type(revision) is not int or revision < 0):
            raise InvalidSelection('revision must be a nonnegative integer')
        from .organization_store import durable
        return await durable(self._save, definition, zone_id, revision, setup, relevant)

    def _save(self, definition, zone_id, revision, setup=None, relevant=None):
        from .context import ContextStore
        from .zone_structure import KEY
        with closing(sqlite3.connect(self.selections.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            previous = None
            if zone_id is None:
                if db.execute('SELECT count(*) FROM habitus_zones').fetchone()[0] >= 100:
                    raise InvalidSelection('at most 100 zones are supported')
                zone_id = 'hz_' + uuid.uuid4().hex
                revision = 0
                # New zones always require explicit selection; no automatic newcomers.
                db.execute('INSERT INTO selection_modes VALUES (?, 1)', (zone_id,))
            else:
                row = db.execute('SELECT definition FROM habitus_zones WHERE zone_id=?', (zone_id,)).fetchone()
                if not row:
                    raise InvalidSelection('unknown Habitus zone')
                previous = json.loads(row[0])
                if self.selections._read(db, zone_id)['revision'] != revision:
                    raise SelectionConflict('Zone or selection changed; reload before saving')
                if previous == definition and setup is None:
                    return dict(zone_id=zone_id, revision=revision, **definition)
            journal = {'$definition': {'before': previous, 'after': definition}}
            if setup is not None:
                # Same SQLite transaction as the definition and relevance decisions.
                # No helper, runtime mode, legacy learning field or HA registry write.
                cfg = ContextStore.read(db, zone_id)
                for other_id, raw in db.execute('SELECT zone_id,config FROM zone_context'):
                    other = json.loads(raw).get(KEY, {})
                    same_label = (other.get('label_id') == setup['label_id'] if setup['label_id'] else
                                  bool(other.get('label_name')) and other['label_name'].casefold() == setup['label_name'].casefold())
                    if other_id != zone_id and same_label:
                        raise SelectionConflict('Dieses Zonenlabel ist bereits mit einer anderen Zone verbunden')
                before = cfg.get(KEY)
                if before and before['label_id'] is not None and before['label_id'] != setup['label_id']:
                    raise SelectionConflict('Die Zone ist bereits mit einem anderen Label verbunden; Umstellung gesondert prüfen')
                for eid, member in setup['members'].items():
                    old_member = (before or {}).get('members', {}).get(eid)
                    if old_member and old_member['identity'] != member['identity']:
                        raise SelectionConflict('Mitglied wurde ersetzt; Identität vor erneuter Zuordnung klären: ' + eid)
                decisions = self.selections._read(db, zone_id)['decisions']
                changes = {eid: 'relevant' if eid in (relevant or []) else 'ignored'
                           for eid in setup['members']}
                changes.update({eid: 'ignored' for eid in (before or {}).get('members', {}) if eid not in setup['members']})
                delta = {eid: value for eid, value in changes.items() if decisions.get(eid, 'unreviewed') != value}
                if previous == definition and before == setup and not delta:
                    return dict(zone_id=zone_id, revision=revision, **definition)
                cfg[KEY] = setup
                db.execute('INSERT OR REPLACE INTO zone_context VALUES (?,?)', (zone_id, json.dumps(cfg)))
                for eid, value in delta.items():
                    db.execute('INSERT OR REPLACE INTO selections VALUES (?,?,?)', (zone_id, eid, value))
                journal['$structure'] = {'before': before, 'after': setup}
                journal['$relevance'] = delta
            db.execute('INSERT INTO habitus_zones VALUES (?, ?) ON CONFLICT(zone_id) DO UPDATE SET definition=excluded.definition', (zone_id, json.dumps(definition)))
            db.execute('INSERT INTO zones VALUES (?, ?) ON CONFLICT(zone_id) DO UPDATE SET revision=excluded.revision', (zone_id, revision + 1))
            db.execute('INSERT INTO selection_journal(zone_id, revision, changes) VALUES (?, ?, ?)',
                       (zone_id, revision + 1, json.dumps(journal)))
            self.selections.prune_journal(db)
            return dict(zone_id=zone_id, revision=revision + 1, **definition)

    async def bind_created_label(self, zone_id, revision, plan_id):
        from .organization_store import durable
        return await durable(self._bind_created_label, zone_id, revision, plan_id)

    def _bind_created_label(self, zone_id, revision, plan_id):
        from .context import ContextStore
        from .organization_store import PREFIX
        from .zone_structure import KEY
        with closing(sqlite3.connect(self.selections.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT value FROM zone_meta WHERE key=?', (PREFIX + plan_id,)).fetchone()
            plan = json.loads(row[0]) if row else {}
            if plan.get('zone_id') != zone_id or plan.get('kind') != 'structure_labels' or plan.get('state') != 'verified':
                raise SelectionConflict('Labelanlage noch nicht vollständig bestätigt')
            if plan.get('binding'):
                return plan
            if self.selections._read(db, zone_id)['revision'] != revision:
                raise SelectionConflict('Zone vor der Labelbindung geändert')
            op = plan['operations'][0]
            created = op.get('receipt', {}).get('label')
            cfg = ContextStore.read(db, zone_id)
            profile = cfg.get(KEY) or {}
            if (op.get('effect') != 'create_zone_label' or not created or profile.get('label_id') is not None or
                    created['name'] != profile.get('label_name')):
                raise SelectionConflict('Labelanlage passt nicht mehr zur geplanten Zone')
            for other_id, raw in db.execute('SELECT zone_id,config FROM zone_context'):
                if other_id != zone_id and json.loads(raw).get(KEY, {}).get('label_id') == created['label_id']:
                    raise SelectionConflict('Label inzwischen mit anderer Zone verbunden')
            profile['label_id'] = created['label_id']
            profile.pop('label_name', None)
            db.execute('INSERT OR REPLACE INTO zone_context VALUES (?,?)', (zone_id, json.dumps(cfg)))
            db.execute('INSERT OR REPLACE INTO zones VALUES (?,?)', (zone_id, revision + 1))
            db.execute('INSERT INTO selection_journal(zone_id,revision,changes) VALUES (?,?,?)',
                       (zone_id, revision + 1, json.dumps({'$zone_label_created': {'plan_id':plan_id, 'label_id':created['label_id']}})))
            self.selections.prune_journal(db)
            plan['binding'] = {'label_id':created['label_id'], 'revision':revision + 1}
            db.execute('UPDATE zone_meta SET value=? WHERE key=?', (json.dumps(plan), PREFIX + plan_id))
            return plan
