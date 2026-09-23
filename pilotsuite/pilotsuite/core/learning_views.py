"""Bounded read models: local time, sampled observability and activation context."""
from collections import Counter
from datetime import datetime, UTC
from statistics import median
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from .selections import InvalidSelection


def temporal_settings(detector):
    name = detector.get('timezone', 'UTC')
    mode = detector.get('day_mode', 'all')
    if not isinstance(name, str) or len(name) > 100:
        raise InvalidSelection('timezone must be an IANA timezone')
    try:
        zone = ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        raise InvalidSelection('Unknown IANA timezone') from None
    if mode not in ('all', 'weekday_weekend'):
        raise InvalidSelection('day_mode must be all or weekday_weekend')
    return zone, mode


def time_bucket(occurred, detector):
    zone, mode = temporal_settings(detector)
    local = datetime.fromtimestamp(occurred, zone)
    group = 'all' if mode == 'all' else 'weekday' if local.weekday() < 5 else 'weekend'
    # Repeated DST wall-clock hours remain one local date/window, not extra days.
    return (group, local.hour // 2), local.date().isoformat()


def coverage_report(rows):
    slots = {slot for slot, _ in rows}
    impaired = {slot for slot, state in rows if state != 'ready'}
    ready = {slot for slot, state in rows if state == 'ready'} - impaired
    return {'bucket_seconds': 300, 'sampled_slots': len(slots), 'ready_only_slots': len(ready),
            'impaired_slots': len(impaired), 'states': dict(Counter(state for _, state in rows)),
            'unobserved_slots_between_checks': ((max(slots)-min(slots))//300+1-len(slots)) if slots else 0,
            'first_check_at': datetime.fromtimestamp(min(slots), UTC).isoformat() if slots else None,
            'last_check_at': datetime.fromtimestamp(max(slots), UTC).isoformat() if slots else None,
            'basis': 'sampled_transport_and_source_availability_not_continuous_sensor_coverage'}


def activation_context(summary, roles):
    result = {}
    for kind in ('light', 'illuminance'):
        info = summary.get(kind, {})
        selected = roles.get(kind, [])
        # Context logging uses only explicitly saved groups, never legacy defaults.
        sources = [e for e in info.get('sources', []) if e in selected]
        valid = bool(selected) and set(sources) == set(selected) and info.get('status') == 'available'
        result[kind] = {'value': info.get('active' if kind == 'light' else 'value') if valid else None,
                        'sources': sources, 'status': 'available' if valid else 'unknown'}
    return result


def context_report(records, detector):
    buckets = {}
    for occurred, data in records:
        key, day = time_bucket(occurred, detector)
        group = buckets.setdefault(key, {'days': set(), 'known_light_days': set(), 'light_on': 0, 'light_off': 0, 'light_unknown': 0, 'lux': [], 'count': 0, 'sources': set()})
        group['days'].add(day); group['count'] += 1
        light = data.get('light', {}).get('value')
        group['light_on' if light is True else 'light_off' if light is False else 'light_unknown'] += 1
        if type(light) is bool: group['known_light_days'].add(day)
        lux = data.get('illuminance', {}).get('value')
        if type(lux) in (int, float): group['lux'].append(lux)
        for kind in ('light', 'illuminance'):
            group['sources'].update(data.get(kind, {}).get('sources', []))
    out = []
    for (day_group, bucket), group in sorted(buckets.items()):
        complete = group['light_on'] + group['light_off']
        out.append({'day_group': day_group, 'start_hour': bucket*2, 'end_hour': bucket*2+2,
                    'activations': group['count'], 'days': len(group['days']),
                    'light_on': group['light_on'], 'light_off': group['light_off'], 'light_unknown': group['light_unknown'],
                    'lux_count': len(group['lux']), 'lux_median': median(group['lux']) if group['lux'] else None,
                    'sources': sorted(group['sources']), 'risk': 'read_only',
                    'review_ready': complete >= detector['min_events'] and len(group['known_light_days']) >= detector['min_days'],
                    'proposal': 'Lichtbedarf und bestehende Automationen prüfen. Gleichzeitige Zustände belegen weder eine Schaltursache noch eine gewünschte Zielhelligkeit.'})
    return out
