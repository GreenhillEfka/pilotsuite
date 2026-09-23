"""Transient, scoped HA history projection and retrospective activity checks.

Raw state samples never become a second HA database. Import only accepted activity
transitions into the existing learning store. Unknown values never become off/zero.
"""
from bisect import bisect_right
from collections import defaultdict
from datetime import datetime, UTC
from statistics import median
import math
from .selections import InvalidSelection
from .learning_views import time_bucket

KINDS = ('temperature', 'humidity', 'illuminance', 'presence', 'light')
UNITS = {'temperature': '°C', 'humidity': '%', 'illuminance': 'lx'}


def timestamp(value):
    try:
        if type(value) in (int, float):
            return float(value) if math.isfinite(value) else None
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.timestamp() if dt.tzinfo else None
    except (ValueError, TypeError, AttributeError, OverflowError):
        return None


def interval(start, end, now):
    a, b = timestamp(start), timestamp(end)
    if a is None or b is None or not 0 < b-a <= 30*86400 or a < now-30*86400-60 or b > now+5:
        raise InvalidSelection('Choose an explicit timezone-aware interval within the last 30 days')
    return a, b


def numeric(value, kind, unit):
    try:
        if isinstance(value, bool): return None
        v = float(value)
    except (TypeError, ValueError): return None
    if not math.isfinite(v): return None
    if kind == 'temperature':
        if unit == '°F': v = (v-32)*5/9
        elif unit == 'K': v -= 273.15
        elif unit != '°C': return None
        return v if v >= -273.15 else None
    if kind == 'humidity': return v if unit == '%' and 0 <= v <= 100 else None
    if kind == 'illuminance': return v if unit in ('lx', 'lux') and v >= 0 else None
    return None


def normalize(records, roles, start, end, *, statistics=False, metadata=None):
    result = {}
    for kind in KINDS:
        for entity in roles.get(kind, []):
            points = {}
            for row in records.get(entity, []):
                if not isinstance(row, dict): continue
                t = timestamp(row.get('start') if statistics else row.get('lu', row.get('last_updated', row.get('last_changed'))))
                if t is None: continue
                if statistics and t > 100000000000: t /= 1000
                if t > end: continue
                if statistics:
                    # HA statistics API uses epoch milliseconds, unlike compressed history.
                    if t > 100000000000: t /= 1000
                    if not start <= t < end: continue
                    unit = (metadata or {}).get(entity, {}).get('unit_of_measurement')
                    v = numeric(row.get('mean'), kind, unit)
                else:
                    attrs = row.get('a', row.get('attributes', {})) or {}
                    value = row.get('s', row.get('state'))
                    v = (True if value == 'on' else False if value == 'off' else None) if kind in ('presence','light') else numeric(value, kind, attrs.get('unit_of_measurement'))
                points[t] = v
            result[entity] = {'kind': kind, 'unit': UNITS.get(kind),
                              'points': sorted(points.items())}
    return result


def activations(series, roles, start, end):
    events = []
    for entity in roles.get('presence', []):
        previous = None
        for t, value in series.get(entity, {}).get('points', []):
            if start < t < end and previous is False and value is True:
                events.append((t, entity))
            previous = value
    # Same five-minute zone-wide episode boundary as live activity-v1.
    accepted = []
    for event in sorted(set(events)):
        if not accepted or event[0]-accepted[-1][0] >= 300: accepted.append(event)
    return accepted


def at(series, entity, t):
    points = series.get(entity, {}).get('points', [])
    i = bisect_right(points, t, key=lambda point: point[0])-1
    if i < 0 or t-points[i][0] > 3600: return None
    return points[i][1]


def reference(series, ids, t, kind):
    values = [at(series, entity, t) for entity in ids]
    valid = [v for v in values if v is not None]
    if kind in ('presence','light'):
        value = True if any(v is True for v in valid) else False if ids and len(valid)==len(ids) else None
    else: value = median(valid) if valid else None
    return {'value': value, 'min': min(valid) if valid else None,
            'max': max(valid) if valid else None, 'valid': len(valid), 'total': len(ids)}


def trend_view(series, roles, start, end, *, statistics=False):
    # <= 481 points per source. Never use decimated chart data for learning.
    step = max(300, math.ceil((end-start)/480))
    times = [start+i*step for i in range(int((end-start)//step)+1)]
    sources, references = [], []
    for entity, info in series.items():
        if statistics:
            pts = [[t,v] for t,v in info['points'] if start <= t < end]
        else:
            pts = [[t,at(series,entity,t)] for t in times]
        sources.append({'entity_id': entity, 'kind': info['kind'], 'unit': info['unit'],
                        'record_count': len(info['points']), 'points': pts})
    if not statistics:
        for kind in KINDS:
            ids = roles.get(kind, [])
            if ids: references.append({'kind':kind,'unit':UNITS.get(kind), 'sources':ids,
                'points': [dict(t=t, **reference(series,ids,t,kind)) for t in times]})
    return {'sources':sources,'references':references,'step_seconds':step,
            'basis':'hourly_source_statistics' if statistics else 'sampled_recorded_states',
            'carry_limit_seconds': None if statistics else 3600,
            'warning':'Stundenmittel sind keine Schaltbelege.' if statistics else
            'Stichproben mit höchstens einer Stunde Fortschreibung. Leere Abschnitte sind unbekannt; Recorder-Zustände beweisen keine lückenlose Sensorüberwachung.'}


def retrospective(events, detector, start, end):
    """Chronological holdout, fixed config; same time buckets as activity-v1."""
    split = start+(end-start)*0.7
    groups = defaultdict(lambda: [[], []])
    heat = defaultdict(int)
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(detector.get('timezone','UTC'))
    for t, entity in events:
        key, day = time_bucket(t, detector)
        groups[key][0 if t < split else 1].append((t,day))
        local = datetime.fromtimestamp(t,tz)
        heat[(local.weekday(),local.hour//2)] += 1
    checks=[]
    for (group,bucket),(train,test) in sorted(groups.items()):
        if len(train) < detector['min_events'] or len({d for _,d in train}) < detector['min_days']: continue
        checks.append({'day_group':group,'start_hour':bucket*2,'training_events':len(train),
                       'training_days':len({d for _,d in train}), 'later_events':len(test),
                       'later_days':len({d for _,d in test}),
                       'state':'reobserved' if test else 'insufficient_later_evidence'})
    return {'split_at':split,'checks':checks,'timezone':tz.key,
            'heatmap':[{'weekday':d,'start_hour':b*2,'events':n} for (d,b),n in sorted(heat.items())],
            'limitations':'Frühere 70 %: Musterbildung, spätere 30 %: erneutes Auftreten prüfen. Keine Genauigkeitsquote; fehlende Belege können Datenlücken sein. Aktuelle Sensorgruppen rückwirkend angewendet.'}
