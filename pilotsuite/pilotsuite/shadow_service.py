"""Opt-in shadow operation. No HomeAssistantClient write method is reachable here."""
from __future__ import annotations
import asyncio
from copy import deepcopy
from datetime import UTC, datetime
import logging
import time
import uuid

from .core.presence_shadow import SCHEMA, DEFAULTS, basis_for, evaluate, validate_spec, finite
from .core.selections import InvalidSelection, SelectionConflict
from .core.presence_kernel import validate_checkpoint

LOGGER = logging.getLogger(__name__)
TICK_SECONDS = 5


class PresenceShadowServiceMixin:
    def _shadow_init(self):
        self._shadow_views = {}  # Disposable rendering cache, never an authority.
        self._shadow_seen = set()

    def _shadow_fresh(self, now):
        try:
            stamp = datetime.fromisoformat(self._last_refresh_at).timestamp()
            return bool(self._connected and self._stream_connected and
                        0 <= now-stamp <= max(60, self.settings.refresh_interval_seconds*2))
        except (ValueError, TypeError, OverflowError):
            return False

    async def _shadow_basis_locked(self, zone_id, catalog=None):
        inventory = await self.selection_inventory(zone_id)
        cfg = await self.context.get(zone_id)
        catalog = await self.world.organization_catalog() if catalog is None else catalog
        basis = basis_for(inventory, cfg, catalog)
        scope = await self.world.scope((), tuple(basis['watched']))
        states = {r['entity_id']: r['state'] for r in scope['entities']}
        return inventory, cfg, basis, states

    @staticmethod
    def _shadow_authorized(inventory, cfg, basis):
        record = cfg.get('presence_shadow')
        if record is None:
            return 'disabled'
        if (not isinstance(record, dict) or set(record) != {'schema','revision','basis','spec','session','started_at','suspended_reason'}
                or record.get('schema') != SCHEMA or not isinstance(record.get('session'), str)
                or len(record['session']) != 32 or not finite(record.get('started_at'), 0, 4102444800)):
            return 'invalid_checkpoint'
        if record.get('suspended_reason') in ('basis_changed','zone_paused','invalid_checkpoint'):
            return record['suspended_reason']
        if not inventory.get('enabled'):
            return 'zone_paused'
        if record.get('revision') != inventory['revision'] or record.get('basis') != basis['hash']:
            return 'basis_changed'
        try:
            validate_checkpoint(cfg.get('presence_lifecycle'))
        except (InvalidSelection, TypeError, ValueError):
            return 'invalid_checkpoint'
        try:
            validate_spec(record['spec'], basis)
        except (InvalidSelection, TypeError, ValueError):
            return 'basis_changed'
        return 'running'

    async def presence_shadow(self, zone_id):
        """Side-effect-free GET: no collection, kernel transition or HA calls."""
        async with self._projection_lock:
            inventory, cfg, basis, states = await self._shadow_basis_locked(zone_id)
            return self._shadow_response(inventory, cfg, basis)

    def _shadow_response(self, inventory, cfg, basis):
        now = time.time()
        state = self._shadow_authorized(inventory, cfg, basis)
        stored = cfg.get('presence_shadow')
        record = stored if isinstance(stored, dict) else {}
        cached = self._shadow_views.get(inventory['zone_id'], {})
        view = cached.get('view')
        current = (state == 'running' and cached.get('session') == record.get('session')
                   and view and 0 <= now-view['observed_at'] <= TICK_SECONDS*3
                   and self._shadow_fresh(now) and cached.get('basis') == basis['hash'])
        if current:
            view = deepcopy(view)
        else:
            view = None  # Never return stale actionable-looking settings as current.
        try:
            public_spec = validate_spec(record.get('spec'), basis)
        except (InvalidSelection, TypeError, ValueError):
            public_spec = deepcopy(DEFAULTS)
        return {'schema':SCHEMA,'zone_id':inventory['zone_id'],'revision':inventory['revision'],
                'state':state,'enabled':state=='running','started_at':record.get('started_at'),
                'spec':public_spec,
                'inputs':{'sources':basis['source_rows'],'owner':basis['owner'],
                          'manual_overrides':basis['overrides'],'blockers':basis['blockers'],
                          'lights':basis['lights'],'lux_candidates':basis['lux'],
                          'issues':basis['issues'],'zone_enabled':inventory.get('enabled',False)},
                'current':view,'view_status':'current' if view else 'not_current',
                'execution':{'allowed':False,'actions':[]},'history_collection':False,
                'message':{'disabled':'Schattenvergleich ist aus.',
                           'basis_changed':'Zuordnung oder Identität geändert. Erneute Bestätigung erforderlich.',
                           'zone_paused':'Zone pausiert; Schattenvergleich ausgesetzt.',
                           'invalid_checkpoint':'Zwischenstand ungültig; bitte stoppen und neu prüfen.',
                           'running':'Schattenvergleich aktiv. Es wird nichts geschaltet.'}[state]}

    async def configure_presence_shadow(self, zone_id, payload):
        if (not isinstance(payload, dict) or type(payload.get('revision')) is not int
                or payload['revision'] < 0 or payload.get('confirm') is not True
                or payload.get('operation') not in ('start','stop')):
            raise InvalidSelection('Operation, Revision und ausdrückliche Bestätigung erforderlich')
        start = payload['operation']=='start'
        if set(payload) != ({'operation','revision','confirm','spec'} if start else {'operation','revision','confirm'}):
            raise InvalidSelection('Unbekannte oder fehlende Schattenparameter')
        async with self._projection_lock:
            inventory, cfg, basis, states = await self._shadow_basis_locked(zone_id)
            if payload['revision'] != inventory['revision']:
                raise SelectionConflict('Zone geändert; vor dem Start neu laden')
            record = None
            if start:
                if not inventory.get('enabled') or not self._shadow_fresh(time.time()):
                    raise InvalidSelection('Aktive Zone und frische HA-Verbindung erforderlich')
                spec = validate_spec(payload['spec'], basis)
                record = {'schema':SCHEMA,'revision':payload['revision']+1,'basis':basis['hash'],
                          'spec':spec,'session':uuid.uuid4().hex,'started_at':time.time(),'suspended_reason':None}
            await self.context.configure_shadow(zone_id, payload['revision'], record)
            self._shadow_views.pop(zone_id, None)
            self._shadow_seen.discard(zone_id)
            await self._derive()
            if start:
                await self._shadow_evaluate_locked(zone_id)
            inventory, cfg, basis, states = await self._shadow_basis_locked(zone_id)
            return self._shadow_response(inventory, cfg, basis)

    async def _shadow_evaluate_locked(self, zone_id, *, now=None, event=None, catalog=None):
        now = time.time() if now is None else now
        inventory, cfg, basis, states = await self._shadow_basis_locked(zone_id, catalog)
        state = self._shadow_authorized(inventory, cfg, basis)
        if state != 'running':
            self._shadow_views.pop(zone_id, None)
            self._shadow_seen.discard(zone_id)
            record = cfg.get('presence_shadow')
            if state != 'disabled' and isinstance(record, dict) and isinstance(record.get('session'), str):
                await self.context.suspend_shadow(zone_id, record['session'], state)
            return
        record = cfg['presence_shadow']
        try:
            cp, lights, view = evaluate({**record,'checkpoint':cfg.get('presence_lifecycle'),
                                        'lighting':cfg.get('shadow_lighting',{})}, basis, states, now=now,
                                        fresh=self._shadow_fresh(now), event=event,
                                        restart=zone_id not in self._shadow_seen)
            await self.context.update_shadow_checkpoint(zone_id, inventory['revision'], record['session'], cp, lights)
            self._shadow_views[zone_id] = {'basis':basis['hash'],'session':record['session'],'view':view}
            self._shadow_seen.add(zone_id)
        except (InvalidSelection, SelectionConflict, ValueError, TypeError):
            self._shadow_views.pop(zone_id, None)
            self._shadow_seen.discard(zone_id)
            # Do not alter invalid retained state or repeatedly invoke a write.
            LOGGER.warning('Shadow projection withheld because its basis or checkpoint is invalid')

    async def _shadow_tick_locked(self, *, now=None, event=None):
        # Existing zone registry and ContextStore are the only persisted owners.
        zones = await self.zones.list()
        alive = {z['zone_id'] for z in zones}
        for old in set(self._shadow_views)-alive:
            self._shadow_views.pop(old, None)
            self._shadow_seen.discard(old)
        catalog = None
        for zone in zones:
            try:
                cfg = await self.context.get(zone['zone_id'])
                if cfg.get('presence_shadow') is not None:
                    if catalog is None:
                        catalog = await self.world.organization_catalog()
                    await self._shadow_evaluate_locked(zone['zone_id'], now=now, event=event, catalog=catalog)
                else:
                    self._shadow_views.pop(zone['zone_id'], None)
            except asyncio.CancelledError:
                raise
            except Exception:
                # An optional shadow failure must not disconnect the shared HA stream
                # or stop processing unrelated zones. No retrying a device write exists.
                self._shadow_views.pop(zone['zone_id'], None)
                self._shadow_seen.discard(zone['zone_id'])
                LOGGER.warning('Shadow state unavailable; ordinary HA projection continues')

    async def _shadow_loop(self):
        while not self._stop.is_set():
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=TICK_SECONDS)
                continue
            except TimeoutError:
                pass
            try:
                async with self._projection_lock:
                    await self._shadow_tick_locked()
            except asyncio.CancelledError:
                raise
            except Exception:
                self._shadow_views.clear()
                LOGGER.exception('Shadow refresh failed; no device action is performed')
