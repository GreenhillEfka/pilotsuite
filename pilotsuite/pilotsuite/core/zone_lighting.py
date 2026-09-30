"""Lighting configuration/observation adapter for the existing zone and light policy.

No presence kernel, HA transport or execution authority lives here. The caller
supplies the primary zone decision; these bounded proposals never actuate lights.
"""
from copy import deepcopy
from dataclasses import asdict

from .lighting_policy import ATMOSPHERES, advance_lighting_preview, validate_lighting_checkpoint
from .organization import identity, fingerprint
from .presence_kernel import timestamp
from .selections import InvalidSelection
from .zone_presence import finite

KEY = 'zone_lighting'
DEFAULTS = {'lights': [], 'daylight_source': None, 'daylight_provenance': 'unconfirmed',
            'manual_entities': [], 'atmosphere': 'neutral', 'off_when_vacant': False,
            'minimum_pct': 15, 'maximum_pct': 85, 'max_age_seconds': 1800,
            'manual_hold_seconds': 900, 'stable_seconds': 30, 'minimum_interval': 60,
            'deadband': 5, 'maximum_step': 15}


def candidates(catalog, relevant):
    rows = [r for r in catalog if r['entity_id'] in relevant and r.get('in_registry')
            and not r.get('disabled') and r.get('platform') and r.get('unique_id')]
    return {'lights': [r['entity_id'] for r in rows if r['entity_id'].startswith('light.')],
            'daylight': [r['entity_id'] for r in rows if r['entity_id'].startswith('sensor.')
                        and r.get('device_class') == 'illuminance' and r.get('unit') in ('lx', 'lux')
                        and not r.get('derived')],
            'manual': [r['entity_id'] for r in rows if r['entity_id'].split('.')[0] in ('input_boolean', 'binary_sensor')]}


def validate_spec(value, catalog, relevant):
    if not isinstance(value, dict) or set(value) != set(DEFAULTS):
        raise InvalidSelection('Vollständige Lichtkonfiguration erforderlich')
    result = deepcopy(value); available = candidates(catalog, relevant)
    for key, role in [('lights', 'lights'), ('manual_entities', 'manual')]:
        ids = result[key]
        if (not isinstance(ids, list) or len(ids) > 20 or any(not isinstance(e, str) for e in ids)
                or len(set(ids)) != len(ids) or not set(ids) <= set(available[role])):
            raise InvalidSelection('Höchstens 20 bestätigte und stabile Quellen für ' + key)
        result[key] = sorted(ids)
    if not result['lights']:
        raise InvalidSelection('Mindestens eine relevante Leuchte wählen')
    source = result['daylight_source']
    if source is not None and (not isinstance(source, str) or source not in available['daylight']):
        raise InvalidSelection('Relevante, unabhängige Luxquelle wählen')
    if (result['daylight_provenance'] not in ('unconfirmed', 'outdoor') or
            source is None and result['daylight_provenance'] != 'unconfirmed'):
        raise InvalidSelection('Herkunft der Tageslichtquelle prüfen')
    for key, lo, hi in [('minimum_pct', 0, 100), ('maximum_pct', 0, 100),
                        ('max_age_seconds', 30, 86400), ('manual_hold_seconds', 30, 86400),
                        ('stable_seconds', 1, 3600), ('minimum_interval', 1, 3600),
                        ('deadband', 1, 100), ('maximum_step', 1, 100)]:
        if type(result[key]) is not int or not lo <= result[key] <= hi:
            raise InvalidSelection('Ungültiger Lichtparameter: ' + key)
    if result['minimum_pct'] > result['maximum_pct']:
        raise InvalidSelection('Minimum darf Maximum nicht überschreiten')
    if (not isinstance(result['atmosphere'], str) or result['atmosphere'] not in ATMOSPHERES
            or type(result['off_when_vacant']) is not bool):
        raise InvalidSelection('Ungültige Lichtstimmung oder Abschaltregel')
    return result


def basis(spec, catalog, presence):
    ids = set(spec['lights'] + spec['manual_entities']) | {spec['daylight_source']}
    metadata = [{**identity(r), **{k:r.get(k) for k in ('device_class','unit','disabled','derived')}}
                for r in catalog if r['entity_id'] in ids]
    return fingerprint({'spec': spec, 'metadata': sorted(metadata, key=lambda r:r['entity_id']),
                        'presence_basis': presence.get('basis'), 'presence_session': presence.get('session')})


