"""Presence Configurator, relevance data and bounded publication of OWNED helper packages.

Relevance authorizes analysis. Saving a behavior config does not rename/create/actuate
anything. Creating an output package or metadata edit uses an explicit durable plan.
Only managed outputs may be published; no automatic takeover of household automations.
"""
from __future__ import annotations
import asyncio
from copy import deepcopy
from datetime import datetime, UTC
import hashlib
import logging
import math
import time
import uuid
from .core import zone_presence as kernel
from .core.zone_presence_store import KEY
from .core.zone_ontology import ROLES as ONTOLOGY_ROLES,metadata_operation,metadata_matches,slug
from .core.zone_data import series_for,validate_window
from .core.organization import identity,same_identity,fingerprint
from .core.presence_adoption import validate_existing_inputs
from .core.selections import InvalidSelection,SelectionConflict
from .ha.client import HomeAssistantError

LOG=logging.getLogger(__name__)
PUBLICATION_HEARTBEAT_SECONDS = 20

class ZonePresenceServiceMixin:
    def _zone_presence_init(self):
        self._zone_views={};self._zone_traces={};self._zone_cache={};self._zone_io_lock=asyncio.Lock()
        self._zone_backoff={};self._zone_last_published={}
        self._zone_lighting_seen=set()

    async def _zone_basis(self,zid,catalog=None):
        inv=await self.selection_inventory(zid);cfg=await self.context.get(zid)
        catalog=await self.world.organization_catalog() if catalog is None else catalog
        relevant={r['entity_id'] for r in inv['items'] if r.get('decision')=='relevant' and not r.get('disabled')}
        own=(cfg.get(KEY) or {}).get('package') or {}
        relevant-=set(own.get('entities',{}).values()) # outputs never become inputs/learning evidence
        return inv,cfg,catalog,relevant

    async def zone_presence_view(self,zid):
        async with self._projection_lock:
            inv,cfg,catalog,relevant=await self._zone_basis(zid)
            config=cfg.get(KEY) or {}
            spec=config.get('spec') or {**deepcopy(kernel.DEFAULTS),'sources':kernel.suggested_sources(catalog,relevant)}
            cached=self._zone_views.get(zid,{})
            current=cached.get('current');now=time.time()
            if not (current and cached.get('revision')==inv['revision'] and self._presence_inputs_fresh(now) and
                    kernel.finite(current.get('observed_at')) and 0<=now-current['observed_at']<=15): current=None
            publication=cached.get('publication','not_published')
            if publication=='verified':publication='not_published'
            receipt=self._zone_last_published.get(zid,{})
            checked_at=receipt.get('verified_at')
            confirmed=bool(inv['enabled'] and cached.get('status')=='current' and current and current.get('valid') and
                config.get('mode')=='publish' and config.get('package') and
                receipt.get('revision')==inv['revision'] and
                receipt.get('signature')==(current.get('state'),current.get('deadline'),True) and
                kernel.finite(checked_at) and 0<=now-checked_at<PUBLICATION_HEARTBEAT_SECONDS and
                publication not in ('unknown_or_conflict','suspended_after_unknown_outcome'))
            if confirmed:publication='verified'
            from .core.presence_adoption import existing_presence_view
            from .core.organization import binding_view
            bound = binding_view(cfg, catalog)['assignments']
            ids = {row['entity_id'] for role in ('presence_status','presence_timer','presence_output')
                   for row in bound.get(role, []) if row.get('entity_id')}
            scope = await self.world.scope((), tuple(ids)) if ids else {'entities': []}
            observations = {row['entity_id']: row['state'] for row in scope['entities']}
            existing = existing_presence_view(cfg, catalog, observations,
                current if inv['enabled'] and config.get('mode') != 'paused' else None,
                fresh=self._presence_inputs_fresh(now), now=now,
                owned=(config.get('package') or {}).get('entities', {}).values())
            labels=[] # fetched on explicit ontology edit, not on every display poll
            from .core import zone_lighting
            light_config=cfg.get(zone_lighting.KEY) or {}
            lighting={'mode':light_config.get('mode','not_configured'),
                      'spec':light_config.get('spec',deepcopy(zone_lighting.DEFAULTS)),
                      'candidates':zone_lighting.candidates(catalog,relevant),
                      'status':cached.get('lighting_status','not_configured'),
                      'current':cached.get('lighting') if current else None,
                      'execution':{'allowed':False,'actions':[]}}
            return {'schema':kernel.SCHEMA,'zone_id':zid,'revision':inv['revision'],
                    'analysis_policy':'relevant_means_live_and_available_history','analysis_enabled':bool(inv['enabled']),
                    'spec':spec,'mode':config.get('mode','compare'),'package':config.get('package'),
                    'catalog':[r for r in catalog if r['entity_id'] in relevant],
                    'current':current,'status':cached.get('status','waiting'),'existing':existing,
                    'publication':publication,'publication_checked_at':checked_at if confirmed else None,
                    'trace':list(self._zone_traces.get(zid,[]))[-128:] if current else [],
                    'trace_basis':'session_only_not_recorded_history','lighting':lighting,
                    'history':self._zone_cache.get(zid,{}).get('summary',{'status':'not_loaded'}),
                    'dashboard_example':'habitus-zonen','ontology_roles':list(ONTOLOGY_ROLES)}

    async def zone_presence_configure(self,zid,payload):
        if (not isinstance(payload,dict) or set(payload)!={'revision','spec','mode'} or
            type(payload['revision']) is not int or payload['mode'] not in ('compare','publish','paused')):
            raise InvalidSelection('Revision, Konfiguration und Betriebsmodus erforderlich')
        async with self._zone_io_lock:
            async with self._projection_lock:
                inv,cfg,catalog,relevant=await self._zone_basis(zid)
                if inv['revision']!=payload['revision']:raise SelectionConflict('Zone geändert')
                spec=kernel.validate_spec(payload['spec'],relevant,catalog)
                validate_existing_inputs(cfg,catalog,spec)
                previous=cfg.get(KEY) or {};package=previous.get('package')
                if payload['mode']=='publish' and not package:
                    raise InvalidSelection('Zuerst ein geprüftes eigenes Ausgangspaket bereitstellen')
                basis=kernel.source_basis(spec,catalog)
                unchanged=(previous.get('schema')==kernel.SCHEMA and
                    isinstance(previous.get('session'),str) and bool(previous['session']) and
                    previous.get('spec')==spec and previous.get('mode')==payload['mode'] and
                    previous.get('basis')==basis and
                    not any(key in cfg for key in ('presence_shadow','presence_lifecycle','shadow_lighting')))
                if unchanged:
                    state=await self.context.zone_operational(zid)
                    # Explicit reconfiguration remains the recovery path for a suspended
                    # evaluator or publisher. An ordinary retry must not reset its clock.
                    unchanged=not (state.get('suspended') or state.get('output_suspended'))
                # Existing output packages may have acquired external consumers. This
                # does not entitle the runtime to disable or rewrite those consumers.
                if not unchanged:
                    record={'schema':kernel.SCHEMA,'spec':spec,'mode':payload['mode'],'session':uuid.uuid4().hex,
                            'basis':basis,'package':package}
                    await self.context.save_zone_presence(zid,inv['revision'],record)
                    self._zone_views.pop(zid,None);self._zone_last_published.pop(zid,None)
                    await self._zone_presence_tick_locked()
            if package and not unchanged:
                await self._zone_invalidate_package(package)
        return await self.zone_presence_view(zid)

    async def _zone_existing_adoption_review(self, zid, revision):
        """Explicit structural read of the saved existing chain. No HA/local config writes."""
        from .core.organization import binding_view
        from .core.presence_adoption import adoption_targets, adoption_plan, validate_automation_ids
        from .domain.automation_inspection import inspect_automation

        async def basis():
            inv, cfg, _, catalog = await self._organization_basis(zid, revision)
            if not self._presence_inputs_fresh(time.time()):
                raise SelectionConflict('Bestandsdaten nicht aktuell; erneut laden')
            assignments = binding_view(cfg, catalog)['assignments']
            roles = ('presence_status','presence_timer','presence_output','presence_automations','presence_sources')
            rows = [row for role in roles for row in assignments.get(role, [])]
            if any(row.get('status') not in ('bound','renamed','exact_id_only') or
                   not row.get('in_registry') or row.get('disabled') for row in rows):
                raise SelectionConflict('Bestandszuordnung enthält ungeklärte oder deaktivierte Identitäten')
            def first(role):
                return next((row['entity_id'] for row in assignments.get(role, [])), None)
            config = cfg.get(KEY) or {}
            sources = sorted({row['entity_id'] for row in config.get('spec', {}).get('sources', [])} |
                             {row['entity_id'] for row in assignments.get('presence_sources', [])})
            runtime = {'owner': first('presence_status'), 'timer': first('presence_timer'),
                       'sensor': first('presence_output'), 'raw_sources': sources}
            selected = [row['entity_id'] for row in assignments.get('presence_automations', [])]
            by_id = {row['entity_id']: row for row in catalog}
            refs = adoption_targets(runtime)
            if any(eid not in by_id or by_id[eid].get('disabled') or not by_id[eid].get('in_registry') for eid in refs):
                raise SelectionConflict('Eine zugeordnete Quelle fehlt oder ist deaktiviert')
            signature = fingerprint({'runtime': runtime, 'selected': selected,
                'identities': [identity(by_id[eid]) for eid in sorted(set(refs + selected))]})
            return runtime, selected, by_id, signature

        if self._automation_review_lock.locked():
            raise HomeAssistantError('Bestandsprüfung läuft bereits')
        async with self._automation_review_lock:
            runtime, selected, catalog, signature = await basis()
            refs = adoption_targets(runtime)
            if not refs and not selected:
                raise InvalidSelection('Zuerst vorhandenen Anwesenheitsbestand zuordnen')
            inspected = []
            async with asyncio.timeout(90):
                ids = set(selected)
                for start in range(0, len(refs), 40):
                    related = await self.client.related_automations(refs[start:start + 40])
                    ids.update(eid for values in related.values() for eid in values)
                ids = validate_automation_ids(sorted(ids))
                if any(eid not in catalog or catalog[eid].get('disabled') or not catalog[eid].get('in_registry') for eid in ids):
                    raise SelectionConflict('Gefundene Automation fehlt im aktiven Register')
                draft = {'current_pattern': {'sources': refs}, 'fields': {'target_ids':
                    [eid for eid in (runtime['owner'], runtime['timer'], runtime['sensor']) if eid]}}
                for eid in ids:
                    raw = await self.client.automation_config(eid)
                    inspected.append(inspect_automation(raw, draft, eid))
            _, _, after, after_signature = await basis()
            if after_signature != signature or any(
                eid not in after or after[eid].get('disabled') or not after[eid].get('in_registry') or
                identity(after[eid]) != identity(catalog[eid]) for eid in ids):
                raise SelectionConflict('Bestandsbasis während der Prüfung geändert')
            # Keep explicitly selected unmatched automations visible; no silent omission.
            result = adoption_plan(zid, revision, runtime, inspected, include_unrelated=True)
            for row in result['automations']:
                value = after[row['automation_id']].get('state')
                row['observed_enabled'] = True if value == 'on' else False if value == 'off' else None
            result.update(mode='existing_control',
                coverage='related_lookup_and_selected_not_exhaustive', checked_at=time.time(),
                control_changed=False, persisted=False)
            result['summary'].update(
                writers=sum(row['writes_owner'] or row['writes_timer'] for row in result['automations']),
                consumers=sum(row['usage'] == 'consumer' for row in result['automations']),
                mixed=sum(row['usage'] == 'mixed_writer' for row in result['automations']))
            return result

    async def zone_lighting_configure(self,zid,payload):
        from .core import zone_lighting
        if (not isinstance(payload,dict) or set(payload)!={'revision','spec','mode'} or
                type(payload['revision']) is not int or payload['mode'] not in ('compare','paused')):
            raise InvalidSelection('Revision, Lichtkonfiguration und Vergleich/Pause erforderlich')
        async with self._zone_io_lock:
            async with self._projection_lock:
                inv,cfg,catalog,relevant=await self._zone_basis(zid)
                if inv['revision']!=payload['revision']:raise SelectionConflict('Zone geändert')
                presence=cfg.get(KEY) or {}
                if not presence.get('spec'):raise InvalidSelection('Zuerst die Zonenpräsenz konfigurieren')
                spec=zone_lighting.validate_spec(payload['spec'],catalog,relevant)
                record={'spec':spec,'mode':payload['mode'],'basis':zone_lighting.basis(spec,catalog,presence)}
                operational=await self.context.zone_operational(zid)
                revision=await self.context.save_zone_lighting(zid,inv['revision'],record,
                    recover=bool((operational.get('lighting') or {}).get('suspended')))
                if revision!=inv['revision']:self._zone_lighting_seen.discard(zid)
                await self._zone_presence_tick_locked()
        return await self.zone_presence_view(zid)

    async def _zone_lighting_tick(self,zid,inv,cfg,catalog,relevant,state,view,now,event):
        from .core import zone_lighting
        record=cfg.get(zone_lighting.KEY)
        if not record:return None,None,'not_configured'
        if record.get('mode')=='paused':return None,None,'paused'
        previous=state.get('lighting') or {}
        if previous.get('suspended'):return previous,None,previous['suspended']
        try:
            spec=zone_lighting.validate_spec(record['spec'],catalog,relevant)
            if record.get('basis')!=zone_lighting.basis(spec,catalog,cfg.get(KEY) or {}):
                return {**previous,'suspended':'basis_changed'},None,'basis_changed'
            watched=spec['lights']+spec['manual_entities']+([spec['daylight_source']] if spec['daylight_source'] else [])
            scope=await self.world.scope((),tuple(watched))
            observations={row['entity_id']:row['state'] for row in scope['entities']}
            point,lighting=zone_lighting.evaluate(spec,state.get('lighting'),observations,view,
                now=now,fresh=self._presence_inputs_fresh(now),event=event,restart=zid not in self._zone_lighting_seen)
            self._zone_lighting_seen.add(zid)
            return point,lighting,'current'
        except (InvalidSelection,ValueError,TypeError,KeyError):
            self._zone_lighting_seen.discard(zid)
            return {**previous,'suspended':'configuration_required'},None,'configuration_required'

    async def _zone_presence_tick_locked(self,event=None):
        catalog=await self.world.organization_catalog()
        for zone in await self.zones.list():
            zid=zone['zone_id'];record={};inv=None
            try:
                inv,cfg,catalog,relevant=await self._zone_basis(zid,catalog);record=cfg.get(KEY) or {}
                if event and event.get('entity_id') not in relevant:continue
                if not inv['enabled'] or record.get('mode')=='paused':
                    self._zone_views[zid]={'revision':inv['revision'],'status':'paused','current':None};continue
                spec=record.get('spec') or {**deepcopy(kernel.DEFAULTS),'sources':kernel.suggested_sources(catalog,relevant)}
                spec=kernel.validate_spec(spec,relevant,catalog)
                validate_existing_inputs(cfg,catalog,spec)
                basis=kernel.source_basis(spec,catalog);state=await self.context.zone_operational(zid)
                if record and record.get('basis')!=basis or state.get('suspended'):
                    await self.context.save_zone_operational(zid,inv['revision'],{**state,'suspended':'source_basis_changed'})
                    self._zone_views[zid]={'revision':inv['revision'],'status':'source_basis_changed','current':None};continue
                # Revision alone (e.g. changed title) never silently rebinds sources. The
                # semantic basis above protects identity and typed source settings.
                scope=await self.world.scope((),tuple(relevant))
                observations={r['entity_id']:r['state'] for r in scope['entities']}
                now=time.time(); checkpoint,view=kernel.evaluate(spec,state.get('checkpoint'),observations,
                    now=now,fresh=self._presence_inputs_fresh(now),event=event)
                by_id={r['entity_id']:r for r in catalog}
                for row in view['sources']:row['name']=by_id.get(row['entity_id'],{}).get('name',row['entity_id'])
                old=self._zone_views.get(zid,{}).get('current')
                if not old or (old['state'],old['reason'],old['deadline'])!=(view['state'],view['reason'],view['deadline']):
                    self._zone_traces.setdefault(zid,[]).append({k:view[k] for k in ('state','reason','deadline','observed_at')})
                    self._zone_traces[zid]=self._zone_traces[zid][-128:]
                light_point,lighting,light_status=await self._zone_lighting_tick(zid,inv,cfg,catalog,relevant,state,view,now,event)
                await self.context.save_zone_operational(zid,inv['revision'],{**state,'basis':basis,'checkpoint':checkpoint,
                        **({'lighting':light_point} if light_point is not None else {}),
                        'session':record.get('session'),'suspended':None})
                self._zone_views[zid]={'revision':inv['revision'],'basis':basis,'current':view,'status':'current',
                                     'lighting':lighting,'lighting_status':light_status}
                if event and event.get('entity_id') in relevant:
                    old_e,new_e=event.get('old_state'),event.get('new_state')
                    if isinstance(old_e,dict) and isinstance(new_e,dict) and old_e.get('state')=='off' and new_e.get('state')=='on':
                        source=next((s for s in spec['sources'] if s['entity_id']==event['entity_id']),None)
                        at=kernel.timestamp(new_e.get('last_changed'))
                        if source and source['kind']!='support' and at is not None:
                            await self.context.relevance_record(zid,inv['revision'],source['entity_id'],at,
                                self.attribution.classify_state(new_e))
            except asyncio.CancelledError:raise
            except (InvalidSelection,SelectionConflict,ValueError,TypeError):
                if record and inv is not None:
                    state=await self.context.zone_operational(zid)
                    await self.context.save_zone_operational(zid,inv['revision'],{**state,'suspended':'configuration_changed'})
                self._zone_views[zid]={'status':'configuration_required','current':None}
            except Exception:
                self._zone_views[zid]={'status':'data_unavailable','current':None}
                LOG.warning('Zone presence unavailable; other zones continue')

    async def zone_data(self,zid,payload):
        if not isinstance(payload,dict) or set(payload)!={'revision','start','end','entity_ids'}:
            raise InvalidSelection('Zeitraum, Revision und relevante Quellen auswählen')
        a,b=validate_window(payload['start'],payload['end'],time.time())
        if type(payload['revision']) is not int or not isinstance(payload['entity_ids'],list):
            raise InvalidSelection('Ungültige Historienparameter')
        ids=payload['entity_ids']
        if not ids or len(ids)>100 or any(not isinstance(e,str) for e in ids) or len(set(ids))!=len(ids):
            raise InvalidSelection('Eine bis 100 unterschiedliche Quellen je Abruf')
        async with self._history_lock:
            async with self._projection_lock:
                inv,cfg,catalog,relevant=await self._zone_basis(zid)
                if inv['revision']!=payload['revision']:raise SelectionConflict('Quellenstand geändert')
                if not inv['enabled'] or not set(ids)<=relevant:raise InvalidSelection('Nur relevante Quellen einer aktiven Zone')
                identities={e:identity(next(r for r in catalog if r['entity_id']==e)) for e in ids}
            raw=await self.client.history(ids,a,b)
            async with self._projection_lock:
                after,_,new_catalog,new_relevant=await self._zone_basis(zid)
                fresh={r['entity_id']:r for r in new_catalog}
                if after['revision']!=inv['revision'] or not set(ids)<=new_relevant or any(
                    not same_identity(v,fresh.get(e,{})) for e,v in identities.items()):
                    raise SelectionConflict('Historienantwort gehört nicht mehr zur bestätigten Quelle')
            sources=series_for({eid:raw['records'].get(eid,[]) for eid in ids},catalog,a,b)
            result={'zone_id':zid,'revision':inv['revision'],'start':a,'end':b,'sources':sources,
                'analysis_policy':'relevance','record_count':sum(s['record_count'] for s in sources),
                'history_exhaustive':False,'warning':'Recorder-Zustände; Lücken bleiben unbekannt. Diagramme sind Anzeigeproben, keine Schaltbelege.'}
            self._zone_cache[zid]={'summary':{'status':'loaded','start':a,'end':b,'sources':len(sources),
                                            'records':result['record_count'],'loaded_at':time.time()},'data':result}
            return result

    async def _zone_presence_loop(self):
        while not self._stop.is_set():
            try:await asyncio.wait_for(self._stop.wait(),timeout=5);continue
            except TimeoutError:pass
            try:
                async with self._projection_lock:await self._zone_presence_tick_locked()
                # Never drive network operations under the event projection lock.
                if self.client._token:
                    await self._zone_publish_all()

            except asyncio.CancelledError:raise
            except Exception:LOG.warning('Optional zone worker failed; main projection continues')

    async def _zone_history_loop(self):
        while not self._stop.is_set():
            try:await asyncio.wait_for(self._stop.wait(),timeout=5);continue
            except TimeoutError:pass
            try:
                if self.client._token:await self._zone_auto_history()
            except asyncio.CancelledError:raise
            except Exception:LOG.warning('Relevant history unavailable; live processing continues')

    async def _zone_auto_history(self):
        if not self._presence_inputs_fresh(time.time()) or self._history_lock.locked():return
        for zone in await self.zones.list():
            zid=zone['zone_id'];now=time.time()
            if self._zone_backoff.get(zid,0)>now:continue
            async with self._projection_lock:
                inv,cfg,catalog,relevant=await self._zone_basis(zid)
            if not zone['enabled'] or not relevant:continue
            summary=self._zone_cache.get(zid,{}).get('summary',{})
            if summary.get('revision')==inv['revision'] and now-summary.get('loaded_at',0)<900:continue
            # One batch per tick, bounded queues and backoff; all relevant entities rotate.
            cursor=summary.get('cursor',0) if summary.get('revision')==inv['revision'] else 0
            ids=sorted(relevant)[cursor:cursor+40]
            try:
                await self.zone_data(zid,{'revision':inv['revision'],'start':datetime.fromtimestamp(now-86400,UTC).isoformat(),
                    'end':datetime.fromtimestamp(now,UTC).isoformat(),'entity_ids':ids})
                cursor+=len(ids); complete=cursor>=len(relevant)
                self._zone_cache[zid]['summary'].update(revision=inv['revision'],cursor=0 if complete else cursor,
                    loaded_at=now if complete else 0,automatic_window_hours=24,all_relevant_in_window=complete)
            except (HomeAssistantError,InvalidSelection,SelectionConflict,TimeoutError):
                self._zone_backoff[zid]=now+60
                self._zone_cache[zid]={'summary':{'status':'unavailable_or_too_large','retry_after':now+60}}
            return

    async def zone_package_preview(self,zid,payload):
        if isinstance(payload,dict) and 'helper_role' in payload:
            return await self._zone_missing_helper_preview(zid,payload)
        if not isinstance(payload,dict) or set(payload)!={'revision'}:raise InvalidSelection('Revision erforderlich')
        inv,cfg,zone,catalog=await self._organization_basis(zid,payload['revision'])
        record=cfg.get(KEY)
        if not record:raise InvalidSelection('Zuerst die Präsenzkonfiguration speichern')
        if record.get('package'):raise InvalidSelection('Zonen-Ausgangspaket existiert bereits')
        token=hashlib.sha256(zid.encode()).hexdigest()[:12]
        rows=await self.client.zone_output_registry();existing={r['entity_id'] for r in rows}
        operations=[]
        for role,domain in [('anwesenheit_intern','input_boolean'),('entscheidung_gueltig','input_boolean'),
                            ('gueltig_bis','input_datetime'),('nachlauf','timer')]:
            name=f'ps_{token}_{role}';eid=domain+'.'+name
            if eid in existing:raise SelectionConflict('Helferkennung existiert bereits; keine Anlage/Wiederholung nach Namensähnlichkeit')
            operations.append({'role':role,'domain':domain,'name':name,'entity_id':eid,'effect':'create_new_zone_helper'})
        name=zone['name']+' Anwesenheit'
        public_id='binary_sensor.'+slug(zone['name'])+'_anwesenheit'
        if public_id in existing:
            raise SelectionConflict('Semantischer Anwesenheitssensor existiert bereits; zuerst bestehenden Ausgang und seine Schreiber prüfen, kein Duplikat anlegen')
        operations.append({'role':'sensor','domain':'template','name':name,'entity_id':public_id,'effect':'create_template_binary_sensor'})
        await self._zone_package_autolabel(cfg, zone, operations)
        return await self.plans.organization_plan_create(zid,inv['revision'],operations,kind='presence_package',
            details={'no_existing_automation_takeover':True,'previously_existing_outputs_untouched':True,
                     'grace_seconds':record['spec']['grace_seconds'],'lease_seconds':90,'availability_resolution_seconds':60})

    async def _zone_missing_helper_preview(self,zid,payload):
        if (set(payload)!={'revision','helper_role','duration_seconds'} or
            type(payload['revision']) is not int or payload['revision']<0 or
            payload['helper_role'] not in ('presence_status','presence_timer')):
            raise InvalidSelection('Einzelnen Boolean oder Timer mit gültiger Revision auswählen')
        role=payload['helper_role'];duration=payload['duration_seconds']
        if ((role=='presence_timer' and (type(duration) is not int or not 1<=duration<=86400)) or
            (role=='presence_status' and duration is not None)):
            raise InvalidSelection('Timerdauer muss 1–86400 Sekunden sein; Boolean hat keine Dauer')
        inv,cfg,zone,_=await self._organization_basis(zid,payload['revision'])
        # A missing/unavailable saved identity is not an empty role. Never replace it.
        if cfg.get('organization',{}).get('assignments',{}).get(role):
            raise SelectionConflict('Funktion bereits zugeordnet; vorhandene Identität prüfen statt Ersatz anlegen')
        if (cfg.get(KEY) or {}).get('package'):
            raise SelectionConflict('Eigenes Ausgangspaket vorhanden; dessen Helfer zuerst prüfen')
        domain='timer' if role=='presence_timer' else 'input_boolean'
        title='Nachlauf' if role=='presence_timer' else 'Anwesenheit intern'
        token=hashlib.sha256(zid.encode()).hexdigest()[:12]
        name=f'ps_{token}_bestand_{role}';eid=domain+'.'+name
        rows=await self.client.zone_output_registry()
        if any(r['entity_id']==eid for r in rows):
            raise SelectionConflict('Helferkennung existiert bereits; vorhandenen Plan oder Bestand prüfen')
        operations = [
            {'role':role,'domain':domain,'name':name,'entity_id':eid,
             'suggested_display_name':zone['name']+' '+title,'effect':'create_unconnected_helper'}]
        await self._zone_package_autolabel(cfg, zone, operations)
        return await self.plans.organization_plan_create(zid,inv['revision'],operations,
            kind='presence_helper',details={'helper_role':role,'grace_seconds':duration or 300,
                'duration_seconds':duration,'automation_connected':False,'binding_changed':False,
                'control_enabled':False,'initial_state_is_presence_evidence':False,
                'recovery':'No automatic deletion; inspect consumers before removing the new helper.',
                'review_required':['existing_helpers','writers_and_consumers','automation_wiring','valid_public_output']})

    async def _zone_package_autolabel(self, cfg, zone, operations):
        """Extend the existing creation plan, never a second post-creation job."""
        from .core.zone_structure import KEY as STRUCTURE
        profile = cfg.get(STRUCTURE)
        if not profile:
            return  # Historical callers retain their explicit ontology workflow.
        if len(set(zone['extra_entity_ids']) | {op['entity_id'] for op in operations}) > 500 or len(profile['members']) + len(operations) > 500:
            raise InvalidSelection('Zone vor der Helferanlage auf höchstens 500 Mitglieder begrenzen')
        if any(op['role']=='sensor' for op in operations) and any(
                'Habitus Zone' in member['roles'] for member in profile['members'].values()):
            raise SelectionConflict('Ein Zonenanker ist bereits verbunden; Bestandskette verwenden')
        labels = await self.client.zone_labels()
        if profile['label_id'] not in {label['label_id'] for label in labels}:
            raise SelectionConflict('Zonenlabel fehlt; Einrichtung zuerst abgleichen')
        by_name = {}
        for label in labels:
            by_name.setdefault(label['name'], []).append(label['label_id'])
        titles = {'anwesenheit_intern': 'Anwesenheit intern', 'entscheidung_gueltig': 'Präsenz gültig',
                  'gueltig_bis': 'Präsenz gültig bis', 'nachlauf': 'Präsenznachlauf',
                  'sensor': 'Anwesenheit', 'presence_status': 'Anwesenheit intern', 'presence_timer': 'Nachlauf'}
        for op in operations:
            roles = (['Habitus Zone', 'Habitus Übersicht', 'Habitus Status'] if op['role']=='sensor'
                     else ['Habitus Status', 'Habitus Diagnose'] if op['domain']=='timer' else ['Habitus Diagnose'])
            if any(len(by_name.get(role, [])) != 1 for role in roles):
                raise SelectionConflict('Benötigte Habitus-Rollenlabels fehlen oder sind mehrdeutig')
            name = zone['name'] + ' ' + titles[op['role']]
            if len(name) > 120:
                raise InvalidSelection('Zonenname für Helfer zu lang')
            op['metadata'] = {'name': name, 'labels': sorted({profile['label_id']} | {by_name[role][0] for role in roles})}
            op['habitus_roles'] = roles
        await self._zone_structure_guard(zone['zone_id'], operations)

    async def _zone_finish_created_metadata(self, zid, plan, index, row, *, may_write=True):
        """Only the exact newly created identity, with durable before/after evidence."""
        op = (await self.plans.organization_plan_get(zid, plan['id']))['operations'][index]
        if 'metadata' not in op:
            return row
        receipt = op.get('receipt', {})
        if not same_identity(receipt.get('identity', {}), row):
            raise SelectionConflict('Helferidentität vor Autolabeling nicht bestätigt')
        current = {'name': row.get('name'), 'labels': sorted(row.get('labels') or [])}
        before = receipt.get('metadata_before')
        after = receipt.get('metadata_after')
        if before is None:
            before = current
            after = {'name': op['metadata']['name'], 'labels': sorted(set(before['labels']) | set(op['metadata']['labels']))}
            await self.plans.organization_receipt(zid, plan['id'], index,
                {'metadata_before': before, 'metadata_after': after})
        if current == after:
            return row
        if current != before or not may_write:
            raise SelectionConflict('Helfermetadaten zwischenzeitlich geändert; nicht überschrieben')
        await self._organization_basis(zid, plan['revision'])
        fresh = next((r for r in await self.client.zone_output_registry() if r['entity_id']==row['entity_id']), {})
        if (not same_identity(row, fresh) or fresh.get('disabled_by') is not None or
                {'name': fresh.get('name'), 'labels': sorted(fresh.get('labels') or [])} != before):
            raise SelectionConflict('Helfer vor der Beschriftung geändert')
        await self._zone_structure_guard(zid, [dict(op, metadata=after)])
        await self._organization_basis(zid, plan['revision'])
        try:
            await self.client.zone_set_metadata(row['entity_id'], **after)
        except HomeAssistantError:
            pass  # A lost response is resolved only by independent readback.
        observed = next((r for r in await self.client.zone_output_registry() if r['entity_id']==row['entity_id']), {})
        if (not same_identity(row, observed) or observed.get('disabled_by') is not None or
                {'name': observed.get('name'), 'labels': sorted(observed.get('labels') or [])} != after):
            raise HomeAssistantError('Autolabeling nicht unabhängig bestätigt')
        await self.plans.organization_receipt(zid, plan['id'], index, {'metadata_verified': True})
        return observed

    async def zone_package_apply(self,zid,plan_id,payload):
        if not isinstance(payload,dict) or set(payload)!={'sha256','confirm'} or payload['confirm'] is not True:
            raise InvalidSelection('Konkreten Ausgangsplan bestätigen')
        async with self._zone_io_lock:
            plan=await self.plans.organization_plan_get(zid,plan_id)
            if plan['kind'] not in ('presence_package','presence_helper'):raise InvalidSelection('Kein Zonen-Helferplan')
            plan,claimed=await self.plans.organization_claim(zid,plan_id,payload['sha256'])
            if not claimed:
                if plan['kind']=='presence_helper' and plan['state']=='verified':
                    return {**plan,'write_repeated':False,'recovery':'creation_previously_verified'}
                current=(await self.context.get(zid)).get(KEY) or {}
                if (current.get('package') or {}).get('plan_id')==plan_id:
                    return {**plan,'write_repeated':False,'recovery':'already_bound'}
                if plan.get('state') not in ('applying','attention','verified'):
                    return {**plan,'write_repeated':False}
                # A claimed package is a durable transaction. Resumption is only
                # allowed while its exact zone revision still exists.
                await self._organization_basis(zid,plan['revision'])
            identities={};entities={}
            for index,op in enumerate(plan['operations']):
                outcome=op.get('outcome')
                if not claimed and outcome in ('verified','sending','unknown'):
                    rows=await self.client.zone_output_registry()
                    row=self._zone_package_receipt_row(op,rows)
                    if row is None:
                        if outcome=='sending':
                            plan=await self.plans.organization_progress(zid,plan_id,index,'unknown')
                        return {**plan,'write_repeated':False,'recovery':'ownership_unconfirmed'}
                    identities[op['role']]=identity(row);entities[op['role']]=row['entity_id']
                    if outcome!='verified':
                        await self.plans.organization_receipt(zid,plan_id,index,
                            {'identity':identity(row),'entity_id':row['entity_id']})
                    try:
                        await self._zone_finish_created_metadata(zid, plan, index, row, may_write=outcome!='verified')
                    except SelectionConflict:
                        return await self.plans.organization_progress(zid,plan_id,index,'conflict')
                    except (HomeAssistantError,TimeoutError):
                        return await self.plans.organization_progress(zid,plan_id,index,'unknown')
                    if outcome!='verified':
                        await self.plans.organization_receipt(zid,plan_id,index,
                            {'identity':identity(row),'entity_id':row['entity_id']})
                        plan=await self.plans.organization_progress(zid,plan_id,index,'verified',True)
                    continue
                if not claimed and outcome=='conflict':
                    return {**plan,'write_repeated':False,'recovery':'conflict'}
                if not claimed and outcome!='pending':
                    return {**plan,'write_repeated':False,'recovery':'invalid_operation_state'}
                try:
                    await self._organization_basis(zid,plan['revision'])
                    before=await self.client.zone_output_registry()
                    if any(r['entity_id']==op['entity_id'] for r in before):
                        raise SelectionConflict('Identität nicht mehr frei')
                    await self.plans.organization_progress(zid,plan_id,index,'sending')
                    # Registry I/O and durable progress both yield. Recheck the
                    # user's exact zone basis immediately before the HA write.
                    await self._organization_basis(zid,plan['revision'])
                    if op['domain']=='template':
                        # Native HA transliteration is not our ontology transliteration.
                        # Create a brand-new ASCII identity, then set its display name only.
                        result=await self.client.zone_create_binary_sensor(op['entity_id'].split('.',1)[1],entities['anwesenheit_intern'],
                            entities['entscheidung_gueltig'],entities['gueltig_bis'])
                        entry=result.get('result') or {};entry_id=entry.get('entry_id') if isinstance(entry,dict) else None
                        entry_id=entry_id or result.get('entry_id')
                        if not isinstance(entry_id,str) or not entry_id:
                            raise HomeAssistantError('Anlage nicht identifizierbar')
                        await self.plans.organization_receipt(zid,plan_id,index,{'config_entry_id':entry_id})
                    else:
                        result=await self.client.zone_create_storage_helper(op['domain'],op['name'],grace_seconds=plan['details']['grace_seconds'])
                        if not isinstance(result,dict) or not result.get('id'):raise HomeAssistantError('Anlage nicht identifizierbar')
                        await self.plans.organization_receipt(zid,plan_id,index,{'storage_id':result['id']})
                    after=await self.client.zone_output_registry()
                    new=[r for r in after if r['entity_id'] not in {x['entity_id'] for x in before}]
                    if op['domain']=='template':
                        matches=[r for r in new if r.get('config_entry_id')==entry_id and r.get('platform')=='template' and r['entity_id']==op['entity_id']]
                    else:
                        matches=[r for r in new if r.get('platform')==op['domain'] and r.get('unique_id')==result['id'] and r['entity_id']==op['entity_id']]
                    if (len(matches)!=1 or not matches[0].get('unique_id') or
                        matches[0].get('disabled_by') is not None):
                        raise HomeAssistantError('Unabhängiges aktives Identitäts-Readback fehlgeschlagen')
                    row=matches[0];identities[op['role']]=identity(row);entities[op['role']]=row['entity_id']
                    await self.plans.organization_receipt(zid,plan_id,index,{'identity':identity(row),'entity_id':row['entity_id']})
                    if 'metadata' in op:
                        await self._zone_finish_created_metadata(zid, plan, index, row)
                    elif op['domain']=='template':
                        await self.client.zone_set_metadata(row['entity_id'],name=op['name'],labels=row.get('labels') or [])
                        named=next((r for r in await self.client.zone_output_registry() if r['entity_id']==row['entity_id']),{})
                        if not same_identity(row,named) or named.get('name')!=op['name']:
                            raise HomeAssistantError('Neuer Sensor-Anzeigename nicht unabhängig bestätigt')
                    await self.plans.organization_progress(zid,plan_id,index,'verified',True)
                except SelectionConflict:return await self.plans.organization_progress(zid,plan_id,index,'conflict')
                except (HomeAssistantError,TimeoutError):return await self.plans.organization_progress(zid,plan_id,index,'unknown')
            if plan['kind']=='presence_helper':
                # The durable operation receipt already independently confirmed
                # creation. No binding follows: do not imply a live functionality
                # check or let an unnecessary later read mask this historical fact.
                return await self.plans.organization_plan_get(zid,plan_id)
            latest={r['entity_id']:r for r in await self.client.zone_output_registry()}
            if len(entities)!=len(plan['operations']) or any(
                not same_identity(identities[role],latest.get(eid,{})) or
                latest[eid].get('disabled_by') is not None for role,eid in entities.items()):
                raise SelectionConflict('Ausgangsidentität vor Bindung geändert')
            plan = await self.plans.organization_plan_get(zid, plan_id)
            for index, op in enumerate(plan['operations']):
                expected = op.get('receipt', {}).get('metadata_after')
                row = latest.get(op['entity_id'], {})
                if expected and {'name': row.get('name'), 'labels': sorted(row.get('labels') or [])} != expected:
                    return await self.plans.organization_progress(zid, plan_id, index, 'conflict')
            try:
                await self._zone_structure_guard(zid, plan['operations'])
            except SelectionConflict:
                return await self.plans.organization_progress(zid, plan_id, len(plan['operations'])-1, 'conflict')
            async with self._projection_lock:
                inv,cfg,catalog,relevant=await self._zone_basis(zid)
                if inv['revision']!=plan['revision']:
                    return await self.plans.organization_progress(zid,plan_id,len(plan['operations'])-1,'conflict')
                config=deepcopy(cfg[KEY]);config['package']={'plan_id':plan_id,'entities':entities,'identities':identities}
                config['mode']='compare' # Creation never turns on presence/control.
                members = {op['entity_id']: {'identity': identities[op['role']], 'roles': op['habitus_roles']}
                           for op in plan['operations'] if 'metadata' in op}
                await self.context.save_zone_presence(zid,inv['revision'],config, structure_members=members or None)
            return await self.plans.organization_plan_get(zid,plan_id)

    @staticmethod
    def _zone_package_receipt_row(op,rows):
        """Resolve only an output proven by this plan's durable receipt.

        Entity names or display names never establish ownership. The registry row
        must match the recorded stable storage/config-entry identifier or the
        independently read-back identity. Ambiguity remains unknown.
        """
        receipt=op.get('receipt')
        if not isinstance(receipt,dict):return None
        matches=[]
        saved=receipt.get('identity')
        if isinstance(saved,dict) and receipt.get('entity_id')==op.get('entity_id'):
            matches=[r for r in rows if r.get('entity_id')==op['entity_id'] and same_identity(saved,r)
                     and r.get('disabled_by') is None]
        elif op.get('domain')=='template' and isinstance(receipt.get('config_entry_id'),str) and receipt['config_entry_id']:
            matches=[r for r in rows if r.get('entity_id')==op['entity_id'] and r.get('platform')=='template'
                     and r.get('config_entry_id')==receipt['config_entry_id'] and r.get('unique_id')
                     and r.get('disabled_by') is None]
        elif isinstance(receipt.get('storage_id'),str) and receipt['storage_id']:
            matches=[r for r in rows if r.get('entity_id')==op['entity_id'] and r.get('platform')==op.get('domain')
                     and r.get('unique_id')==receipt['storage_id'] and r.get('disabled_by') is None]
        return matches[0] if len(matches)==1 else None

    async def _zone_invalidate_package(self,package):
        # Verify identity before touching a held output, including pause/stop.
        rows={r['entity_id']:r for r in await self.client.zone_output_registry()}
        eid=package['entities']['entscheidung_gueltig'];expected=package['identities']['entscheidung_gueltig']
        if not same_identity(expected,rows.get(eid,{})):raise SelectionConflict('Ausgangsidentität geändert')
        await self.client.zone_output_service('input_boolean','turn_off',eid)

    async def _zone_publish_all(self):
        if self._zone_io_lock.locked():return
        async with self._zone_io_lock:
            for zone in await self.zones.list():
                zid=zone['zone_id'];cfg=await self.context.get(zid);record=cfg.get(KEY) or {};package=record.get('package')
                if not package or record.get('mode')!='publish':continue
                stored=await self.context.zone_operational(zid)
                if stored.get('output_suspended'):
                    self._zone_last_published.pop(zid,None)
                    self._zone_views.setdefault(zid,{})['publication']='suspended_after_unknown_outcome'
                    continue
                try:
                    view=self._zone_views.get(zid,{});current=view.get('current')
                    await self._zone_publish(zid,record,view,current)
                except (HomeAssistantError,SelectionConflict,TimeoutError):
                    self._zone_last_published.pop(zid,None)
                    # HA I/O releases the projection lock: a newer source event may
                    # already have persisted a deadline. Never restore the old snapshot
                    # merely to add the output-failure marker.
                    async with self._projection_lock:
                        inv=await self.selection_inventory(zid)
                        stored=await self.context.zone_operational(zid)
                        await self.context.save_zone_operational(zid,inv['revision'],{**stored,'output_suspended':True})
                    self._zone_views.setdefault(zid,{})['publication']='unknown_or_conflict'
                    # One compensating invalidation, never a replay of the uncertain write.
                    try:await self._zone_invalidate_package(package)
                    except (HomeAssistantError,SelectionConflict,TimeoutError):pass
                    # A failed invalidation still expires through the bounded lease.

    async def _zone_assert_current_publication(self,zid,view,current):
        """Recheck after awaited I/O, without holding the projection lock over HA."""
        inv=await self.selection_inventory(zid)
        latest=self._zone_views.get(zid,{})
        newest=latest.get('current')
        now=time.time()
        if (inv['revision']!=view.get('revision') or not inv['enabled'] or
            latest.get('revision')!=view.get('revision') or latest.get('status')!='current' or
            not newest or newest.get('generation')!=current.get('generation') or
            not self._presence_inputs_fresh(now) or
            any(not candidate.get('valid') or not kernel.finite(candidate.get('observed_at')) or
                not 0<=now-candidate['observed_at']<=15 for candidate in (current,newest))):
            raise SelectionConflict('Präsenzgrundlage während Ausgabe geändert oder veraltet')

    async def _zone_publish(self,zid,record,view,current):
        package=record['package'];entities=package['entities'];now=time.time()
        last=self._zone_last_published.get(zid,{})
        valid=bool(current and current['valid'] and kernel.finite(current.get('observed_at')) and
                   0<=now-current['observed_at']<=15 and self._presence_inputs_fresh(now) and view.get('status')=='current')
        signature=(current.get('state'),current.get('deadline'),valid) if current else (None,None,False)
        if last.get('signature')==signature and now-last.get('at',0)<PUBLICATION_HEARTBEAT_SECONDS:return
        rows={r['entity_id']:r for r in await self.client.zone_output_registry()}
        for role,eid in entities.items():
            if not same_identity(package['identities'][role],rows.get(eid,{})) or rows[eid].get('disabled_by'):
                raise SelectionConflict('Zonen-Ausgang wurde verändert')
        inv=await self.selection_inventory(zid)
        if inv['revision']!=view.get('revision'):raise SelectionConflict('Zonenbasis vor Ausgabe geändert')
        if current and self._zone_views.get(zid,{}).get('current',{}).get('generation')!=current['generation']:
            raise SelectionConflict('Präsenzentscheidung inzwischen geändert')
        # Validity goes low before changing the held output; ordinary heartbeat renewal
        # does not pulse the public entity unavailable. No HA compare-and-swap exists.
        # Lease and validity go low before changing the held output. Invalid state never
        # produces owner.off. A fail anywhere leaves the public sensor unavailable.
        if not valid:
            await self.client.zone_output_service('input_boolean','turn_off',entities['entscheidung_gueltig'])
            self._zone_last_published[zid]={'signature':signature,'at':now};return
        await self._zone_assert_current_publication(zid,view,current)
        before_states=await self.client.zone_output_states()
        await self._zone_assert_current_publication(zid,view,current)
        desired='on' if current['occupied'] else 'off'
        if before_states.get(entities['anwesenheit_intern'],{}).get('state')!=desired:
            await self.client.zone_output_service('input_boolean','turn_off',entities['entscheidung_gueltig'])
            await self._zone_assert_current_publication(zid,view,current)
            await self.client.zone_output_service('input_boolean','turn_on' if current['occupied'] else 'turn_off',entities['anwesenheit_intern'])
            await self._zone_assert_current_publication(zid,view,current)
        deadline=current['deadline']
        if signature!=last.get('signature'):
            if deadline and deadline>now:
                await self.client.zone_output_service('timer','start',entities['nachlauf'],{'duration':max(1,min(86400,math.ceil(deadline-now)))})
            else:await self.client.zone_output_service('timer','cancel',entities['nachlauf'])
        states=await self.client.zone_output_states()
        if states.get(entities['anwesenheit_intern'],{}).get('state')!=('on' if current['occupied'] else 'off'):
            raise HomeAssistantError('Boolean-Ausgabe nicht bestätigt')
        await self._zone_assert_current_publication(zid,view,current)
        await self.client.zone_output_service('input_datetime','set_datetime',entities['gueltig_bis'],{'timestamp':now+90})
        await self._zone_assert_current_publication(zid,view,current)
        await self.client.zone_output_service('input_boolean','turn_on',entities['entscheidung_gueltig'])
        states=await self.client.zone_output_states()
        await self._zone_assert_current_publication(zid,view,current)
        if states.get(entities['entscheidung_gueltig'],{}).get('state')!='on':raise HomeAssistantError('Ausgabe-Gültigkeit nicht bestätigt')
        if states.get(entities['sensor'],{}).get('state')!=desired:
            # Allow an asynchronous template update to settle; only read is repeated.
            await asyncio.sleep(.15)
            states=await self.client.zone_output_states()
            await self._zone_assert_current_publication(zid,view,current)
            if states.get(entities['sensor'],{}).get('state')!=desired:
                raise HomeAssistantError('Öffentlicher Anwesenheitssensor nicht bestätigt')
        self._zone_last_published[zid]={'signature':signature,'at':now,
            'verified_at':time.time(),'revision':view['revision']}
        view['publication']='verified'

    async def ontology_catalog(self,zid):
        inv,cfg,zone,catalog=await self._organization_basis(zid)
        return {'zone_id':zid,'revision':inv['revision'],'zone_name':zone['name'],'catalog':catalog,
                'labels':await self.client.zone_labels(),'roles':list(ONTOLOGY_ROLES),
                'physical_locations_unchanged':True,'technical_id_execution':False}

    async def _zone_structure_shared_roles(self, zid, operations, labels):
        """HA role labels are global, even when entities belong to several zones."""
        from .core.zone_structure import KEY as STRUCTURE
        role_names = {row['label_id']: row['name'] for row in labels if row['name'] in ONTOLOGY_ROLES}
        profile = (await self.context.get(zid)).get(STRUCTURE, {})
        changes = {eid:set(member['roles']) for eid,member in profile.get('members', {}).items()}
        changes.update({op['entity_id']: {role_names[key] for key in (op.get('after') or op.get('metadata', {})).get('labels', []) if key in role_names}
                        for op in operations if 'entity_id' in op})
        for other in await self.zones.list():
            if other['zone_id'] == zid:
                continue
            members = (await self.context.get(other['zone_id'])).get(STRUCTURE, {}).get('members', {})
            for eid in set(members) & set(changes):
                if set(members[eid]['roles']) != changes[eid]:
                    raise SelectionConflict('Globale HA-Rollenlabels widersprechen einer weiteren Zone: ' + eid)

    async def _zone_structure_guard(self, zid, operations, expected_labels=None, planned_label=None):
        from .core.zone_structure import KEY as STRUCTURE, PENDING_LABEL
        profile = deepcopy((await self.context.get(zid)).get(STRUCTURE))
        if not profile:
            return []
        labels = await self.client.zone_labels()
        if profile['label_id'] is None:
            if not planned_label or planned_label['name'] != profile.get('label_name'):
                raise SelectionConflict('Zonenlabel ist noch nicht angelegt; Zonenlabels zuerst abgleichen')
            profile['label_id'] = planned_label['label_id']
            if planned_label['label_id'] == PENDING_LABEL:
                if any(row['name'].casefold() == planned_label['name'].casefold() for row in labels):
                    raise SelectionConflict('Labelname inzwischen vorhanden; Bestand ausdrücklich zuordnen')
                labels = [*labels, planned_label]
            elif not any(row['label_id']==planned_label['label_id'] and row['name']==planned_label['name'] for row in labels):
                raise SelectionConflict('Angelegtes Zonenlabel inzwischen geändert')
        names = {row['label_id']: row['name'] for row in labels}
        if profile['label_id'] not in names:
            raise SelectionConflict('Zonenlabel fehlt inzwischen')
        for key, name in (expected_labels or {}).items():
            if (name in ONTOLOGY_ROLES or key == profile['label_id']) and names.get(key) != name:
                raise SelectionConflict('Zonen- oder Rollenlabel seit der Vorschau geändert')
        await self._zone_structure_shared_roles(zid, operations, labels)
        rows = {row['entity_id']: row for row in await self.client.zone_output_registry()}
        devices = await self.client.zone_label_devices()
        projected = {eid: set(row.get('labels') or []) for eid, row in rows.items()}
        for op in operations:
            after = op.get('after') or op.get('metadata')
            if not after:
                continue
            if not set(after['labels']) <= set(names):
                # Existing unrelated labels may have been removed meanwhile too.
                # Never send a label ID that no longer exists.
                raise SelectionConflict('Ein benötigtes Label fehlt inzwischen')
            roles = {names[key] for key in after['labels'] if names[key] in ONTOLOGY_ROLES}
            if 'habitus_roles' in op and roles != set(op['habitus_roles']):
                raise SelectionConflict('Bedeutung der Helferrollen seit der Vorschau geändert')
            projected[op['entity_id']] = set(after['labels'])
            rows.setdefault(op['entity_id'], {'disabled_by': None})
        anchors = {key for key, name in names.items() if name == 'Habitus Zone'}
        zones = [(profile['label_id'], True)]
        for other in await self.zones.list():
            if other['zone_id'] != zid:
                label = (await self.context.get(other['zone_id'])).get(STRUCTURE, {}).get('label_id')
                if label:
                    zones.append((label, False))
        changed = {op['entity_id'] for op in operations if 'entity_id' in op}
        for label, own in zones:
            members = {eid for eid, values in projected.items() if label in values or label in devices.get(rows[eid].get('device_id'), [])}
            if not own and not members & changed:
                continue
            # Disabled anchors are still existing identities, not permission to replace them.
            if sum(bool(projected[eid] & anchors) for eid in members) > 1:
                raise SelectionConflict('Der Abgleich würde mehrere öffentliche Zonenanker hinterlassen')
        return labels

    async def structure_label_preview(self, zid, payload):
        from .core.zone_structure import KEY as STRUCTURE, PENDING_LABEL
        if not isinstance(payload, dict) or set(payload) != {'revision'}:
            raise InvalidSelection('Revision erforderlich')
        inv, cfg, _, _ = await self._organization_basis(zid, payload['revision'])
        profile = cfg.get(STRUCTURE)
        if not profile:
            raise InvalidSelection('Zuerst ein Zonenlabel und Mitglieder speichern')
        labels = await self.client.zone_labels()
        pending = profile['label_id'] is None
        label_id = PENDING_LABEL if pending else profile['label_id']
        planned_label = {'label_id': label_id, 'name':profile['label_name']} if pending else None
        if not pending and label_id not in {row['label_id'] for row in labels}:
            raise SelectionConflict('Das verbundene Zonenlabel fehlt inzwischen')
        by_name = {}
        for label in labels:
            by_name.setdefault(label['name'], []).append(label['label_id'])
        required_roles = {role for member in profile['members'].values() for role in member['roles']}
        if any(len(by_name.get(role, [])) != 1 for role in required_roles):
            raise SelectionConflict('Benötigte Habitus-Rollenlabels fehlen oder sind mehrdeutig')
        role_ids = {label for role in ONTOLOGY_ROLES for label in by_name.get(role, [])}
        rows = {row['entity_id']: row for row in await self.client.zone_output_registry()}
        operations = ([{'effect':'create_zone_label', 'name':profile['label_name']}] if pending else [])
        for eid, member in profile['members'].items():
            row = rows.get(eid, {})
            if not same_identity(member['identity'], row) or row.get('disabled_by') is not None:
                raise SelectionConflict('Mitglied fehlt, wurde ersetzt oder deaktiviert: ' + eid)
            before = {'name': row.get('name'), 'labels': sorted(row.get('labels') or [])}
            desired = sorted((set(before['labels']) - role_ids) | {label_id} |
                             {by_name[role][0] for role in member['roles']})
            after = {'name': before['name'], 'labels': desired}
            if before != after:
                operations.append({'entity_id': eid, 'identity': identity(row), 'before': before,
                                   'after': after, 'effect': 'zone_membership_and_roles'})
        await self._zone_structure_guard(zid, operations, planned_label=planned_label)
        await self._organization_basis(zid, inv['revision'])
        if not operations:
            return {'state': 'unchanged', 'operations': [], 'message': 'Zonenlabel und Rollen stimmen überein.'}
        return await self.plans.organization_plan_create(zid, inv['revision'], operations, kind='structure_labels',
            details={'scope': 'zone_labels_and_roles', 'label_id': profile['label_id'],
                     'label_names': {row['label_id']: row['name'] for row in [*labels, *([planned_label] if pending else [])]},
                     'creates_zone_label': pending,
                     'other_labels_preserved': True, 'physical_locations_unchanged': True,
                     'names_unchanged': True, 'control_enabled': False,
                     'limits': ['Label-basierte Automationen und Dashboards können auf den Abgleich reagieren.',
                                'Entfernte Mitglieder verlieren keine bestehenden HA-Labels; Entfernung gesondert prüfen.',
                                'Bei Teilfehlern bleiben bestätigte Schritte sichtbar; kein blindes Wiederholen.']})

    async def ontology_preview(self,zid,payload):
        if not isinstance(payload,dict) or set(payload)!={'revision','entity_id','name','zone_label','roles','target_entity_id'}:
            raise InvalidSelection('Vollständiger Ontologieauftrag erforderlich')
        inv,_,zone,catalog=await self._organization_basis(zid,payload['revision'])
        rows=await self.client.zone_output_registry();row=next((r for r in rows if r['entity_id']==payload['entity_id']),None)
        if not row or not row.get('unique_id') or row.get('disabled_by'):raise InvalidSelection('Aktive stabile Entität erforderlich')
        if payload['target_entity_id'] not in (None,'',row['entity_id']):
            # Technical rename is a migration across components, not a registry trick.
            return {'state':'migration_required','execution':False,'reason':'Entitäts-ID-Änderung benötigt vollständige Verbraucherprüfung einschließlich Templates, Dashboards und Integrationen.',
                    'current_entity_id':row['entity_id'],'requested_entity_id':payload['target_entity_id']}
        labels=await self.client.zone_labels()
        op=metadata_operation(row,labels,name=payload['name'],zone_label=payload['zone_label'],roles=payload['roles'])
        if 'Habitus Zone' in payload['roles']:
            item=next((r for r in catalog if r['entity_id']==row['entity_id']),{})
            if not row['entity_id'].startswith('binary_sensor.') or item.get('device_class') not in ('occupancy','presence'):
                raise InvalidSelection('Zonenanker muss ein semantischer Anwesenheits-Binärsensor sein')
            anchor_id=next(l['label_id'] for l in labels if l['name']=='Habitus Zone')
            collisions=[r['entity_id'] for r in rows if r['entity_id']!=row['entity_id'] and
                        anchor_id in (r.get('labels') or []) and payload['zone_label'] in (r.get('labels') or [])]
            if collisions:raise SelectionConflict('Zone besitzt bereits einen anderen semantischen Anker')
        return await self.plans.organization_plan_create(zid,inv['revision'],[op],kind='ontology',details={
            'scope':'display_name_and_role_labels','entity_ids_unchanged':True,'other_labels_preserved':True,
            'limits':['Name-/Label-basierte Automationen und Dashboards können auf diese Änderung reagieren.','HA besitzt keinen atomaren Compare-and-swap für Registermetadaten.']})

    @staticmethod
    def _zone_resolved_label_operations(plan):
        from .core.zone_structure import PENDING_LABEL
        created = next((op.get('receipt', {}).get('label') for op in plan['operations'] if op.get('effect')=='create_zone_label'), None)
        operations = []
        for index, raw in enumerate(plan['operations']):
            if raw.get('effect') == 'create_zone_label':
                continue
            op = deepcopy(raw)
            for side in ('before', 'after'):
                if PENDING_LABEL in op[side]['labels']:
                    if not created:
                        raise SelectionConflict('Anlagebeleg für das neue Zonenlabel fehlt')
                    op[side]['labels'] = sorted(created['label_id'] if key==PENDING_LABEL else key for key in op[side]['labels'])
            operations.append((index, op))
        return created, operations

    async def _zone_create_planned_label(self, zid, plan):
        """Creation receipt proves ownership; a matching name never does."""
        from .core.zone_structure import PENDING_LABEL
        op = plan['operations'][0]
        if op.get('outcome') == 'conflict':
            return plan
        try:
            await self._organization_basis(zid, plan['revision'])
            if op.get('outcome') == 'pending':
                before_labels = await self._zone_structure_guard(zid, plan['operations'], plan['details'].get('label_names'),
                    planned_label={'label_id':PENDING_LABEL, 'name':op['name']})
                rows = {row['entity_id']: row for row in await self.client.zone_output_registry()}
                for change in plan['operations'][1:]:
                    if not metadata_matches(rows.get(change['entity_id'], {}), change, 'before'):
                        raise SelectionConflict('Mitglied vor der Labelanlage geändert')
                await self.plans.organization_progress(zid, plan['id'], 0, 'sending')
                await self._organization_basis(zid, plan['revision'])
                # No label mutation is retried after sending without a receipt.
                created = await self.client.zone_create_label(op['name'])
                if (not isinstance(created, dict) or not isinstance(created.get('label_id'), str) or
                        not created['label_id'] or created['label_id'] in {row['label_id'] for row in before_labels} or
                        created.get('name') != op['name']):
                    raise HomeAssistantError('Labelanlage nicht identifizierbar')
                await self.plans.organization_receipt(zid, plan['id'], 0,
                    {'label': {'label_id':created['label_id'], 'name':created['name']}})
                plan = await self.plans.organization_plan_get(zid, plan['id'])
                op = plan['operations'][0]
            created = op.get('receipt', {}).get('label')
            if not created:
                return await self.plans.organization_progress(zid, plan['id'], 0, 'unknown')
            labels = await self.client.zone_labels()
            found = next((row for row in labels if row['label_id']==created['label_id']), None)
            if not found or found['name'] != created['name']:
                raise SelectionConflict('Angelegtes Label fehlt oder wurde manuell geändert')
            return await self.plans.organization_progress(zid, plan['id'], 0, 'verified', True)
        except SelectionConflict:
            return await self.plans.organization_progress(zid, plan['id'], 0, 'conflict')
        except (HomeAssistantError, TimeoutError):
            return await self.plans.organization_progress(zid, plan['id'], 0, 'unknown')

    async def ontology_apply(self,zid,plan_id,payload):
        if not isinstance(payload,dict) or set(payload)!={'sha256','confirm'} or payload['confirm'] is not True:
            raise InvalidSelection('Konkreten Metadatenplan bestätigen')
        async with self._automation_review_lock:
            plan=await self.plans.organization_plan_get(zid,plan_id)
            if plan['kind'] not in ('ontology','structure_labels'):raise InvalidSelection('Kein Metadatenplan')
            plan,claimed=await self.plans.organization_claim(zid,plan_id,payload['sha256'])
            creates_label = plan['operations'][0].get('effect') == 'create_zone_label'
            if not claimed and (not creates_label or plan.get('binding')):
                return {**plan,'write_repeated':False}
            if creates_label:
                plan = await self._zone_create_planned_label(zid, plan)
                if plan['operations'][0]['outcome'] != 'verified':
                    return plan
            created, indexed = self._zone_resolved_label_operations(plan)
            changes = [op for _, op in indexed]
            async def read(eid):
                if plan['kind']=='structure_labels':
                    return await self.client.zone_registry_entry(eid)
                return next((r for r in await self.client.zone_output_registry() if r['entity_id']==eid),{})
            guard_labels = None
            for offset, (index, op) in enumerate(indexed):
                try:
                    if offset == 0:
                        guard_labels = await self._zone_structure_guard(zid, changes, plan['details'].get('label_names'), created)
                    elif guard_labels:
                        await self._zone_structure_shared_roles(zid, [op], guard_labels)
                        anchor_ids = {row['label_id'] for row in guard_labels if row['name']=='Habitus Zone'}
                        if anchor_ids & set(op['after']['labels']):
                            await self._zone_structure_guard(zid, changes, plan['details'].get('label_names'), created)
                    await self._organization_basis(zid,plan['revision'])
                    row=await read(op['entity_id'])
                    if not claimed and op.get('outcome') != 'pending':
                        if op.get('outcome')=='conflict':return plan
                        # Read-only recovery. An uncertain write is never repeated.
                        outcome = 'verified' if metadata_matches(row,op,'after') else 'unknown'
                        plan = await self.plans.organization_progress(zid,plan_id,index,outcome)
                        if outcome!='verified':return plan
                        continue
                    if not metadata_matches(row,op,'before'):return await self.plans.organization_progress(zid,plan_id,index,'conflict')
                    await self.plans.organization_progress(zid,plan_id,index,'sending')
                    await self._organization_basis(zid,plan['revision'])
                    confirmed=True
                    try:await self.client.zone_set_metadata(op['entity_id'],**op['after'])
                    except HomeAssistantError:confirmed=False
                    row=await read(op['entity_id'])
                    outcome='verified' if metadata_matches(row,op,'after') else 'unknown'
                    plan=await self.plans.organization_progress(zid,plan_id,index,outcome,confirmed)
                    if outcome!='verified':return plan
                except SelectionConflict:return await self.plans.organization_progress(zid,plan_id,index,'conflict')
                except (HomeAssistantError,TimeoutError):return await self.plans.organization_progress(zid,plan_id,index,'unknown')
            try:
                final_rows = {row['entity_id']: row for row in await self.client.zone_output_registry()}
                for index, op in indexed:
                    if not metadata_matches(final_rows.get(op['entity_id'], {}), op, 'after'):
                        return await self.plans.organization_progress(zid, plan_id, index, 'conflict')
                await self._zone_structure_guard(zid, changes, plan['details'].get('label_names'), created)
                if creates_label:
                    plan = await self.zones.bind_created_label(zid, plan['revision'], plan_id)
            except SelectionConflict:
                return await self.plans.organization_progress(zid, plan_id, len(plan['operations'])-1, 'conflict')
            except (HomeAssistantError, TimeoutError):
                return await self.plans.organization_progress(zid, plan_id, len(plan['operations'])-1, 'unknown')
            return plan

    async def ontology_restore_preview(self,zid,plan_id,payload):
        if not isinstance(payload,dict) or set(payload)!={'revision'}:raise InvalidSelection('Revision erforderlich')
        await self._organization_basis(zid,payload['revision'])
        original=await self.plans.organization_plan_get(zid,plan_id)
        if original['kind'] not in ('ontology','structure_labels') or original['state']!='verified':
            raise InvalidSelection('Nur verifiziert abgeschlossene Metadatenpläne zurücknehmen')
        rows={r['entity_id']:r for r in await self.client.zone_output_registry()}
        operations=[]
        _, indexed = self._zone_resolved_label_operations(original)
        for _, op in indexed:
            if not metadata_matches(rows.get(op['entity_id'],{}),op,'after'):
                raise SelectionConflict('Metadaten inzwischen geändert; Rücknahme würde fremde Änderungen überschreiben')
            operations.append({**{k:v for k,v in op.items() if k not in ('outcome','write_response_confirmed')},
                               'before':op['after'],'after':op['before']})
        if not operations:
            return {'state':'unchanged', 'operations':[], 'message':'Nur das Label wurde angelegt. Keine automatische Löschung; mögliche Verbraucher zuerst prüfen.'}
        return await self.plans.organization_plan_create(zid,payload['revision'],operations,kind=original['kind'],
                    details={'restores':plan_id,'scope':'exact_previous_metadata',
                             'limits':['Das neu angelegte Zonenlabel bleibt bestehen; keine automatische Löschung.'] if original['details'].get('creates_zone_label') else []})
