"""Organization writes in the existing ContextStore and PlanStore database.

The zone revision is shared with roles and definitions. Mappings do not change
learning. Name-edit plans are durable, bounded and never blindly replayed.
"""
from __future__ import annotations
import asyncio
import json
import sqlite3
import time
import uuid
from contextlib import closing
from copy import deepcopy
from .organization import fingerprint, validate_saved
from .selections import InvalidSelection, SelectionConflict

PREFIX = 'organization_plan:'
MAX_PLANS = 100


async def durable(fn, *args):
    task = asyncio.create_task(asyncio.to_thread(fn, *args))
    try:
        return await asyncio.shield(task)
    except asyncio.CancelledError:
        try: await task
        finally: raise


class OrganizationContextMixin:
    async def save_organization(self, zone_id, revision, profile):
        validate_saved(profile)
        return await durable(self._save_organization, zone_id, revision, profile)

    def _save_organization(self, zone_id, revision, profile):
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            if type(revision) is not int or not db.execute('SELECT 1 FROM habitus_zones WHERE zone_id=?',(zone_id,)).fetchone():
                raise InvalidSelection('Ungültige Zone oder Revision')
            if self.selections._read(db,zone_id)['revision'] != revision:
                raise SelectionConflict('Zone seit dem Öffnen geändert; Zuordnung nicht gespeichert')
            cfg = self.read(db,zone_id)
            if cfg.get('organization') == profile:
                return {'revision':revision,'changed':False}
            # Only this key changes. Evidence, detector, learning, roles and unknown fields survive.
            before = deepcopy(cfg.get('organization'))
            cfg['organization'] = deepcopy(profile)
            db.execute('INSERT OR REPLACE INTO zone_context VALUES (?,?)',(zone_id,json.dumps(cfg)))
            db.execute('INSERT OR REPLACE INTO zones VALUES (?,?)',(zone_id,revision+1))
            db.execute('INSERT INTO selection_journal(zone_id,revision,changes) VALUES (?,?,?)',
                       (zone_id,revision+1,json.dumps({'$organization':{'before':before,'profile_hash':fingerprint(profile)}})))
            self.selections.prune_journal(db)
            if self.read(db,zone_id)['organization'] != profile:
                raise RuntimeError('Funktionsprofil konnte nicht zurückgelesen werden')
            return {'revision':revision+1,'changed':True}