def evaluate(spec, previous, states, presence, *, now, fresh, event=None, restart=False):
    """Consume one existing presence decision and advance only the lighting policy."""
    previous = previous or {}
    old_at = previous.get('observed_at')
    uninterrupted = not restart and finite(old_at) and 0 <= now-old_at <= 15
    points = previous.get('points', {})
    if not uninterrupted:
        points = {e:{**asdict(validate_lighting_checkpoint(point)), 'band':'unknown',
                     'candidate_band':None, 'candidate_since':None}
                  for e,point in points.items() if e in spec['lights']}
    holds = {e:t for e,t in previous.get('holds', {}).items()
             if e in spec['lights'] and finite(t) and now < t <= now+spec['manual_hold_seconds']}
    last_event = {e:at for e,at in previous.get('last_event', {}).items() if e in spec['lights'] and finite(at)}
    if fresh and isinstance(event, dict) and event.get('entity_id') in spec['lights']:
        eid = event['entity_id']; old, new = event.get('old_state'), event.get('new_state')
        if isinstance(old, dict) and isinstance(new, dict):
            at = timestamp(new.get('last_updated'))
            def effect(row):
                attrs = row.get('attributes') or {}
                return (row.get('state'), attrs.get('brightness'), attrs.get('color_temp_kelvin'), attrs.get('rgb_color'))
            if (finite(at) and 0 <= now-at <= 15 and at > last_event.get(eid, -1) and
                    old.get('state') in ('on','off') and new.get('state') in ('on','off') and effect(old) != effect(new)):
                holds[eid] = at + spec['manual_hold_seconds']; last_event[eid] = at
    valid_presence = bool(fresh and presence and presence.get('valid') is True)
    presence_state = presence['state'] if valid_presence else 'unknown'
    manual = [{'entity_id': e, 'state': states.get(e, {}).get('state', 'unknown')} for e in spec['manual_entities']]
    blocked = any(r['state'] != 'off' for r in manual)
    lux_id = spec['daylight_source']; raw = states.get(lux_id, {})
    at = timestamp(raw.get('last_reported', raw.get('last_updated')))
    age = now-at if finite(at) and at <= now else None
    lux = None
    if (fresh and age is not None and age <= spec['max_age_seconds'] and spec['daylight_provenance'] == 'outdoor'
            and raw.get('attributes', {}).get('unit_of_measurement') in ('lx', 'lux')):
        try:
            value = float(raw.get('state'))
            if finite(value) and value >= 0: lux = value
        except (ValueError, TypeError): pass
    next_points = {}; rows = []
    for eid in spec['lights']:
        live = states.get(eid, {}); attrs = live.get('attributes') or {}
        modes = attrs.get('supported_color_modes', [])
        modes = modes if isinstance(modes, list) else []
        dim = any(m in modes for m in ('brightness','color_temp','hs','rgb','rgbw','rgbww','xy','white'))
        raw_pct = attrs.get('brightness')
        pct = round(raw_pct*100/255, 1) if finite(raw_pct) and 0 <= raw_pct <= 255 else None
        if live.get('state') == 'off': pct = 0
        low, high = attrs.get('min_color_temp_kelvin'), attrs.get('max_color_temp_kelvin')
        color = 'color_temp' in modes and type(low) is int and type(high) is int and 1500 <= low <= high <= 10000
        held = blocked or eid in holds
        prior = points.get(eid)
        if not fresh or live.get('state') not in ('on','off'):
            # Forget stability across a gap, retain the last proposal's cooldown.
            if prior:
                next_points[eid] = {**prior, 'band':'unknown', 'candidate_band':None, 'candidate_since':None}
            rows.append({'entity_id':eid, 'status':'input_unavailable', 'settings':{},
                         'desired_brightness':None, 'reason':'Leuchtenzustand oder Verbindung unklar.', 'manual_until':holds.get(eid)})
            continue
        result = advance_lighting_preview(prior, now=now, presence_state=presence_state,
            daylight_lux=lux, daylight_available=lux is not None, current_on=live['state']=='on',
            current_brightness=pct, atmosphere=spec['atmosphere'], manual_override=held,
            off_when_vacant=spec['off_when_vacant'], supports_brightness=dim, supports_color_temp=color,
            minimum_kelvin=low if color else 2000, maximum_kelvin=high if color else 6500,
            minimum=spec['minimum_pct'], maximum=spec['maximum_pct'], stable_seconds=spec['stable_seconds'],
            minimum_interval=spec['minimum_interval'], deadband=spec['deadband'], maximum_step=spec['maximum_step'])
        next_points[eid] = asdict(result.checkpoint)
        rows.append({'entity_id':eid, 'status':result.status, 'settings':dict(result.proposed_settings),
                     'desired_brightness':result.desired_brightness, 'reason':result.explanation,
                     'manual_until':holds.get(eid)})
    state = {'points':next_points, 'holds':holds, 'last_event':last_event, 'observed_at':now}
    view = {'observed_at':now, 'presence_state':presence_state, 'lights':rows, 'manual_sources':manual,
            'daylight':{'entity_id':lux_id, 'value':lux, 'age_seconds':age, 'provenance':spec['daylight_provenance']},
            'execution':{'allowed':False, 'actions':[]},
            'message':'Laufender Lichtvergleich auf der PilotSuite-Präsenz. Bestehende HA-Steuerung bleibt zuständig.'}
    return state, view
