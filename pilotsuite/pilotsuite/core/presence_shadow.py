"""Live shadow adapters around the canonical presence and lighting kernels.

No HA client, history query, learner, service name or executable action enters this
module. Configuration is a bounded description of already-confirmed source roles.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import math
from copy import deepcopy

from .lighting_policy import ATMOSPHERES, LightingCheckpoint, advance_lighting_preview
from .organization import binding_view, fingerprint, identity, ENTITY
from .presence_kernel import PresenceCheckpoint, advance_presence, checkpoint_dict, validate_checkpoint, timestamp
from .selections import InvalidSelection

SCHEMA = "pilotsuite-presence-shadow-v1"
DEFAULTS = {"source_modes": {}, "grace_seconds": 300, "max_source_age_seconds": 1800,
            "lux_source": None, "lux_provenance": "unconfirmed", "atmosphere": "neutral",
            "off_when_vacant": False, "minimum_pct": 15, "maximum_pct": 85}
DERIVED = {"template", "group", "input_boolean", "threshold", "min_max"}
REASONS = {
    "not_observed": "Noch keine bestätigte Beobachtung.",
    "continuous_presence": "Eine gültige Dauerquelle meldet Präsenz.",
    "required_source_unknown": "Mindestens eine erforderliche Quelle ist unklar.",
    "source_dependencies_unknown": "Abhängigkeiten sind nicht unabhängig bestätigt.",
    "activity_pulse": "Ein beobachteter Bewegungsimpuls startet den Nachlauf.",
    "all_clear_starts_grace": "Die Dauerquelle wurde frei; der Nachlauf läuft.",
    "grace_deadline_pending": "Der ursprüngliche Ablaufzeitpunkt bleibt erhalten.",
    "restart_preserves_deadline": "Wiederanlauf ohne Verlängerung des Nachlaufs.",
    "deadline_elapsed_all_clear": "Nachlauf abgelaufen; alle benötigten Quellen sind gültig und frei.",
    "all_clear_remains_vacant": "Die Quellen bleiben frei.",
    "no_recent_presence_basis": "Ohne beobachteten Aufenthalt wird keine Abwesenheit behauptet.",
    "manual_cancel_requires_policy": "Abbruch ist keine Abwesenheitsmessung.",
}


def finite(value, lo=0, hi=1e9):
    return type(value) in (int, float) and math.isfinite(value) and lo <= value <= hi


def basis_for(inventory, config, catalog):
    """Resolve user-confirmed mappings, never discover membership from names."""
    by_id = {r['entity_id']: r for r in catalog}
    assignments = binding_view(config, catalog)['assignments']
    roles = config.get('roles', {})
    relevant = {r['entity_id'] for r in inventory.get('items', []) if r.get('decision') == 'relevant'}
    issues = []

    def chosen(role, fallback):
        if role in assignments:
            rows = assignments[role]
            if any(r.get('status') not in ('bound', 'renamed', 'exact_id_only') for r in rows):
                issues.append('unresolved_' + role)
            return sorted({r['entity_id'] for r in rows if isinstance(r.get('entity_id'), str)})
        return sorted(set(fallback))

    presence = roles.get('presence', [])
    owner_fallback = [e for e in presence if e.startswith('input_boolean.')]
    sources = chosen('presence_sources', [e for e in presence if e not in owner_fallback and e in relevant])
    owners = chosen('presence_status', owner_fallback if len(owner_fallback) == 1 else [])
    overrides = chosen('manual_override', [])
    blockers = chosen('automation_blocker', [])
    lights = sorted({e for e in roles.get('light', []) if e in relevant})
    lux = sorted({e for e in roles.get('illuminance', []) if e in relevant})
    if not sources or len(sources) > 20:
        issues.append('confirmed_sources_required')
    if len(owners) != 1:
        issues.append('one_comparison_status_required')
    if set(sources) & set(owners + overrides + blockers):
        issues.append('source_output_overlap')
    source_rows = []
    for eid in sources:
        row = by_id.get(eid, {})
        reason = None
        if not row.get('in_registry') or row.get('disabled'):
            reason = 'source_missing_or_disabled'
        elif not eid.startswith('binary_sensor.') or row.get('derived') or row.get('platform') in DERIVED:
            reason = 'independent_raw_source_required'
        if reason:
            issues.append(reason)
        source_rows.append({'entity_id': eid, 'name': row.get('name') or eid,
                            'suggested_mode': 'continuous' if row.get('device_class') in ('occupancy','presence') else 'pulse',
                            'blocked_reason': reason})
    watched = sorted(set(sources + owners + overrides + blockers + lights + lux))
    # State values and names are deliberately not identity. Rename, replacement,
    # type changes, membership/configuration edits invalidate the authorized basis.
    metadata = [{**identity(by_id[e]), 'device_id': by_id[e].get('device_id'),
                 'device_class': by_id[e].get('device_class'), 'derived': by_id[e].get('derived'),
                 'unit': by_id[e].get('unit'), 'disabled': by_id[e].get('disabled')}
                if e in by_id else {'entity_id': e, 'missing': True} for e in watched]
    data = {'sources': sources, 'owner': owners[0] if len(owners) == 1 else None,
            'overrides': overrides, 'blockers': blockers, 'lights': lights, 'lux': lux,
            'watched': watched, 'source_rows': source_rows, 'issues': sorted(set(issues))}
    data['hash'] = fingerprint({'metadata': metadata, 'organization': config.get('organization'),
                                'roles': roles, 'relevant': sorted(relevant)})
    return data


def validate_spec(value, basis):
    if not isinstance(value, dict) or set(value) != set(DEFAULTS):
        raise InvalidSelection('Vollständige, begrenzte Schattenkonfiguration erforderlich')
    result = deepcopy(value)
    modes = result['source_modes']
    if (not isinstance(modes, dict) or set(modes) != set(basis['sources']) or
            any(v not in ('pulse', 'continuous') for v in modes.values())):
        raise InvalidSelection('Jede bestätigte Rohquelle benötigt genau einen Signaltyp')
    if basis['issues']:
        raise InvalidSelection('Unvollständige oder abhängige Präsenzzuordnung: ' + ', '.join(basis['issues']))
    for key, lo, hi in [('grace_seconds', 1, 86400), ('max_source_age_seconds', 30, 86400),
                        ('minimum_pct', 0, 100), ('maximum_pct', 0, 100)]:
        if type(result[key]) is not int or not lo <= result[key] <= hi:
            raise InvalidSelection('Ungültiger Parameter: ' + key)
    if result['minimum_pct'] > result['maximum_pct']:
        raise InvalidSelection('Minimale Helligkeit darf das Maximum nicht überschreiten')
    if result['lux_source'] is not None and (not isinstance(result['lux_source'], str) or result['lux_source'] not in basis['lux']):
        raise InvalidSelection('Luxquelle muss eine ausdrücklich zugeordnete Helligkeitsquelle sein')
    if (result['lux_provenance'] not in ('unconfirmed', 'outdoor') or
            result['lux_source'] is None and result['lux_provenance'] != 'unconfirmed'):
        raise InvalidSelection('Tageslichtherkunft ist nicht bestätigt')
    if not isinstance(result['atmosphere'], str) or result['atmosphere'] not in ATMOSPHERES or type(result['off_when_vacant']) is not bool:
        raise InvalidSelection('Ungültiges Atmosphärenprofil oder Abschaltziel')
    return result


def observation(eid, states, now, max_age):
    item = states.get(eid, {})
    state = item.get('state')
    at = timestamp(item.get('last_reported', item.get('last_updated')))
    age = now-at if at is not None else None
    valid = state not in (None, 'unknown', 'unavailable') and age is not None and 0 <= age <= max_age
    return {'entity_id': eid, 'state': state if valid else 'unknown',
            'usable': valid, 'age_seconds': round(age, 1) if age is not None and age >= 0 else None,
            'reason': 'reported' if valid else 'unavailable_or_unverified_report_age'}


def logical_observation(eid, states, now, max_age):
    """HA helper/actuator states are held values, not fresh physical measurements."""
    row = observation(eid, states, now, max_age)
    value = states.get(eid, {}).get('state')
    if value in ('on', 'off'):
        row.update(state=value, usable=True, reason='current_ha_held_state')
    return row


def evaluate(record, basis, states, *, now, fresh, event=None, restart=False):
    """Advance existing kernels using cached HA observations, never claimed actions."""
    spec = record['spec']
    point = validate_checkpoint(record.get('checkpoint'))
    if point.last_activity_at is not None and point.last_activity_at > now:
        point = PresenceCheckpoint(reason='not_observed')
    rows = [dict(observation(e, states, now, spec['max_source_age_seconds']), mode=spec['source_modes'][e])
            for e in basis['sources']]
    for row in rows:
        if row['state'] not in ('on', 'off'):
            row.update(state='unknown', usable=False)
    pulse_at = None
    if isinstance(event, dict) and event.get('entity_id') in spec['source_modes']:
        old, new = event.get('old_state'), event.get('new_state')
        if (spec['source_modes'][event['entity_id']] == 'pulse' and isinstance(old, dict)
                and isinstance(new, dict) and old.get('state') == 'off' and new.get('state') == 'on'):
            at = timestamp(new.get('last_changed'))
            if at is not None and 0 <= now-at <= spec['max_source_age_seconds'] and (
                    point.last_activity_at is None or at >= point.last_activity_at):
                pulse_at = at
    # A pulse's high level is not a continuously present person. After its actual
    # event deadline, however, a still-high pulse sensor is NOT evidence of clear.
    def levels(at, receiving_pulse=False):
        result = []
        for row in rows:
            value = row['state'] if row['state'] in ('on','off') else 'unknown'
            if row['mode'] == 'pulse' and value == 'on':
                value = 'off' if receiving_pulse or point.deadline is not None and point.deadline > at else 'unknown'
            result.append(value)
        return result
    if fresh and pulse_at is not None:
        point = advance_presence(point, continuous=levels(pulse_at, True), pulse=True,
                                 now=pulse_at, grace_seconds=spec['grace_seconds']).checkpoint
    transition = advance_presence(point, continuous=levels(now) if fresh else ['unknown'],
                                  now=now, grace_seconds=spec['grace_seconds'], restart=restart)
    current = transition.checkpoint
    # Do not turn the five-second local observation tick into repeated persisted
    # "new activity" while an unchanged continuous source stays high.
    if current.state == point.state == 'occupied' and point.last_activity_at is not None:
        current = replace(current, last_activity_at=point.last_activity_at, generation=point.generation)
    owner = logical_observation(basis['owner'], states, now, spec['max_source_age_seconds'])
    if not fresh:
        owner.update(state='unknown', usable=False, reason='transport_unavailable')
    occupied = True if current.state in ('occupied','grace') else False if current.state == 'vacant' else None
    ha_occupied = owner['state'] == 'on' if owner['state'] in ('on','off') else None
    mismatch = 'unassessable' if occupied is None or ha_occupied is None else 'same' if occupied == ha_occupied else 'different'
    manual_rows = [logical_observation(e, states, now, spec['max_source_age_seconds']) for e in basis['overrides']+basis['blockers']]
    manual_hold = any(r['state'] != 'off' for r in manual_rows)
    lux_id = spec['lux_source']
    lux = observation(lux_id, states, now, spec['max_source_age_seconds']) if lux_id else None
    lux_value = None
    if lux and lux['usable'] and spec['lux_provenance'] == 'outdoor':
        raw = states[lux_id]
        if raw.get('attributes', {}).get('unit_of_measurement') in ('lx','lux'):
            try:
                v = float(raw['state'])
                if finite(v): lux_value = v
            except (ValueError, TypeError):
                pass
    lights, lighting_points = [], {}
    previous_lights = record.get('lighting', {})
    for eid in basis['lights'][:20]:
        live = logical_observation(eid, states, now, spec['max_source_age_seconds'])
        attrs = states.get(eid, {}).get('attributes', {})
        attrs = attrs if isinstance(attrs, dict) else {}
        modes = attrs.get('supported_color_modes', [])
        modes = modes if isinstance(modes, list) else []
        brightness = attrs.get('brightness')
        dim = any(m in modes for m in ('brightness','color_temp','hs','rgb','rgbw','rgbww','xy','white'))
        pct = (round(brightness*100/255, 1) if finite(brightness, 0, 255) else None)
        if live['state'] == 'off': pct = 0
        kmin, kmax = attrs.get('min_color_temp_kelvin'), attrs.get('max_color_temp_kelvin')
        kelvin = 'color_temp' in modes and type(kmin) is int and type(kmax) is int and 1500 <= kmin <= kmax <= 10000
        prior = previous_lights.get(eid)
        if restart or not fresh or current.state == 'unknown' or manual_hold or lux_value is None:
            prior = None  # no stabilization across a data gap / manual intervention
        if not live['usable'] or live['state'] not in ('on','off') or not fresh:
            lights.append({'entity_id': eid, 'status':'input_unavailable', 'settings': {},
                           'desired_brightness':None,'reason':'Leuchtenzustand oder Verbindung nicht bestätigt.'})
            continue
        try:
            result = advance_lighting_preview(prior, now=now, presence_state=current.state,
                daylight_lux=lux_value, daylight_available=lux_value is not None,
                current_on=live['state']=='on', current_brightness=pct, atmosphere=spec['atmosphere'],
                manual_override=manual_hold, off_when_vacant=spec['off_when_vacant'],
                supports_brightness=dim, supports_color_temp=kelvin,
                minimum_kelvin=kmin if kelvin else 2000, maximum_kelvin=kmax if kelvin else 6500,
                minimum=spec['minimum_pct'], maximum=spec['maximum_pct'])
        except InvalidSelection:
            lights.append({'entity_id':eid,'status':'input_unavailable','settings':{},
                           'desired_brightness':None,'reason':'Ungültiger Lichtzwischenstand; keine Freigabe.'})
            continue
        lighting_points[eid] = asdict(result.checkpoint)
        lights.append({'entity_id': eid, 'status':result.status,'settings':dict(result.proposed_settings),
                       'desired_brightness':result.desired_brightness,'reason':result.explanation})
    view = {'computed':checkpoint_dict(current),'explanation':transition.explanation,
            'ha_status': owner, 'comparison':mismatch, 'sources': rows,
            'manual_hold':manual_hold, 'manual_sources':manual_rows,
            'lights':lights, 'daylight':{'source':lux_id,'provenance':spec['lux_provenance'],
                                      'value':lux_value,'usable':lux_value is not None and fresh},
            'observed_at':now,'transport_fresh':fresh,
            'report_age_limit_seconds':spec['max_source_age_seconds'],
            'limitations':['Abweichung ist ein Prüfpunkt, kein Fehlerurteil.',
              'Meldealter ist kein Nachweis physischer Messgenauigkeit.',
              'Nur letzter Zwischenstand; keine neue Lern- oder Verlaufssammlung.',
              'Kein Gerät, Timer oder HA-Raumstatus wird verändert.']}
    return checkpoint_dict(current), lighting_points, view
