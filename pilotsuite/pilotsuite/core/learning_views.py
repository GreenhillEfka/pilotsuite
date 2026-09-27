"""Bounded read models: local time, sampled observability and activation context."""
from collections import Counter
from datetime import datetime, UTC
import math
import re
from statistics import median
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from .selections import InvalidSelection

ENTITY_ID = re.compile(r"[a-z0-9_]+\.[a-z0-9_]+\Z")


def _valid_timestamp(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        return False
    try:
        datetime.fromtimestamp(value, UTC)
    except (OverflowError, OSError, ValueError):
        return False
    return True


def _valid_lux(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def _source_ids(value):
    if not isinstance(value, (list, tuple)):
        return []
    result = []
    for item in value:
        if (isinstance(item, str) and len(item) <= 255 and ENTITY_ID.fullmatch(item)
                and item not in result):
            result.append(item)
    return result


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
    if not _valid_timestamp(occurred):
        raise InvalidSelection('occurred must be a finite supported timestamp')
    zone, mode = temporal_settings(detector)
    local = datetime.fromtimestamp(occurred, zone)
    group = 'all' if mode == 'all' else 'weekday' if local.weekday() < 5 else 'weekend'
    # Repeated DST wall-clock hours remain one local date/window, not extra days.
    return (group, local.hour // 2), local.date().isoformat()


def coverage_report(rows):
    rows = [(slot, state) for slot, state in rows
            if _valid_timestamp(slot) and isinstance(state, str) and 0 < len(state) <= 64]
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
        info = summary.get(kind, {}) if isinstance(summary, dict) else {}
        info = info if isinstance(info, dict) else {}
        selected = _source_ids(roles.get(kind, [])) if isinstance(roles, dict) else []
        # Context logging uses only explicitly saved groups, never legacy defaults.
        sources = [e for e in _source_ids(info.get('sources', [])) if e in selected]
        value = info.get('active' if kind == 'light' else 'value')
        value_valid = type(value) is bool if kind == 'light' else _valid_lux(value)
        valid = (bool(selected) and set(sources) == set(selected)
                 and info.get('status') == 'available' and value_valid)
        result[kind] = {'value': value if valid else None,
                        'sources': sources, 'status': 'available' if valid else 'unknown'}
    return result


def context_report(records, detector):
    buckets = {}
    for occurred, data in records:
        try:
            key, day = time_bucket(occurred, detector)
        except InvalidSelection:
            continue
        data = data if isinstance(data, dict) else {}
        group = buckets.setdefault(key, {'days': set(), 'known_light_days': set(), 'light_on': 0, 'light_off': 0, 'light_unknown': 0, 'lux': [], 'count': 0, 'sources': set()})
        group['days'].add(day); group['count'] += 1
        light_info = data.get('light', {})
        light_info = light_info if isinstance(light_info, dict) else {}
        lux_info = data.get('illuminance', {})
        lux_info = lux_info if isinstance(lux_info, dict) else {}
        light = light_info.get('value')
        group['light_on' if light is True else 'light_off' if light is False else 'light_unknown'] += 1
        if type(light) is bool: group['known_light_days'].add(day)
        lux = lux_info.get('value')
        if _valid_lux(lux): group['lux'].append(lux)
        group['sources'].update(_source_ids(light_info.get('sources', [])))
        group['sources'].update(_source_ids(lux_info.get('sources', [])))
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
