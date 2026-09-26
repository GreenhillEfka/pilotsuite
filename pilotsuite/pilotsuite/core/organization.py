"""Functional vocabulary, stable bindings and bounded structural inventory analysis.

These projections never evaluate templates, infer consent, or authorize control.
"""
from __future__ import annotations
import hashlib
import json
import re
from copy import deepcopy
from difflib import SequenceMatcher
from .selections import InvalidSelection

SCHEMA = 'pilotsuite-organization-v1'
ENTITY = re.compile(r'[a-z_]+\.[a-z0-9_]+')
ROLES = {
    'presence_sources': ('Präsenzquellen', ('binary_sensor', 'input_boolean'), 20),
    'presence_status': ('Raumstatus', ('input_boolean', 'binary_sensor'), 1),
    'presence_timer': ('Nachlauftimer', ('timer',), 1),
    'presence_duration': ('Nachlauf-Dauer', ('input_number', 'number'), 1),
    'manual_override': ('Manuelle Bedienung', ('input_boolean', 'binary_sensor'), 1),
    'automation_blocker': ('Automatiksperre', ('input_boolean', 'binary_sensor'), 1),
    'presence_automations': ('Zuständige Automationen', ('automation',), 20),
}
TIMINGS = ('observe', 'existing_for', 'timer', 'external')
HELPER_PLATFORMS = frozenset(('input_boolean', 'input_number', 'timer', 'input_select',
    'input_datetime', 'input_text', 'input_button', 'template', 'group', 'threshold', 'min_max'))
ROLE_SUFFIX = {'presence_status': 'anwesenheit', 'presence_timer': 'anwesenheit_nachlauf',
    'presence_duration': 'anwesenheit_nachlaufdauer', 'manual_override': 'manuelle_bedienung',
    'automation_blocker': 'automatik_sperre'}
# Only literal first arguments of known HA functions are recognized. No evaluation.
LITERAL = re.compile(r"(?<![\w.])(?:states|is_state|state_attr|is_state_attr|expand)\s*\(\s*(['\"])([a-z_]+\.[a-z0-9_]+)\1\s*(?=[,)])")
DOT_STATE = re.compile(r'(?<![\w.])states\.([a-z_]+\.[a-z0-9_]+)(?=\.|\b)')


def fingerprint(value):
    try:
        raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    except (ValueError, TypeError, RecursionError) as exc:
        raise InvalidSelection('Ungültige strukturierte Daten') from exc
    return hashlib.sha256(raw).hexdigest()


def empty():
    return {'schema': SCHEMA, 'timing': 'observe', 'assignments': {}}


def identity(row):
    return {'entity_id': row['entity_id'], 'platform': row.get('platform'), 'unique_id': row.get('unique_id')}


def same_identity(a, b):
    """The registry key is domain + platform + unique_id, never name alone."""
    return bool(a.get('unique_id') and a.get('platform') and
        a['entity_id'].split('.')[0] == b.get('entity_id', '').split('.')[0] and
        a['platform'] == b.get('platform') and a['unique_id'] == b.get('unique_id'))


def resolve(saved, catalog):
    exact = next((r for r in catalog if r['entity_id'] == saved['entity_id']), None)
    if saved.get('unique_id') and saved.get('platform'):
        matches = [r for r in catalog if same_identity(saved, r)]
        if len(matches) != 1:
            return {'saved_entity_id': saved['entity_id'], 'entity_id': None,
                    'status': 'identity_unresolved', 'name': saved['entity_id']}
        row = matches[0]
        status = 'renamed' if row['entity_id'] != saved['entity_id'] else 'bound'
    elif exact and not exact.get('unique_id'):
        row, status = exact, 'exact_id_only'
    else:
        return {'saved_entity_id': saved['entity_id'], 'entity_id': None,
                'status': 'identity_unresolved', 'name': saved['entity_id']}
    return {**deepcopy(row), 'saved_entity_id': saved['entity_id'], 'status': status}


def binding_view(config, catalog):
    cfg = config.get('organization', empty())
    return {'schema': SCHEMA, 'timing': cfg['timing'],
            'assignments': {k: [resolve(v, catalog) for v in values]
                            for k, values in cfg['assignments'].items()},
            'authority': 'mapping_only', 'learning_consent': False}


