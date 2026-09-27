"""Latest-only shadow settings/checkpoints in the existing ContextStore database."""
from __future__ import annotations
from contextlib import closing
from copy import deepcopy
import json
import sqlite3
from .organization_store import durable
from .presence_kernel import checkpoint_dict, validate_checkpoint
from .lighting_policy import validate_lighting_checkpoint
from .selections import InvalidSelection, SelectionConflict


class ShadowContextMixin:
    async def configure_shadow(self, zone_id, revision, record):
        return await durable(self._configure_shadow, zone_id, revision, deepcopy(record))

    def _shadow_revision(self, db, zone_id, revision):
        if type(revision) is not int or revision < 0 or not db.execute(
                'SELECT 1 FROM habitus_zones WHERE zone_id=?', (zone_id,)).fetchone():
            raise InvalidSelection('Ungültige Zone oder Revision')
        if self.selections._read(db, zone_id)['revision'] != revision:
            raise SelectionConflict('Zone geändert; Schattenkonfiguration neu laden')

    def _configure_shadow(self, zone_id, revision, record):
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            self._shadow_revision(db, zone_id, revision)
            cfg = self.read(db, zone_id)
            if record is not None:
                record['revision'] = revision+1
                cfg['presence_shadow'] = record
                cfg['presence_lifecycle'] = checkpoint_dict(validate_checkpoint(None))
                cfg['shadow_lighting'] = {}
            else:
                cfg.pop('presence_shadow', None)
                cfg.pop('presence_lifecycle', None)
                cfg.pop('shadow_lighting', None)
            # Does NOT call ContextStore.configure: learning settings/evidence survive.
            db.execute('INSERT OR REPLACE INTO zone_context VALUES (?,?)',
                       (zone_id, json.dumps(cfg, allow_nan=False)))
            db.execute('INSERT OR REPLACE INTO zones VALUES (?,?)', (zone_id, revision+1))
            db.execute('INSERT INTO selection_journal(zone_id,revision,changes) VALUES (?,?,?)',
                       (zone_id, revision+1, json.dumps({'$shadow': {'enabled':record is not None}})))
            self.selections.prune_journal(db)
            return revision+1

    async def update_shadow_checkpoint(self, zone_id, revision, session, checkpoint, lighting):
        return await durable(self._update_shadow_checkpoint, zone_id, revision, session, checkpoint, lighting)

    def _update_shadow_checkpoint(self, zone_id, revision, session, checkpoint, lighting):
        current = checkpoint_dict(validate_checkpoint(checkpoint))
        if not isinstance(lighting, dict) or len(lighting) > 20:
            raise InvalidSelection('Zu viele Lichtzwischenstände')
        for point in lighting.values():
            validate_lighting_checkpoint(point)
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            self._shadow_revision(db, zone_id, revision)
            cfg = self.read(db, zone_id)
            if cfg.get('presence_shadow', {}).get('session') != session:
                raise SelectionConflict('Schattenvergleich beendet oder neu gestartet')
            if cfg.get('presence_lifecycle') == current and cfg.get('shadow_lighting') == lighting:
                return
            cfg['presence_lifecycle'] = current
            cfg['shadow_lighting'] = deepcopy(lighting)
            db.execute('UPDATE zone_context SET config=? WHERE zone_id=?',
                       (json.dumps(cfg, allow_nan=False), zone_id))

    async def suspend_shadow(self, zone_id, session, reason):
        if reason not in ('basis_changed','zone_paused','invalid_checkpoint'):
            raise InvalidSelection('Ungültiger Unterbrechungsgrund')
        await durable(self._suspend_shadow, zone_id, session, reason)

    def _suspend_shadow(self, zone_id, session, reason):
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            cfg = self.read(db, zone_id)
            record = cfg.get('presence_shadow')
            if not isinstance(record, dict) or record.get('session') != session or record.get('suspended_reason'):
                return
            record['suspended_reason'] = reason
            db.execute('UPDATE zone_context SET config=? WHERE zone_id=?',
                       (json.dumps(cfg, allow_nan=False), zone_id))
