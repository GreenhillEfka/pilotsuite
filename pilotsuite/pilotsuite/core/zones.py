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
            db.execute('BEGIN IMMEDIATE')
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

    async def save(self, definition, zone_id=None, revision=None):
        definition = self.validate(definition)
        if zone_id is not None and (type(revision) is not int or revision < 0):
            raise InvalidSelection('revision must be a nonnegative integer')
        return await asyncio.to_thread(self._save, definition, zone_id, revision)

    def _save(self, definition, zone_id, revision):
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
                if previous == definition:
                    return dict(zone_id=zone_id, revision=revision, **definition)
            db.execute('INSERT INTO habitus_zones VALUES (?, ?) ON CONFLICT(zone_id) DO UPDATE SET definition=excluded.definition', (zone_id, json.dumps(definition)))
            db.execute('INSERT INTO zones VALUES (?, ?) ON CONFLICT(zone_id) DO UPDATE SET revision=excluded.revision', (zone_id, revision + 1))
            db.execute('INSERT INTO selection_journal(zone_id, revision, changes) VALUES (?, ?, ?)',
                       (zone_id, revision + 1, json.dumps({'$definition': {'before': previous, 'after': definition}})))
            self.selections.prune_journal(db)
            return dict(zone_id=zone_id, revision=revision + 1, **definition)