def validate_saved(value):
    if not isinstance(value, dict) or set(value) != {'schema', 'timing', 'assignments'} or value['schema'] != SCHEMA:
        raise InvalidSelection('Ungültiges Funktionsprofil')
    if value['timing'] not in TIMINGS or not isinstance(value['assignments'], dict) or not set(value['assignments']) <= set(ROLES):
        raise InvalidSelection('Unbekannte Funktion oder Nachlaufart')
    for role, rows in value['assignments'].items():
        if not isinstance(rows, list) or len(rows) > ROLES[role][2]:
            raise InvalidSelection('Zu viele Funktionsquellen')
        for row in rows:
            if (not isinstance(row, dict) or set(row) != {'entity_id', 'platform', 'unique_id'} or
                not isinstance(row['entity_id'], str) or len(row['entity_id']) > 255 or
                not ENTITY.fullmatch(row['entity_id']) or row['entity_id'].split('.')[0] not in ROLES[role][1] or
                any(v is not None and (not isinstance(v, str) or len(v) > 512) for v in (row['platform'], row['unique_id']))):
                raise InvalidSelection('Ungültige gespeicherte Identität')
    return value


def bind_request(payload, catalog, previous):
    if (not isinstance(payload, dict) or set(payload) != {'revision', 'timing', 'assignments', 'confirm'} or
        type(payload['revision']) is not int or payload['revision'] < 0 or payload['confirm'] is not True or
        payload['timing'] not in TIMINGS or not isinstance(payload['assignments'], dict) or
        not set(payload['assignments']) <= set(ROLES)):
        raise InvalidSelection('Revision, Funktionszuordnung, Nachlaufart und Bestätigung erforderlich')
    by_id = {r['entity_id']: r for r in catalog}
    old = previous.get('organization', empty())['assignments']
    assignments = {}
    for role, ids in payload['assignments'].items():
        if (not isinstance(ids, list) or len(ids) > ROLES[role][2] or
            any(not isinstance(e, str) or len(e) > 255 or not ENTITY.fullmatch(e) or e.split('.')[0] not in ROLES[role][1] for e in ids)):
            raise InvalidSelection('Entitätstyp oder Anzahl passt nicht zur Funktion: ' + role)
        rows = []
        for eid in sorted(set(ids)):
            item = by_id.get(eid)
            previous_row = next((x for x in old.get(role, []) if x['entity_id'] == eid), None)
            if previous_row:
                # Retaining a disappeared/replaced identity never adopts its replacement.
                rows.append(deepcopy(previous_row)); continue
            if not item or item.get('disabled') or not item.get('in_registry'):
                raise InvalidSelection('Neue Zuordnung ist nicht im aktiven Register vorhanden: ' + eid)
            rows.append(identity(item))
        assignments[role] = rows
    used = {v['entity_id'] for v in assignments.get('presence_status', [])}
    if used & {v['entity_id'] for v in assignments.get('presence_sources', [])}:
        raise InvalidSelection('Raumstatus darf nicht zugleich seine eigene unabhängige Präsenzquelle sein')
    if payload['timing'] == 'timer' and not assignments.get('presence_timer'):
        raise InvalidSelection('Nachlaufart Timer erfordert einen ausgewählten vorhandenen Timer')
    if payload['timing'] == 'existing_for' and not assignments.get('presence_automations'):
        raise InvalidSelection('Vorhandenes for benötigt die zuständige Bestandsautomation')
    return validate_saved({'schema': SCHEMA, 'timing': payload['timing'], 'assignments': assignments})


