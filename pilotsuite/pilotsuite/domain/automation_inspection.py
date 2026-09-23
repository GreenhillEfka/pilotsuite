"""Bounded structural review. Never evaluate templates or return raw HA config."""
import hashlib
import json
import re

from pilotsuite.ha.client import HomeAssistantError

TRIGGERS = {'state','numeric_state','time','time_pattern','sun','event','homeassistant',
            'zone','template','device','mqtt','calendar','webhook','tag','geo_location'}
CONDITIONS = {'state','numeric_state','time','sun','zone','template','device','trigger','and','or','not'}
FLOW = {'choose','if','repeat','parallel','sequence','delay','wait_template','wait_for_trigger',
        'event','variables','stop'}


def inspect_automation(config, draft, automation_id, previous_fingerprint=None):
    if not isinstance(config, dict): raise HomeAssistantError('Invalid automation configuration')
    # Validate work bounds before either hashing or walking nested structures.
    stack=[(config,0)]; nodes=0; has_template=False
    while stack:
        value,depth=stack.pop();nodes+=1
        if depth>16 or nodes>2000: raise HomeAssistantError('Automation complexity limit exceeded')
        if isinstance(value,dict): stack.extend((v,depth+1) for v in value.values())
        elif isinstance(value,list): stack.extend((v,depth+1) for v in value)
        elif isinstance(value,str): has_template |= any(s in value for s in ('{{','{%','{#'))
    try: encoded=json.dumps(config,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    except (ValueError,TypeError,RecursionError) as exc: raise HomeAssistantError('Invalid automation configuration') from exc
    if len(encoded)>120*1024: raise HomeAssistantError('Automation configuration too large')
    fingerprint=hashlib.sha256(encoded).hexdigest()
    sources=set(draft['current_pattern']['sources']);targets=set(draft['fields']['target_ids'])
    sections={key:[] for key in ('triggers','conditions','actions')};warnings=set()
    if has_template: warnings.add('templates_not_evaluated')
    if 'use_blueprint' in config: warnings.add('blueprint_not_expanded')

    def walk(value, section, path):
        if isinstance(value,list):
            for i,item in enumerate(value): walk(item,section,f'{path}[{i}]')
            return
        if not isinstance(value,dict):
            warnings.add('unsupported_structure');return
        if sum(map(len,sections.values()))>=200: raise HomeAssistantError('Automation step limit exceeded')
        refs=set();unknown=set()
        for obj in (value, value.get('target',{}), value.get('data',{})):
            if not isinstance(obj,dict): continue
            ids=obj.get('entity_id',[])
            if isinstance(ids,str): ids=ids.split(',')
            if isinstance(ids,list):
                for entity in ids:
                    if isinstance(entity,str) and re.fullmatch(r'[a-z_]+\.[a-z0-9_]+',entity.strip()): refs.add(entity.strip())
                    else: unknown.add('dynamic_or_invalid_entity_reference')
            else: unknown.add('dynamic_or_invalid_entity_reference')
            if any(k in obj for k in ('device_id','area_id','label_id','floor_id')): unknown.add('indirect_target_not_resolved')
        service=None
        if section=='triggers':
            kind=value.get('trigger',value.get('platform'))
            kind=kind if isinstance(kind,str) and kind in TRIGGERS else 'unsupported'
        elif section=='conditions' or 'condition' in value:
            kind=value.get('condition');kind=kind if isinstance(kind,str) and kind in CONDITIONS else 'unsupported'
        else:
            call=value.get('action',value.get('service'))
            if isinstance(call,str) and re.fullmatch(r'[a-z_]+\.[a-z0-9_]+',call):
                kind='service_call';service=call
                if call.startswith(('script.','scene.','automation.')): unknown.add('indirect_call_not_expanded')
                # A direct script service name can itself identify an unrelated entity.
                if call.startswith('script.'): service='script.*'
            else: kind=next((k for k in sorted(FLOW) if k in value),'unsupported')
        if kind=='unsupported': unknown.add('unsupported_step')
        if value.get('enabled') is False: unknown.add('disabled_step')
        if isinstance(value.get('enabled'),str): unknown.add('dynamic_enablement')
        entry={'path':path,'kind':kind,'service':service,
               'source_references':sorted(refs & sources),'target_references':sorted(refs & targets),
               'other_reference_count':len(refs-sources-targets),'limitations':sorted(unknown)}
        sections[section].append(entry);warnings.update(unknown)
        # Only known structural fields are traversed; data/payload/alias values never escape.
        for key,child_section in [('conditions','conditions'),('condition','conditions'),('if','conditions'),
                                  ('then','actions'),('else','actions'),('sequence','actions'),
                                  ('default','actions'),('parallel','actions'),('wait_for_trigger','triggers')]:
            child=value.get(key)
            if isinstance(child,(list,dict)): walk(child,child_section,path+'.'+key)
            elif key in value and key != 'condition': warnings.add('unsupported_structure')
        if 'choose' in value:
            branches=value['choose']
            if isinstance(branches,list):
                for i,branch in enumerate(branches):
                    if not isinstance(branch,dict): warnings.add('unsupported_structure');continue
                    for k,s in [('conditions','conditions'),('sequence','actions')]:
                        if k in branch: walk(branch[k],s,f'{path}.choose[{i}].{k}')
            else: warnings.add('unsupported_structure')
        repeat=value.get('repeat')
        if isinstance(repeat,dict):
            for k,s in [('while','conditions'),('until','conditions'),('sequence','actions')]:
                if k in repeat: walk(repeat[k],s,path+'.repeat.'+k)
        elif 'repeat' in value: warnings.add('unsupported_structure')

    for plural,singular in [('triggers','trigger'),('conditions','condition'),('actions','action')]:
        if plural in config and singular in config: warnings.add('ambiguous_section_aliases')
        walk(config.get(plural,config.get(singular,[])),plural,plural)
    checklist=[{'id':key,'state':'open','reason':reason} for key,reason in [
        ('intent','Compare desired comfort goal with the existing behavior'),
        ('timing','Review trigger values, timing and conditions in Home Assistant'),
        ('manual_override','Verify manual control and exceptions; authored text is not proof'),
        ('enabled','Check live enabled state; configuration is not runtime state'),
        ('risk','Assess effects and recovery separately; no action approval')]]
    action_targets=sorted({e for step in sections['actions'] if step['kind']=='service_call' for e in step['target_references']})
    source_triggers=sorted({e for step in sections['triggers'] for e in step['source_references']})
    if targets-set(action_targets): checklist.insert(0,{'id':'target_gap','state':'open','reason':'Targets lack direct service-call references; indirect behavior may still exist'})
    if sources-set(source_triggers): checklist.insert(0,{'id':'source_gap','state':'open','reason':'Some pattern sources have no recognized direct trigger reference'})
    if warnings: checklist.insert(0,{'id':'unknowns','state':'open','reason':'Resolve unsupported, indirect or dynamic behavior'})
    return {'schema':'pilotsuite-automation-inspection-v1','entity_id':automation_id,
            'config_fingerprint':fingerprint,
            'change_status':'first_read' if previous_fingerprint is None else 'unchanged' if fingerprint==previous_fingerprint else 'changed',
            'sections':sections,'limitations':sorted(warnings),
            'alignment':{'source_trigger_references':source_triggers,'target_action_references':action_targets,
                         'sources_without_direct_trigger_reference':sorted(sources-set(source_triggers)),
                         'targets_without_direct_action_reference':sorted(targets-set(action_targets)),
                         'semantic_equivalence':'not_determined'},
            'checklist':checklist,'coverage':'structural_only','risk':'not_assessed',
            'execution':{'allowed':False,'actions':[]}}
