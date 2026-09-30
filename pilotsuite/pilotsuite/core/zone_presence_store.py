"""Zone config and bounded operational state in the existing ContextStore SQLite DB."""
from contextlib import closing
from copy import deepcopy
import json
import sqlite3
import time
from .organization_store import durable
from .selections import SelectionConflict, InvalidSelection

KEY='zone_presence_v2'

class ZonePresenceContextMixin:
    async def save_zone_lighting(self,zid,revision,config,*,recover=False):
        return await durable(self._save_zone_lighting,zid,revision,deepcopy(config),recover)

    def _save_zone_lighting(self,zid,revision,config,recover=False):
        from .zone_lighting import KEY as LIGHTING
        with closing(sqlite3.connect(self.path,timeout=10)) as db,db:
            db.execute('BEGIN IMMEDIATE');self._shadow_revision(db,zid,revision)
            previous=self.read(db,zid)
            if previous.get(LIGHTING)==config and not recover:return revision
            previous[LIGHTING]=config
            db.execute('INSERT OR REPLACE INTO zone_context VALUES (?,?)',(zid,json.dumps(previous,allow_nan=False)))
            db.execute('INSERT OR REPLACE INTO zones VALUES (?,?)',(zid,revision+1))
            row=db.execute('SELECT value FROM zone_meta WHERE key=?',('zone_presence_state:'+zid,)).fetchone()
            if row:
                state=json.loads(row[0]);state.pop('lighting',None)
                db.execute('UPDATE zone_meta SET value=? WHERE key=?',(json.dumps(state,allow_nan=False),'zone_presence_state:'+zid))
            db.execute('INSERT INTO selection_journal(zone_id,revision,changes) VALUES (?,?,?)',
                (zid,revision+1,json.dumps({'$zone_lighting':{'mode':config['mode']}})))
            self.selections.prune_journal(db)
            return revision+1

    async def save_zone_presence(self,zid,revision,config, *, structure_members=None):
        return await durable(self._save_zone_presence,zid,revision,deepcopy(config),deepcopy(structure_members))

    def _save_zone_presence(self,zid,revision,config,structure_members=None):
        with closing(sqlite3.connect(self.path,timeout=10)) as db,db:
            db.execute('BEGIN IMMEDIATE');self._shadow_revision(db,zid,revision)
            previous=self.read(db,zid);before=deepcopy(previous.get(KEY))
            previous[KEY]=config
            if structure_members:
                from .zone_structure import KEY as STRUCTURE
                if STRUCTURE not in previous:
                    raise SelectionConflict('Zonenstruktur vor der Helferbindung verloren')
                definition = json.loads(db.execute('SELECT definition FROM habitus_zones WHERE zone_id=?', (zid,)).fetchone()[0])
                ids = sorted(set(definition['extra_entity_ids']) | set(structure_members))
                if len(ids) > 500:
                    raise InvalidSelection('Zu viele Zonenmitglieder')
                previous[STRUCTURE]['members'].update(structure_members)
                definition['extra_entity_ids'] = ids
                db.execute('UPDATE habitus_zones SET definition=? WHERE zone_id=?', (json.dumps(definition), zid))
            # Exactly one evaluation owner. Previous shadow sessions cannot coexist.
            for key in ('presence_shadow','presence_lifecycle','shadow_lighting'):
                previous.pop(key,None)
            db.execute('INSERT OR REPLACE INTO zone_context VALUES (?,?)',(zid,json.dumps(previous,allow_nan=False)))
            db.execute('INSERT OR REPLACE INTO zones VALUES (?,?)',(zid,revision+1))
            db.execute('DELETE FROM zone_meta WHERE key=?',('zone_presence_state:'+zid,))
            db.execute('INSERT INTO selection_journal(zone_id,revision,changes) VALUES (?,?,?)',
                (zid,revision+1,json.dumps({'$zone_presence':{'before':before,'mode':config.get('mode')}})))
            self.selections.prune_journal(db)
            return revision+1

    async def zone_operational(self,zid):
        return await durable(self._zone_operational,zid)
    def _zone_operational(self,zid):
        with closing(sqlite3.connect(self.path)) as db:
            row=db.execute('SELECT value FROM zone_meta WHERE key=?',('zone_presence_state:'+zid,)).fetchone()
            return json.loads(row[0]) if row else {}

    async def save_zone_operational(self,zid,revision,value):
        return await durable(self._save_zone_operational,zid,revision,deepcopy(value))
    def _save_zone_operational(self,zid,revision,value):
        text=json.dumps(value,allow_nan=False)
        if len(text)>200000: raise InvalidSelection('Betriebszwischenstand zu groß')
        with closing(sqlite3.connect(self.path,timeout=10)) as db,db:
            # Read zone existence, revision and value in one SQLite snapshot. An
            # identical checkpoint needs no writer reservation or process cache.
            row=db.execute('SELECT COALESCE(z.revision,0), m.value FROM habitus_zones AS h '
                'LEFT JOIN zones AS z ON z.zone_id=h.zone_id '
                'LEFT JOIN zone_meta AS m ON m.key=? WHERE h.zone_id=?',
                ('zone_presence_state:'+zid,zid)).fetchone()
            if type(revision) is int and revision>=0 and row and row[0]==revision and row[1]==text:return
            # The read may have raced with another writer. Recheck both revision
            # and value after acquiring the existing transactional write boundary.
            db.execute('BEGIN IMMEDIATE');self._shadow_revision(db,zid,revision)
            row=db.execute('SELECT value FROM zone_meta WHERE key=?',('zone_presence_state:'+zid,)).fetchone()
            if row and row[0]==text:return
            db.execute('INSERT OR REPLACE INTO zone_meta VALUES (?,?)',('zone_presence_state:'+zid,text))

    async def relevance_record(self,zid,revision,eid,occurred,origin,*,historical=False):
        return await durable(self._relevance_record,zid,revision,eid,occurred,origin,historical)
    def _relevance_record(self,zid,revision,eid,occurred,origin,historical):
        from .context import RETENTION
        from .attribution import ALLOWED_ORIGINS
        from .zone_presence import finite
        now=time.time()
        if not finite(occurred) or not now-RETENTION<=occurred<=now+5:return False
        with closing(sqlite3.connect(self.path,timeout=10)) as db,db:
            db.execute('BEGIN IMMEDIATE');self._shadow_revision(db,zid,revision)
            self.prune(db,now)
            selected=self.selections._read(db,zid)
            if selected['decisions'].get(eid)!='relevant':return False
            definition=json.loads(db.execute('SELECT definition FROM habitus_zones WHERE zone_id=?',(zid,)).fetchone()[0])
            if not definition['enabled']:return False
            if historical:
                # Historical visualization/analysis is transient. Never claim live origin
                # for retained imported evidence without an authorized receipt.
                return False
            last=db.execute('SELECT MAX(occurred) FROM activity_evidence WHERE zone_id=?',(zid,)).fetchone()[0]
            if last is not None and occurred-last<300:return False
            db.execute('INSERT OR IGNORE INTO activity_evidence VALUES (?,?,?,?)',
                       (zid,eid,occurred,origin if origin in ALLOWED_ORIGINS else 'unknown'))
            self.prune(db,now)
            return True