def inspect_structure(config):
    """Extract references with exact JSON paths and inherited disabled status."""
    stack = [(config, 0)]; nodes = 0
    while stack:
        v, depth = stack.pop(); nodes += 1
        if depth > 18 or nodes > 5000:
            raise InvalidSelection('Automation überschreitet die Analysegrenze')
        if isinstance(v, dict): stack.extend((x, depth+1) for x in v.values())
        elif isinstance(v, list): stack.extend((x, depth+1) for x in v)
    if not isinstance(config, dict) or len(json.dumps(config, ensure_ascii=True)) > 120*1024:
        raise InvalidSelection('Automation zu groß oder ungültig')
    refs, warnings, timings = [], set(), set()
    if 'use_blueprint' in config: warnings.add('blueprint_not_expanded')
    def walk(value, path='', enabled=True, action=None):
        if isinstance(value, dict):
            state = value.get('enabled', True)
            enabled = False if enabled is False or state is False else None if enabled is None or not isinstance(state, bool) else True
            action = value.get('action', value.get('service', action))
            if any(k in value for k in ('area_id', 'device_id', 'label_id', 'floor_id')):
                warnings.add('indirect_targets_not_resolved')
            if isinstance(action, str) and action.startswith(('script.', 'scene.', 'automation.')):
                warnings.add('indirect_calls_not_expanded')
            for key, child in value.items():
                if key in ('alias', 'description'): continue
                p = path + '/' + str(key).replace('~', '~0').replace('/', '~1')
                if key == 'for' and enabled is True: timings.add('existing_for')
                if key == 'entity_id':
                    ids = child if isinstance(child, list) else child.split(',') if isinstance(child, str) else []
                    if not ids or any(not isinstance(e, str) or not ENTITY.fullmatch(e.strip()) for e in ids):
                        warnings.add('dynamic_or_invalid_entity_reference')
                    for i, eid in enumerate(ids):
                        if isinstance(eid, str) and ENTITY.fullmatch(eid.strip()):
                            refs.append({'entity_id': eid.strip(), 'path': p + ('/'+str(i) if isinstance(child, list) else ''),
                                'kind': 'direct', 'enabled': enabled, 'action': action if isinstance(action, str) else None,
                                'write_target': isinstance(action, str) and not any(x in p for x in ('/conditions/', '/condition/', '/if/')) and ('/target/entity_id' in p or '/data/entity_id' in p)})
                walk(child, p, enabled, action)
        elif isinstance(value, list):
            for i, child in enumerate(value): walk(child, path+'/'+str(i), enabled, action)
        elif isinstance(value, str) and any(x in value for x in ('{{', '{%')):
            warnings.add('template_semantics_not_evaluated')
            cleaned = re.sub(r'{#.*?#}', '', value, flags=re.S)
            ids = {m.group(2) for m in LITERAL.finditer(cleaned)} | {m.group(1) for m in DOT_STATE.finditer(cleaned)}
            for eid in sorted(ids): refs.append({'entity_id': eid, 'path': path, 'kind': 'template_literal',
                'enabled': enabled, 'action': action if isinstance(action, str) else None, 'write_target': False})
            warnings.add('template_dependency_coverage_partial')
    for plural, singular in (('triggers','trigger'), ('conditions','condition'), ('actions','action')):
        if plural in config and singular in config: warnings.add('ambiguous_root_aliases')
        walk(config.get(plural, config.get(singular, [])), '/'+(plural if plural in config else singular))
    for key in ('variables', 'trigger_variables'):
        if key in config: walk(config[key], '/' + key)
    for ref in refs:
        eid, path, call = ref['entity_id'], ref['path'], ref['action'] or ''
        ref['role_hint'] = ('presence_timer' if eid.startswith('timer.') else
            'presence_duration' if eid.startswith(('input_number.', 'number.')) and any(x in path for x in ('/for/', '/duration', '/delay')) else
            'presence_status' if eid.startswith('input_boolean.') and ref['write_target'] and call in ('input_boolean.turn_on','input_boolean.turn_off') else
            'presence_sources' if eid.startswith('binary_sensor.') and path.startswith(('/trigger/', '/triggers/')) else None)
        if eid.startswith('timer.') and ref['enabled'] is True: timings.add('timer')
    return {'fingerprint': fingerprint(config), 'references': refs, 'timing_methods': sorted(timings), 'limitations': sorted(warnings)}


def replacement_candidates(eid, catalog, area_ids):
    domain, _, old = eid.partition('.')
    candidates = []
    for row in catalog:
        if row['entity_id'].split('.')[0] != domain or row.get('disabled') or row['entity_id'] == eid:
            continue
        reasons, score = [], 0
        if row.get('unique_id') == old and row.get('platform') == domain:
            reasons.append('storage_key_matches_old_object_id'); score += 100
        if row.get('area_id') in area_ids:
            reasons.append('same_area'); score += 20
        similarity = SequenceMatcher(None, old, row['entity_id'].split('.',1)[1]).ratio()
        if similarity >= .55: reasons.append('similar_identifier'); score += round(similarity*20)
        if score < 25: continue
        candidates.append({'entity_id': row['entity_id'], 'name': row['name'], 'reasons': reasons,
            'rank_score': score, 'unit': row.get('unit'), 'state': row.get('state'),
            'requires_confirmation': True, 'semantic_equivalence': 'not_proven'})
    return sorted(candidates, key=lambda x: (-x['rank_score'], x['entity_id']))[:5]


