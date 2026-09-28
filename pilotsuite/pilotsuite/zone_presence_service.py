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
from .core.selections import InvalidSelection,SelectionConflict
from .ha.client import HomeAssistantError

LOG=logging.getLogger(__name__)

class ZonePresenceServiceMixin:
    def _zone_presence_init(self):
        self._zone_views={};self._zone_traces={};self._zone_cache={};self._zone_io_lock=asyncio.Lock()
        self._zone_backoff={};self._zone_last_published={}

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
            if not (current and cached.get('revision')==inv['revision'] and self._shadow_fresh(now) and
                    kernel.finite(current.get('observed_at')) and 0<=now-current['observed_at']<=15): current=None
            labels=[] # fetched on explicit ontology edit, not on every display poll
            return {'schema':kernel.SCHEMA,'zone_id':zid,'revision':inv['revision'],
                    'analysis_policy':'relevant_means_live_and_available_history','analysis_enabled':bool(inv['enabled']),
                    'spec':spec,'mode':config.get('mode','compare'),'package':config.get('package'),
                    'catalog':[r for r in catalog if r['entity_id'] in relevant],
                    'current':current,'status':cached.get('status','waiting'),
                    'publication':cached.get('publication','not_published'),
                    'trace':list(self._zone_traces.get(zid,[]))[-128:] if current else [],
                    'trace_basis':'session_only_not_recorded_history',
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
                previous=cfg.get(KEY) or {};package=previous.get('package')
                if payload['mode']=='publish' and not package:
                    raise InvalidSelection('Zuerst ein geprüftes eigenes Ausgangspaket bereitstellen')
                # Existing output packages may have acquired external consumers. This
                # does not entitle the runtime to disable or rewrite those consumers.
                record={'schema':kernel.SCHEMA,'spec':spec,'mode':payload['mode'],'session':uuid.uuid4().hex,
                        'basis':kernel.source_basis(spec,catalog),'package':package}
                await self.context.save_zone_presence(zid,inv['revision'],record)
                self._zone_views.pop(zid,None);self._zone_last_published.pop(zid,None)
                await self._zone_presence_tick_locked()
            if package:
                await self._zone_invalidate_package(package)
        return await self.zone_presence_view(zid)

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
                basis=kernel.source_basis(spec,catalog);state=await self.context.zone_operational(zid)
                if record and record.get('basis')!=basis or state.get('suspended'):
                    await self.context.save_zone_operational(zid,inv['revision'],{**state,'suspended':'source_basis_changed'})
                    self._zone_views[zid]={'revision':inv['revision'],'status':'source_basis_changed','current':None};continue
                # Revision alone (e.g. changed title) never silently rebinds sources. The
                # semantic basis above protects identity and typed source settings.
                scope=await self.world.scope((),tuple(relevant))
                observations={r['entity_id']:r['state'] for r in scope['entities']}
                now=time.time(); checkpoint,view=kernel.evaluate(spec,state.get('checkpoint'),observations,
                    now=now,fresh=self._shadow_fresh(now),event=event)
                by_id={r['entity_id']:r for r in catalog}
                for row in view['sources']:row['name']=by_id.get(row['entity_id'],{}).get('name',row['entity_id'])
                old=self._zone_views.get(zid,{}).get('current')
                if not old or (old['state'],old['reason'],old['deadline'])!=(view['state'],view['reason'],view['deadline']):
                    self._zone_traces.setdefault(zid,[]).append({k:view[k] for k in ('state','reason','deadline','observed_at')})
                    self._zone_traces[zid]=self._zone_traces[zid][-128:]
                await self.context.save_zone_operational(zid,inv['revision'],{**state,'basis':basis,'checkpoint':checkpoint,
                        'session':record.get('session'),'suspended':None})
                self._zone_views[zid]={'revision':inv['revision'],'basis':basis,'current':view,'status':'current'}
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
        if not self._shadow_fresh(time.time()) or self._history_lock.locked():return
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
        return await self.plans.organization_plan_create(zid,inv['revision'],operations,kind='presence_package',
            details={'no_existing_automation_takeover':True,'previously_existing_outputs_untouched':True,
                     'grace_seconds':record['spec']['grace_seconds'],'lease_seconds':90,'availability_resolution_seconds':60})

    async def zone_package_apply(self,zid,plan_id,payload):
        if not isinstance(payload,dict) or set(payload)!={'sha256','confirm'} or payload['confirm'] is not True:
            raise InvalidSelection('Konkreten Ausgangsplan bestätigen')
        async with self._zone_io_lock:
            plan=await self.plans.organization_plan_get(zid,plan_id)
            if plan['kind']!='presence_package':raise InvalidSelection('Kein Zonen-Ausgangsplan')
            plan,claimed=await self.plans.organization_claim(zid,plan_id,payload['sha256'])
            if not claimed:
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
                    if len(matches)!=1 or not matches[0].get('unique_id'):raise HomeAssistantError('Unabhängiges Identitäts-Readback fehlgeschlagen')
                    row=matches[0];identities[op['role']]=identity(row);entities[op['role']]=row['entity_id']
                    await self.plans.organization_receipt(zid,plan_id,index,{'identity':identity(row),'entity_id':row['entity_id']})
                    if op['domain']=='template':
                        await self.client.zone_set_metadata(row['entity_id'],name=op['name'],labels=row.get('labels') or [])
                        named=next((r for r in await self.client.zone_output_registry() if r['entity_id']==row['entity_id']),{})
                        if not same_identity(row,named) or named.get('name')!=op['name']:
                            raise HomeAssistantError('Neuer Sensor-Anzeigename nicht unabhängig bestätigt')
                    await self.plans.organization_progress(zid,plan_id,index,'verified',True)
                except SelectionConflict:return await self.plans.organization_progress(zid,plan_id,index,'conflict')
                except (HomeAssistantError,TimeoutError):return await self.plans.organization_progress(zid,plan_id,index,'unknown')
            latest={r['entity_id']:r for r in await self.client.zone_output_registry()}
            if len(entities)!=len(plan['operations']) or any(
                not same_identity(identities[role],latest.get(eid,{})) or
                latest[eid].get('disabled_by') is not None for role,eid in entities.items()):
                raise SelectionConflict('Ausgangsidentität vor Bindung geändert')
            async with self._projection_lock:
                inv,cfg,catalog,relevant=await self._zone_basis(zid)
                if inv['revision']!=plan['revision']:
                    return await self.plans.organization_progress(zid,plan_id,len(plan['operations'])-1,'conflict')
                config=deepcopy(cfg[KEY]);config['package']={'plan_id':plan_id,'entities':entities,'identities':identities}
                config['mode']='compare' # Creation never turns on presence/control.
                await self.context.save_zone_presence(zid,inv['revision'],config)
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
                    self._zone_views.setdefault(zid,{})['publication']='suspended_after_unknown_outcome'
                    continue
                try:
                    view=self._zone_views.get(zid,{});current=view.get('current')
                    await self._zone_publish(zid,record,view,current)
                except (HomeAssistantError,SelectionConflict,TimeoutError):
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
            not self._shadow_fresh(now) or
            any(not candidate.get('valid') or not kernel.finite(candidate.get('observed_at')) or
                not 0<=now-candidate['observed_at']<=15 for candidate in (current,newest))):
            raise SelectionConflict('Präsenzgrundlage während Ausgabe geändert oder veraltet')

    async def _zone_publish(self,zid,record,view,current):
        package=record['package'];entities=package['entities'];now=time.time()
        last=self._zone_last_published.get(zid,{})
        valid=bool(current and current['valid'] and kernel.finite(current.get('observed_at')) and
                   0<=now-current['observed_at']<=15 and self._shadow_fresh(now) and view.get('status')=='current')
        signature=(current.get('state'),current.get('deadline'),valid) if current else (None,None,False)
        if last.get('signature')==signature and now-last.get('at',0)<20:return
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
        self._zone_last_published[zid]={'signature':signature,'at':now};view['publication']='verified'

    async def ontology_catalog(self,zid):
        inv,cfg,zone,catalog=await self._organization_basis(zid)
        return {'zone_id':zid,'revision':inv['revision'],'zone_name':zone['name'],'catalog':catalog,
                'labels':await self.client.zone_labels(),'roles':list(ONTOLOGY_ROLES),
                'physical_locations_unchanged':True,'technical_id_execution':False}

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

    async def ontology_apply(self,zid,plan_id,payload):
        if not isinstance(payload,dict) or set(payload)!={'sha256','confirm'} or payload['confirm'] is not True:
            raise InvalidSelection('Konkreten Metadatenplan bestätigen')
        async with self._automation_review_lock:
            plan=await self.plans.organization_plan_get(zid,plan_id)
            if plan['kind']!='ontology':raise InvalidSelection('Kein Ontologieplan')
            plan,claimed=await self.plans.organization_claim(zid,plan_id,payload['sha256'])
            if not claimed:return {**plan,'write_repeated':False}
            op=plan['operations'][0]
            try:
                await self._organization_basis(zid,plan['revision'])
                row=next((r for r in await self.client.zone_output_registry() if r['entity_id']==op['entity_id']),{})
                if not metadata_matches(row,op,'before'):return await self.plans.organization_progress(zid,plan_id,0,'conflict')
                await self.plans.organization_progress(zid,plan_id,0,'sending')
                confirmed=True
                try:await self.client.zone_set_metadata(op['entity_id'],**op['after'])
                except HomeAssistantError:confirmed=False
                row=next((r for r in await self.client.zone_output_registry() if r['entity_id']==op['entity_id']),{})
                return await self.plans.organization_progress(zid,plan_id,0,'verified' if metadata_matches(row,op,'after') else 'unknown',confirmed)
            except SelectionConflict:return await self.plans.organization_progress(zid,plan_id,0,'conflict')
            except (HomeAssistantError,TimeoutError):return await self.plans.organization_progress(zid,plan_id,0,'unknown')

    async def ontology_restore_preview(self,zid,plan_id,payload):
        if not isinstance(payload,dict) or set(payload)!={'revision'}:raise InvalidSelection('Revision erforderlich')
        await self._organization_basis(zid,payload['revision'])
        original=await self.plans.organization_plan_get(zid,plan_id)
        if original['kind']!='ontology' or original['state']!='verified':
            raise InvalidSelection('Nur verifiziert abgeschlossene Metadatenpläne zurücknehmen')
        rows={r['entity_id']:r for r in await self.client.zone_output_registry()}
        operations=[]
        for op in original['operations']:
            if not metadata_matches(rows.get(op['entity_id'],{}),op,'after'):
                raise SelectionConflict('Metadaten inzwischen geändert; Rücknahme würde fremde Änderungen überschreiben')
            operations.append({**{k:v for k,v in op.items() if k not in ('outcome','write_response_confirmed')},
                               'before':op['after'],'after':op['before']})
        return await self.plans.organization_plan_create(zid,payload['revision'],operations,kind='ontology',
                    details={'restores':plan_id,'scope':'exact_previous_metadata'})
