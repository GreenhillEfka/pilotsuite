"""HA labels describe membership; explicit selection authorizes analysis, not control."""
from .organization import identity, same_identity
from .selections import InvalidSelection, SelectionConflict
from .zone_ontology import ROLES

KEY = 'zone_structure'
SCHEMA = 'pilotsuite-zone-structure-v1'
MAX_MEMBERS = 500
PENDING_LABEL = '$new_zone_label'


def label_catalog(labels, catalog):
    counts = {}
    for row in catalog:
        for label in set(row.get('labels', [])) | set(row.get('device_labels', [])):
            counts[label] = counts.get(label, 0) + 1
    return [{'label_id': row['label_id'], 'name': row.get('name') or row['label_id'],
             'member_count': counts.get(row['label_id'], 0)} for row in labels]


def label_members(label_id, labels, catalog):
    label = next((row for row in labels if row['label_id'] == label_id), None)
    if label is None:
        raise InvalidSelection('Das gewählte HA-Label existiert nicht mehr')
    role_names = {row['label_id']: row['name'] for row in labels if row.get('name') in ROLES}
    members = []
    for row in catalog:
        direct = label_id in row.get('labels', [])
        inherited = label_id in row.get('device_labels', [])
        if not direct and not inherited:
            continue
        members.append({**row, 'membership_source': 'entity' if direct else 'device',
                        'habitus_roles': sorted({role_names[key] for key in row.get('labels', []) if key in role_names})})
    if len(members) > MAX_MEMBERS:
        raise InvalidSelection('Mehr als 500 Labelmitglieder; Label vor dem Import eingrenzen')
    return {'label_id': label_id, 'name': label['name'], 'members': members,
            'control_enabled': False, 'learning_changed': False}


def member_identities(profile, catalog):
    """Explain saved identities using the existing resolver; never migrate members."""
    from .organization import resolve
    result = []
    for eid, member in (profile or {}).get('members', {}).items():
        row = resolve(member['identity'], catalog)
        status = row['status']
        if row.get('entity_id') and not row.get('in_registry'):
            status = 'identity_unresolved'
        elif row.get('disabled'):
            status = 'disabled'
        result.append({'saved_entity_id':eid,
                       'entity_id':row.get('entity_id') if status != 'identity_unresolved' else None,
                       'name':row.get('name') or eid, 'status':status})
    return result