def analyze(automation_id, config, catalog, area_ids, fresh):
    result = inspect_structure(config); by_id = {r['entity_id']: r for r in catalog}
    findings = []
    for eid in sorted({r['entity_id'] for r in result['references']}):
        row = by_id.get(eid)
        state = ('snapshot_stale' if not fresh else 'missing' if row is None else
                 'disabled' if row.get('disabled') else 'unavailable' if row.get('state') in (None,'unknown','unavailable') else 'present')
        refs = [r for r in result['references'] if r['entity_id'] == eid]
        findings.append({'entity_id': eid, 'name': row['name'] if row else eid,
            'status': state, 'references': refs,
            'candidates': replacement_candidates(eid, catalog, area_ids) if state == 'missing' else [],
            'role_hints': sorted({r['role_hint'] for r in refs if r['role_hint'] and r['enabled'] is True}),
            'derived': bool(row and row.get('platform') in ('input_boolean','template','group','threshold','min_max'))})
    return {'automation_id': automation_id, 'fingerprint': result['fingerprint'],
        'findings': findings, 'timing_methods': result['timing_methods'], 'limitations': result['limitations'],
        'coverage': 'selected_automation_only', 'execution': {'allowed': False}}


def repair_preview(automation_id, config, expected, replacements, catalog):
    """An exact, non-executable edit list. Do not return household config strings."""
    inspected = inspect_structure(config)
    if not isinstance(expected, str) or inspected['fingerprint'] != expected:
        from .selections import SelectionConflict
        raise SelectionConflict('Automation seit der Analyse geändert; erneut lesen')
    if not isinstance(replacements, dict) or not 1 <= len(replacements) <= 20:
        raise InvalidSelection('1 bis 20 bewusste Ersatzzuteilungen erforderlich')
    by_id = {r['entity_id']: r for r in catalog}
    edits = []
    for old, new in replacements.items():
        if (not isinstance(old, str) or not isinstance(new, str) or not ENTITY.fullmatch(old)
                or not ENTITY.fullmatch(new) or old == new or old.split('.')[0] != new.split('.')[0]):
            raise InvalidSelection('Ersatz muss eine andere Entität derselben Domain sein')
        refs = [r for r in inspected['references'] if r['entity_id'] == old]
        row = by_id.get(new)
        if not refs or not row or row.get('disabled') or row.get('state') in (None, 'unknown', 'unavailable'):
            raise InvalidSelection('Fundstelle oder verfügbarer Ersatz fehlt')
        old_row = by_id.get(old)
        if old_row and old_row.get('unit') and row.get('unit') != old_row['unit']:
            raise InvalidSelection('Einheit stimmt nicht überein; keine Gleichwertigkeit annehmen')
        edits.extend({'path': r['path'], 'before_entity_id': old, 'after_entity_id': new,
                      'kind': r['kind'], 'enabled': r['enabled']} for r in refs)
    return {'automation_id': automation_id, 'fingerprint': inspected['fingerprint'],
            'edits': edits, 'limitations': inspected['limitations'],
            'execution': {'allowed': False, 'reason': 'automation_write_executor_not_implemented'},
            'semantic_equivalence': 'requires_review', 'consumer_coverage': 'selected_automation_only'}


def naming_proposals(zone, config, catalog):
    """Uniform vocabulary; ID changes remain blocked without complete consumer coverage."""
    view = binding_view(config, catalog)
    stem = str(zone['name']).lower().replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
    stem = re.sub(r'[^a-z0-9]+', '_', stem).strip('_')[:48] or 'zone'
    names = {r['entity_id']: r for r in catalog}
    rows = []
    for role, suffix in ROLE_SUFFIX.items():
        for row in view['assignments'].get(role, []):
            eid = row.get('entity_id')
            if not eid: continue
            proposed_id = eid.split('.')[0] + '.' + stem + '_' + suffix
            rows.append({'role': role, 'entity_id': eid, 'current_name': row['name'],
                'proposed_name': zone['name'] + ' · ' + ROLES[role][0],
                'proposed_entity_id': proposed_id,
                'name_change_eligible': bool(row.get('unique_id') and row.get('platform') in HELPER_PLATFORMS and not row.get('disabled')),
                'entity_id_change': {'allowed': False,
                    'collision': proposed_id != eid and proposed_id in names,
                    'reason': 'consumer_coverage_incomplete',
                    'unverified': ['scripts','scenes','dashboards','groups','config_entries','external_apps']}})
    return rows
