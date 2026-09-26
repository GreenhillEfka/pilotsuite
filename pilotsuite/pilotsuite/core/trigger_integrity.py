"""Bounded trigger-ID cross references, not a control-flow or safety proof.

Only structural paths/counts leave this module; authored IDs and payloads do not.
HA owns execution. Manual automation.trigger calls may supply different context.
"""
from .selections import InvalidSelection


def inspect_trigger_integrity(config):
    pending = [(config, 0)]; nodes = 0
    while pending:
        value, depth = pending.pop(); nodes += 1
        if depth > 18 or nodes > 5000:
            raise InvalidSelection('Automation überschreitet die Analysegrenze')
        if isinstance(value, dict): pending.extend((v, depth+1) for v in value.values())
        elif isinstance(value, list): pending.extend((v, depth+1) for v in value)
    if not isinstance(config, dict):
        raise InvalidSelection('Automation muss ein Objekt sein')
    limitations = set(); declarations = []; selectors = []; complete = True

    def identifier(value):
        if type(value) is int: return str(value)
        if isinstance(value, str) and len(value) <= 512 and not any(x in value for x in ('{{', '{%', '{#')):
            return value
        return None

    def enabled(value, parent=True):
        own = value.get('enabled', True)
        if parent is False or own is False: return False
        if parent is None or type(own) is not bool:
            limitations.add('dynamic_enablement'); return None
        return True

    for plural, singular in (('triggers', 'trigger'), ('conditions', 'condition'), ('actions', 'action')):
        if plural in config and singular in config:
            limitations.add('ambiguous_section_aliases')
            if plural == 'triggers': complete = False
    key = 'triggers' if 'triggers' in config else 'trigger'
    triggers = config.get(key, [])
    if isinstance(triggers, dict): triggers = [triggers]; single = True
    else: single = False
    if not isinstance(triggers, list):
        triggers = []; complete = False; limitations.add('unsupported_trigger_catalogue')
    if 'use_blueprint' in config:
        complete = False; limitations.add('blueprint_not_expanded')
    for i, trigger in enumerate(triggers):
        path = '/' + key + ('' if single else '/' + str(i))
        if (not isinstance(trigger, dict) or 'triggers' in trigger or
            not isinstance(trigger.get('trigger', trigger.get('platform')), str)):
            complete = False; limitations.add('unsupported_trigger_catalogue'); continue
        name = identifier(trigger['id']) if 'id' in trigger else str(i)
        if name is None:
            complete = False; limitations.add('dynamic_or_invalid_trigger_id')
        declarations.append({'id': name, 'path': path, 'enabled': enabled(trigger)})

    def walk(value, path, parent=True):
        if isinstance(value, list):
            for i, item in enumerate(value): walk(item, path+'/'+str(i), parent)
            return
        if not isinstance(value, dict):
            limitations.add('unresolved_condition_structure'); return
        active = enabled(value, parent)
        if value.get('condition') == 'trigger':
            raw = value.get('id'); raw = raw if isinstance(raw, list) else [raw]
            ids = [identifier(v) for v in raw]
            selectors.append({'path': path, 'enabled': active, 'ids': ids,
                              'valid': bool(ids) and all(v is not None for v in ids)})
        if value.get('condition') == 'template': limitations.add('template_control_flow_not_evaluated')
        # Never descend into data, event payloads, variables, aliases or wait triggers.
        for key in ('conditions', 'if', 'then', 'else', 'sequence', 'default', 'parallel'):
            if key in value: walk(value[key], path+'/'+key, active)
        if 'choose' in value:
            choices = value['choose']
            if isinstance(choices, list):
                for i, choice in enumerate(choices): walk(choice, path+'/choose/'+str(i), active)
            else: limitations.add('unresolved_condition_structure')
        if 'repeat' in value:
            repeat = value['repeat']
            if isinstance(repeat, dict):
                for key in ('while', 'until', 'sequence'):
                    if key in repeat: walk(repeat[key], path+'/repeat/'+key, active)
            else: limitations.add('unresolved_condition_structure')
        # HA also accepts shorthand boolean conditions.
        for key in ('and', 'or', 'not'):
            if key in value: walk(value[key], path+'/'+key, active)
    for plural, singular in (('conditions', 'condition'), ('actions', 'action')):
        key = plural if plural in config else singular
        walk(config.get(key, []), '/'+key)

    rows = []; referenced = set()
    for selector in selectors:
        ids = set(v for v in selector['ids'] if v is not None)
        matches = [d for d in declarations if d['id'] in ids]
        known = {d['id'] for d in matches}
        missing = len(ids-known) if complete and selector['valid'] else None
        if selector['enabled'] is False: state = 'inactive'
        elif not selector['valid'] or not complete or selector['enabled'] is None: state = 'unknown'
        elif not matches: state = 'missing'
        elif missing: state = 'partial_match'
        elif any(d['enabled'] is True for d in matches): state = 'matched'
        elif any(d['enabled'] is None for d in matches): state = 'unknown'
        else: state = 'disabled_only'
        if selector['enabled'] is not False: referenced.update(ids)
        if not selector['valid']: limitations.add('dynamic_or_invalid_selector')
        rows.append({'path': selector['path'], 'state': state,
                     'requested_count': len(ids), 'missing_count': missing,
                     'matching_trigger_paths': [d['path'] for d in matches]})
    return {'schema': 'pilotsuite-trigger-integrity-v1', 'catalogue_complete': complete,
            'trigger_count': len(declarations), 'selectors': rows,
            'not_referenced_by_id': [d['path'] for d in declarations
                if d['enabled'] is True and d['id'] is not None and d['id'] not in referenced],
            'limitations': sorted(limitations), 'coverage': 'static_trigger_ids_only',
            'execution': {'allowed': False, 'actions': []}}