def setup_profile(payload, labels, catalog, previous=None):
    required = {'label_id', 'entity_ids', 'relevant_entity_ids'}
    if not isinstance(payload, dict) or not required <= set(payload) or set(payload) - required - {'roles', 'label_name'}:
        raise InvalidSelection('Zonenlabel, Mitglieder und relevante Quellen erforderlich')
    label_id = payload['label_id']
    pending = label_id is None
    if pending:
        name = payload.get('label_name')
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 80 or any(ord(c) < 32 for c in name):
            raise InvalidSelection('Neuen Labelnamen mit 1–80 Zeichen angeben')
        name = name.strip()
        if name in ROLES or any(row['name'].casefold() == name.casefold() for row in labels):
            raise InvalidSelection('Dieser Labelname existiert bereits oder ist eine Habitus-Rolle; vorhandenes Label wählen')
    elif 'label_name' in payload or not isinstance(label_id, str) or label_id not in {row['label_id'] for row in labels}:
        raise InvalidSelection('Vorhandenes Zonenlabel wählen')
    role_names = {row['label_id']: row['name'] for row in labels if row.get('name') in ROLES}
    if label_id in role_names:
        raise InvalidSelection('Ein Habitus-Rollenlabel ist kein Zonenlabel')
    for key in ('entity_ids', 'relevant_entity_ids'):
        values = payload[key]
        if (not isinstance(values, list) or len(values) > MAX_MEMBERS
                or any(not isinstance(value, str) for value in values) or len(set(values)) != len(values)):
            raise InvalidSelection('Höchstens 500 unterschiedliche Entitäten wählen')
    if not set(payload['relevant_entity_ids']) <= set(payload['entity_ids']):
        raise InvalidSelection('Relevante Quellen müssen zur gewählten Zone gehören')
    index = {row['entity_id']: row for row in catalog}
    requested_roles = payload.get('roles', {})
    if not isinstance(requested_roles, dict) or not set(requested_roles) <= set(payload['entity_ids']):
        raise InvalidSelection('Rollen müssen zu ausgewählten Mitgliedern gehören')
    for roles in requested_roles.values():
        if (not isinstance(roles, list) or len(roles) > len(ROLES)
                or any(not isinstance(role, str) or role not in ROLES for role in roles)
                or len(set(roles)) != len(roles)):
            raise InvalidSelection('Unbekannte oder doppelte Habitus-Rolle')
    members = {}
    for eid in sorted(payload['entity_ids']):
        row = index.get(eid)
        saved = (previous or {}).get('members', {}).get(eid)
        if saved and (not row or not row.get('in_registry') or row.get('disabled')):
            if row and row.get('in_registry') and not same_identity(saved['identity'], row):
                raise SelectionConflict('Gespeicherte Identität wurde ersetzt: ' + eid)
            if eid in requested_roles and sorted(requested_roles[eid]) != saved['roles']:
                raise InvalidSelection('Rollen eines fehlenden Mitglieds erst nach Klärung ändern')
            members[eid] = saved
            continue
        if not row or row.get('disabled') or not row.get('in_registry') or not row.get('unique_id') or not row.get('platform'):
            raise InvalidSelection('Mitglied fehlt, ist deaktiviert oder nicht stabil identifizierbar: ' + eid)
        roles = sorted({role_names[key] for key in row.get('labels', []) if key in role_names})
        if eid in requested_roles:
            roles = requested_roles[eid]
            if (not isinstance(roles, list) or len(roles) > len(ROLES)
                    or any(not isinstance(role, str) or role not in ROLES for role in roles)
                    or len(set(roles)) != len(roles)):
                raise InvalidSelection('Unbekannte oder doppelte Habitus-Rolle')
            roles = sorted(roles)
        if 'Habitus Zone' in roles and (not eid.startswith('binary_sensor.') or row.get('device_class') not in ('occupancy', 'presence')):
            raise InvalidSelection('Zonenanker muss ein Anwesenheits-Binärsensor sein')
        members[eid] = {'identity': identity(row), 'roles': roles}
    anchors = [eid for eid, member in members.items() if 'Habitus Zone' in member['roles']]
    if len(anchors) > 1:
        raise InvalidSelection('Mehrere Zonenanker gefunden; zuerst den öffentlichen Status klären')
    if set(anchors) & set(payload['relevant_entity_ids']):
        raise InvalidSelection('Der Zonenanker ist ein Ausgang, keine unabhängige Präsenzquelle')
    return {'schema': SCHEMA, 'label_id': label_id, 'members': members, **({'label_name': name} if pending else {})}


def connection_suggestions(config, catalog, relevant, *, fresh):
    """Propose known semantics, never infer helper purpose from similar names."""
    if not fresh:
        return {'assignments':{}, 'reason':'snapshot_unconfirmed', 'changed':False}
    structure = config.get(KEY) or {}
    saved = config.get('organization', {}).get('assignments', {})
    owned = set(((config.get('zone_presence_v2') or {}).get('package') or {}).get('entities', {}).values())
    items = {row['entity_id']:row for row in catalog}
    eligible = {}
    for eid, member in structure.get('members', {}).items():
        row = items.get(eid)
        if (row and eid not in owned and row.get('in_registry') and not row.get('disabled') and
                same_identity(member['identity'], row)):
            eligible[eid] = row
    anchors = [eid for eid,row in eligible.items() if 'Habitus Zone' in structure['members'][eid]['roles'] and
               eid.startswith('binary_sensor.') and row.get('device_class') in ('occupancy','presence')]
    input_ids = {row['entity_id'] for row in (config.get('zone_presence_v2') or {}).get('spec', {}).get('sources', [])}
    assignments = {}
    if len(anchors)==1 and anchors[0] not in input_ids and not saved.get('presence_output'):
        assignments['presence_output'] = anchors
    bound_outputs = {row['entity_id'] for role in ('presence_status','presence_output') for row in saved.get(role, [])}
    sources = sorted(eid for eid,row in eligible.items() if eid in relevant and eid not in anchors and eid not in bound_outputs and
                     eid.startswith('binary_sensor.') and not row.get('derived') and
                     row.get('device_class') in ('motion','occupancy','presence'))
    if sources and len(sources)<=20 and not saved.get('presence_sources'):
        assignments['presence_sources'] = sources
    return {'assignments':assignments, 'reason':'confirmed_zone_members', 'changed':False,
            'source_limit_exceeded':len(sources)>20,
            'preserved_roles':sorted(role for role in ('presence_output','presence_sources') if saved.get(role))}
