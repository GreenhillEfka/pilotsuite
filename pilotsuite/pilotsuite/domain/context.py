"""Role groups: robust climate median with visible spread, no reference mixing."""
from dataclasses import replace
from statistics import median
from pilotsuite.core.context import ROLE_KINDS


def context_summary(neurons, roles):
    by_id = {n.entity_id: n for n in neurons}
    climate, summary = [], {}
    references = set(roles.get('reference_temperature', []))
    for kind in ('temperature', 'humidity', 'illuminance'):
        candidates = [n for n in neurons if n.kind == kind and n.entity_id not in references]
        explicit = roles.get(kind, [])
        members = [by_id[e] for e in explicit if e in by_id and by_id[e].kind == kind] if kind in roles else candidates if len(candidates)==1 else []
        valid = [n for n in members if n.quality == 'good' and type(n.value) in (int, float)]
        missing = len(explicit)-len(members) if explicit else 0
        status = ('partial' if missing or len(valid)<len(members) else 'available') if valid else 'unavailable' if members or explicit else 'not_selected' if kind in roles and candidates else 'ambiguous' if len(candidates)>1 else 'not_present'
        values = [n.value for n in valid]
        value = median(values) if values else None
        summary[kind] = {'status': status, 'sources': [n.entity_id for n in members], 'requested_sources': explicit,
                         'value': value, 'unit': valid[0].unit if valid else None, 'candidate_count': len(candidates),
                         'min': min(values) if values else None, 'max': max(values) if values else None,
                         'spread': max(values)-min(values) if values else None, 'valid_count': len(valid), 'missing_count': missing, 'total_count': len(members)+missing,
                         'measurements': [{'entity_id': n.entity_id, 'value': n.value, 'unit': n.unit, 'quality': n.quality} for n in members],
                         'aggregation': 'median', 'spatial_scope': 'zone summary, not necessarily one room'}
        # Mood severity uses the aggregate; evidence retains every contributing sensor below.
        if valid and kind in {'temperature', 'humidity'}:
            climate.append(replace(valid[0], entity_id='aggregate.'+kind, name='Zone median '+kind, value=value))
        elif members and kind in {'temperature', 'humidity'}:
            climate.append(members[0])
    summary['reference_temperature'] = [{'source': n.entity_id, 'value': n.value, 'unit': n.unit, 'quality': n.quality} for n in neurons if n.entity_id in references and n.kind=='temperature']
    for label, kinds in [('presence', ROLE_KINDS['presence']), ('daylight_binary', ROLE_KINDS['daylight_binary']), ('light', {'light'})]:
        members = [n for n in neurons if n.kind in kinds]
        candidate_count = len(members)
        expected = roles.get(label, [])
        if label in {'presence', 'daylight_binary'} or label in roles:
            members = [n for n in members if n.entity_id in expected]
        missing = len(expected)-len(members) if expected else 0
        valid = [n for n in members if n.quality == 'good' and type(n.value) is bool]
        on = sum(n.value is True for n in valid)
        summary[label] = {'status': 'not_selected' if not expected and candidate_count and (label in {'presence', 'daylight_binary'} or label in roles) else 'unavailable' if missing and not members else 'not_present' if not members else 'unavailable' if not valid else 'partial' if missing or len(valid)<len(members) else 'available',
                          'sources': [n.entity_id for n in members], 'requested_sources': expected,
                          'aggregation': 'any_on', 'on': on, 'valid': len(valid), 'total': len(members)+missing,
                          'active': True if on else None if missing or len(valid)<len(members) or not members else False}
    for kind in ('temperature', 'humidity', 'illuminance', 'presence', 'daylight_binary', 'light'):
        info = summary[kind]
        info['reference'] = {'value': info.get('value', info.get('active')),
                             'unit': info.get('unit'), 'sources': info['sources'],
                             'status': info['status'], 'method': info['aggregation'],
                             'virtual': True}
    return summary, climate
