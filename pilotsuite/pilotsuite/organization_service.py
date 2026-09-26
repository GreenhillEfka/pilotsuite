"""Existing-inventory organization use cases; no second learner or runtime owner."""
from __future__ import annotations
import asyncio
from copy import deepcopy
from .core.organization import (ROLES, HELPER_PLATFORMS, ENTITY, binding_view, bind_request,
    analyze, repair_preview, naming_proposals, same_identity, identity, fingerprint)
from .core.selections import InvalidSelection, SelectionConflict
from .ha.client import HomeAssistantError


def validate_payload(payload,keys):
    if not isinstance(payload,dict) or set(payload)!=set(keys):
        raise InvalidSelection('Unbekannte Felder oder unvollständiger Auftrag')
    if 'revision' in keys and (type(payload['revision']) is not int or payload['revision']<0):
        raise InvalidSelection('Gültige Zonenrevision erforderlich')


def registry_matches(row,operation,expected):
    return (same_identity(operation['identity'],row)
            and row.get('entity_id')==operation['entity_id']
            and row.get('disabled_by') is None and row.get('name')==expected)


class OrganizationServiceMixin:
    async def _organization_basis(self,zone_id,revision=None):
        async with self._projection_lock:
            inventory=await self.selection_inventory(zone_id)
            if revision is not None and inventory['revision']!=revision:
                raise SelectionConflict('Zone geändert; Stand neu laden')
            config=await self.context.get(zone_id)
            zone=next((z for z in await self.zones.list() if z['zone_id']==zone_id),None)
            if not zone: raise InvalidSelection('Unbekannte Zone')
            catalog=await self.world.organization_catalog()
            return inventory,config,zone,catalog

    async def _organization_shared(self, zone_id, entity_ids, catalog):
        shared = {}
        for zone in await self.zones.list():
            if zone['zone_id'] == zone_id: continue
            cfg = await self.context.get(zone['zone_id'])
            view = binding_view(cfg, catalog)
            for rows in view['assignments'].values():
                for row in rows:
                    if row.get('entity_id') in entity_ids:
                        shared.setdefault(row['entity_id'], set()).add(zone['zone_id'])
        return {eid: sorted(zones) for eid, zones in shared.items()}

    async def organization_overview(self,zone_id):
        inv,cfg,zone,catalog=await self._organization_basis(zone_id)
        # Inventory dropdowns include unassigned-area and out-of-zone helpers explicitly.
        domains={d for _,ds,_ in ROLES.values() for d in ds}
        eligible=[r for r in catalog if r['entity_id'].split('.')[0] in domains]
        if len(eligible)>10000:
            raise InvalidSelection('Bestandsgrenze überschritten; keine Teilmenge als vollständig ausgeben')
        naming=naming_proposals(zone,cfg,catalog)
        shared=await self._organization_shared(zone_id,{r['entity_id'] for r in naming},catalog)
        for row in naming:
            row['shared_zone_ids']=shared.get(row['entity_id'],[])
            if row['shared_zone_ids']: row['name_change_eligible']=False
        return {'schema':'pilotsuite-organization-v1','zone_id':zone_id,'revision':inv['revision'],
            'zone_name':zone['name'],'bindings':binding_view(cfg,catalog),'catalog':eligible,
            'roles':{key:{'label':v[0],'domains':list(v[1]),'max':v[2]} for key,v in ROLES.items()},
            'naming':naming,'plans':await self.plans.organization_plans(zone_id),
            'fresh':(await self.status())['ready'], 'scope':'global_registry_and_state_snapshot',
            'learning_changed':False,'control_enabled':False}

    async def organization_save(self,zone_id,payload):
        validate_payload(payload,('revision','timing','assignments','confirm'))
        async with self._automation_review_lock:
            async with self._projection_lock:
                inv=await self.selection_inventory(zone_id)
                if inv['revision']!=payload['revision']: raise SelectionConflict('Zone geändert; neu laden')
                catalog=await self.world.organization_catalog()
                cfg=await self.context.get(zone_id)
                profile=bind_request(payload,catalog,cfg)
                result=await self.context.save_organization(zone_id,payload['revision'],profile)
                await self._derive()
        return {**result,'zone_id':zone_id,'saved':True,'learning_changed':False,'control_enabled':False}

    async def organization_analyze(self,zone_id,payload):
        validate_payload(payload,('revision','automation_ids'))
        ids=payload['automation_ids']
        if (not isinstance(ids,list) or not 1<=len(ids)<=8 or len(set(x for x in ids if isinstance(x,str)))!=len(ids)
                or any(not isinstance(e,str) or len(e)>255 or not ENTITY.fullmatch(e) or not e.startswith('automation.') for e in ids)):
            raise InvalidSelection('Eine bis acht unterschiedliche Bestandsautomationen auswählen')
        if self._automation_review_lock.locked(): raise HomeAssistantError('Bestandsprüfung läuft bereits')
        async with self._automation_review_lock:
            inv,cfg,zone,catalog=await self._organization_basis(zone_id,payload['revision'])
            known={r['entity_id'] for r in catalog if r['entity_id'].startswith('automation.')}
            if not set(ids)<=known: raise InvalidSelection('Automation fehlt im aktuellen Bestand')
            reports=[];unread=[]
            async with asyncio.timeout(90):
                for eid in ids:
                    try:
                        raw=await self.client.automation_config(eid)
                        reports.append(analyze(eid,raw,catalog,zone['area_ids'],(await self.status())['ready']))
                    except (HomeAssistantError,InvalidSelection) as exc:
                        unread.append({'automation_id':eid,'reason':'configuration_unreadable' if isinstance(exc,HomeAssistantError) else 'structural_analysis_limit'})
            _,_,_,after=await self._organization_basis(zone_id,payload['revision'])
            # Registry identity changes invalidate recommendations; live state changes alone do not.
            if fingerprint([identity(r) for r in after])!=fingerprint([identity(r) for r in catalog]):
                raise SelectionConflict('Entitätsregister während der Analyse geändert; erneut prüfen')
            return {'zone_id':zone_id,'revision':inv['revision'],'reports':reports,'unread':unread,
                'complete':not unread,'coverage':'selected_automations_only','execution':{'allowed':False}}

    async def organization_repair_preview(self,zone_id,payload):
        validate_payload(payload,('revision','automation_id','fingerprint','replacements'))
        eid=payload['automation_id']
        if not isinstance(eid,str) or not ENTITY.fullmatch(eid) or not eid.startswith('automation.') or len(eid)>255:
            raise InvalidSelection('Ungültige Automation')
        async with self._automation_review_lock:
            _,_,_,catalog=await self._organization_basis(zone_id,payload['revision'])
            raw=await self.client.automation_config(eid)
            report=repair_preview(eid,raw,payload['fingerprint'],payload['replacements'],catalog)
            await self._organization_basis(zone_id,payload['revision'])
            return await self.plans.organization_plan_create(zone_id,payload['revision'],report['edits'],
                kind='repair_review',details={k:v for k,v in report.items() if k!='edits'})

    async def organization_name_preview(self,zone_id,payload):
        validate_payload(payload,('revision','roles'))
        selected=payload['roles']
        if not isinstance(selected,list) or not 1<=len(selected)<=5 or any(not isinstance(x,str) or x not in ROLES for x in selected):
            raise InvalidSelection('Eine bis fünf Helferfunktionen für die Namensbereinigung wählen')
        if self._automation_review_lock.locked(): raise HomeAssistantError('Bestandsprüfung läuft bereits')
        async with self._automation_review_lock:
            _,cfg,zone,catalog=await self._organization_basis(zone_id,payload['revision'])
            suggestions=[r for r in naming_proposals(zone,cfg,catalog) if r['role'] in selected]
            if len(suggestions)!=len(set(selected)) or not all(r['name_change_eligible'] for r in suggestions):
                raise InvalidSelection('Jede Funktion muss einem aktiven identifizierbaren Helfer zugeordnet sein')
            if len({r['entity_id'] for r in suggestions})!=len(suggestions):
                raise InvalidSelection('Ein Helfer ist mehrfach mit verschiedenen Funktionen belegt; zuerst auflösen')
            if await self._organization_shared(zone_id,{r['entity_id'] for r in suggestions},catalog):
                raise SelectionConflict('Helfer wird mehreren Zonen zugeordnet; gemeinsamen Namensraum zuerst klären')
            operations=[]
            for suggestion in suggestions:
                row=await self.client.organization_registry(suggestion['entity_id'])
                saved=next(r for r in catalog if r['entity_id']==suggestion['entity_id'])
                if (not same_identity(saved,row) or row.get('disabled_by') is not None
                        or row.get('platform') not in HELPER_PLATFORMS):
                    raise SelectionConflict('Helferidentität geändert oder nicht bestätigbar')
                if row.get('name') is not None and (not isinstance(row['name'],str) or len(row['name'])>255):
                    raise InvalidSelection('Vorheriger Name nicht sicher wiederherstellbar')
                desired=suggestion['proposed_name']
                if len(desired)>120: raise InvalidSelection('Zonenname für einheitliche Helfernamen zu lang')
                if row.get('name')==desired: continue
                operations.append({'entity_id':row['entity_id'],'identity':identity(row),'role':suggestion['role'],
                    'before':row.get('name'),'after':desired,'effect':'registry_display_name_only'})
            if not operations:
                return {'state':'unchanged','operations':[],'message':'Anzeigenamen entsprechen bereits dem Schema.'}
            await self._organization_basis(zone_id,payload['revision'])
            return await self.plans.organization_plan_create(zone_id,payload['revision'],operations,
                details={'atomic':False,'scope':'display_names_only','entity_ids_unchanged':True,
                    'limits':['name_based_templates_and_voice_assistants_may_be_affected','ha_registry_has_no_compare_and_swap']})

    async def organization_name_apply(self,zone_id,plan_id,payload):
        validate_payload(payload,('sha256','confirm'))
        if payload['confirm'] is not True: raise InvalidSelection('Ausdrückliche Planbestätigung erforderlich')
        if self._automation_review_lock.locked(): raise HomeAssistantError('Bestandsänderung läuft bereits')
        async with self._automation_review_lock:
            plan,claimed=await self.plans.organization_claim(zone_id,plan_id,payload['sha256'])
            if not claimed: return {**plan,'replayed':True,'write_repeated':False}
            for index,op in enumerate(plan['operations']):
                try:
                    await self._organization_basis(zone_id,plan['revision'])
                    current=await self.client.organization_registry(op['entity_id'])
                    if not registry_matches(current,op,op['before']):
                        return await self.plans.organization_progress(zone_id,plan_id,index,'conflict')
                    _,_,_,catalog=await self._organization_basis(zone_id,plan['revision'])
                    if await self._organization_shared(zone_id,{op['entity_id']},catalog):
                        return await self.plans.organization_progress(zone_id,plan_id,index,'conflict')
                    # Durable before-image and sending marker precede every side effect.
                    await self.plans.organization_progress(zone_id,plan_id,index,'sending')
                    confirmed=True
                    try:
                        await self.client.organization_set_name(op['entity_id'],op['after'])
                    except HomeAssistantError:
                        confirmed=False
                    readback=await self.client.organization_registry(op['entity_id'])
                    outcome='verified' if registry_matches(readback,op,op['after']) else 'unknown'
                    plan=await self.plans.organization_progress(zone_id,plan_id,index,outcome,confirmed)
                    if outcome!='verified': return plan
                except SelectionConflict:
                    return await self.plans.organization_progress(zone_id,plan_id,index,'conflict')
                except (HomeAssistantError,TimeoutError):
                    return await self.plans.organization_progress(zone_id,plan_id,index,'unknown')
            return plan

    async def organization_name_restore_preview(self,zone_id,plan_id,payload):
        validate_payload(payload,('revision',))
        async with self._automation_review_lock:
            await self._organization_basis(zone_id,payload['revision'])
            previous=await self.plans.organization_plan_get(zone_id,plan_id)
            if previous['kind'] not in ('names','restore_names'):
                raise InvalidSelection('Kein Namensänderungsplan')
            operations=[]
            for op in previous['operations']:
                if op.get('outcome')!='verified' or not op.get('write_response_confirmed'):
                    continue  # Unknown origin is not proof that we may undo someone else's edit.
                row=await self.client.organization_registry(op['entity_id'])
                if not registry_matches(row,op,op['after']):
                    raise SelectionConflict('Name oder Identität seither geändert; keine automatische Rücknahme')
                operations.append({k:deepcopy(v) for k,v in op.items() if k not in ('outcome','write_response_confirmed')} |
                                  {'before':op['after'],'after':op['before']})
            if not operations: raise InvalidSelection('Keine sicher zuordenbare Änderung für eine Rücknahme')
            await self._organization_basis(zone_id,payload['revision'])
            return await self.plans.organization_plan_create(zone_id,payload['revision'],operations,kind='restore_names',
                details={'previous_plan':plan_id,'atomic':False,'scope':'display_names_only'})