class OrganizationPlanMixin:
    # Reuses PlanStore's lock and ContextStore's DB. No second filesystem store.
    async def organization_plan_create(self, zone_id, revision, operations, *, kind='names', details=None):
        async with self._lock:
            return await durable(self._organization_plan_create,zone_id,revision,operations,kind,details)

    def _organization_plan_create(self, zone_id, revision, operations, kind, details):
        if kind not in ('names','restore_names','repair_review') or not 1 <= len(operations) <= 30:
            raise InvalidSelection('Ungültiger oder leerer Ordnungsplan')
        plan={'id':uuid.uuid4().hex,'zone_id':zone_id,'revision':revision,'kind':kind,
              'created_at':time.time(),'expires_at':time.time()+900,'state':'preview',
              'operations':deepcopy(operations),'details':deepcopy(details or {})}
        plan['sha256']=fingerprint(plan)
        with closing(sqlite3.connect(self._context.path,timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            self._organization_revision(db,plan)
            if db.execute('SELECT COUNT(*) FROM zone_meta WHERE key LIKE ?', (PREFIX+'%',)).fetchone()[0] >= MAX_PLANS:
                raise InvalidSelection('Planlimit erreicht; vorhandene Wiederherstellungsdaten werden nicht automatisch gelöscht')
            db.execute('INSERT INTO zone_meta VALUES (?,?)',(PREFIX+plan['id'],json.dumps(plan)))
        return plan

    def _organization_revision(self, db, plan):
        if not db.execute('SELECT 1 FROM habitus_zones WHERE zone_id=?',(plan['zone_id'],)).fetchone():
            raise SelectionConflict('Zone existiert nicht mehr')
        if self._context.selections._read(db,plan['zone_id'])['revision'] != plan['revision']:
            raise SelectionConflict('Zone geändert; neuen Plan erstellen')

    async def organization_plan_get(self, zone_id, plan_id):
        async with self._lock:
            return await durable(self._organization_plan_get,zone_id,plan_id)

    def _organization_plan_get(self,zone_id,plan_id):
        if not isinstance(plan_id,str) or len(plan_id)!=32 or any(c not in '0123456789abcdef' for c in plan_id):
            raise InvalidSelection('Ungültige Plan-ID')
        with closing(sqlite3.connect(self._context.path)) as db:
            row=db.execute('SELECT value FROM zone_meta WHERE key=?',(PREFIX+plan_id,)).fetchone()
            if not row: raise InvalidSelection('Plan nicht gefunden')
            plan=json.loads(row[0])
            if plan['zone_id']!=zone_id: raise InvalidSelection('Plan gehört zu einer anderen Zone')
            return plan

    async def organization_plans(self,zone_id):
        async with self._lock:
            return await durable(self._organization_plans,zone_id)

    def _organization_plans(self,zone_id):
        with closing(sqlite3.connect(self._context.path)) as db:
            plans=[json.loads(row[0]) for row in db.execute('SELECT value FROM zone_meta WHERE key LIKE ?',(PREFIX+'%',))]
            return sorted([p for p in plans if p['zone_id']==zone_id],key=lambda p:p['created_at'],reverse=True)

    async def organization_claim(self,zone_id,plan_id,sha256):
        async with self._lock:
            return await durable(self._organization_claim,zone_id,plan_id,sha256)

    def _organization_claim(self,zone_id,plan_id,sha256):
        plan=self._organization_plan_get(zone_id,plan_id)
        if not isinstance(sha256,str) or plan['sha256']!=sha256:
            raise SelectionConflict('Plan-Prüfsumme stimmt nicht')
        if plan['kind']=='repair_review':
            raise InvalidSelection('Reparaturplan ist nur eine Vorschau, kein ausführbarer Auftrag')
        with closing(sqlite3.connect(self._context.path,timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            latest=json.loads(db.execute('SELECT value FROM zone_meta WHERE key=?',(PREFIX+plan_id,)).fetchone()[0])
            if latest['state'] != 'preview':
                return latest,False  # Durable receipt / unknown outcome: do not send again.
            self._organization_revision(db,latest)
            if time.time()>latest['expires_at']:
                raise SelectionConflict('Vorschau abgelaufen; neu prüfen')
            latest['state']='applying'
            for op in latest['operations']: op['outcome']='pending'
            db.execute('UPDATE zone_meta SET value=? WHERE key=?',(json.dumps(latest),PREFIX+plan_id))
            return latest,True

    async def organization_progress(self,zone_id,plan_id,index,outcome,confirmed=None):
        async with self._lock:
            return await durable(self._organization_progress,zone_id,plan_id,index,outcome,confirmed)

    def _organization_progress(self,zone_id,plan_id,index,outcome,confirmed):
        if outcome not in ('pending','sending','verified','conflict','unknown'):
            raise InvalidSelection('Ungültiger Bearbeitungszustand')
        plan=self._organization_plan_get(zone_id,plan_id)
        with closing(sqlite3.connect(self._context.path,timeout=10)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            plan=json.loads(db.execute('SELECT value FROM zone_meta WHERE key=?',(PREFIX+plan_id,)).fetchone()[0])
            plan['operations'][index]['outcome']=outcome
            if confirmed is not None: plan['operations'][index]['write_response_confirmed']=confirmed
            values=[x.get('outcome') for x in plan['operations']]
            plan['state']='verified' if all(v=='verified' for v in values) else 'attention' if any(v in ('unknown','conflict') for v in values) else 'applying'
            db.execute('UPDATE zone_meta SET value=? WHERE key=?',(json.dumps(plan),PREFIX+plan_id))
            return plan
