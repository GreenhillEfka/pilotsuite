"""Existing helper inspection: stable storage identity, no adoption by name."""
from __future__ import annotations
import math

from .selections import InvalidSelection

SIMPLE_HELPERS = frozenset({"input_boolean", "input_select", "input_number", "timer"})
FLOW_HELPERS = frozenset({"template", "group", "min_max", "threshold", "derivative", "integration",
                          "statistics", "trend", "filter", "tod", "generic_thermostat", "generic_hygrostat"})
SAFE_FIELDS = {"input_boolean": ("initial",), "timer": ("duration", "restore"),
               "input_number": ("min", "max", "step", "unit_of_measurement", "mode", "initial"),
               "input_select": ("options", "initial")}


def candidates(inventory, registry, bindings=None):
    items = {i['entity_id']: i for i in inventory['items']}
    bound_ids = {r['entity_id'] for rows in (bindings or {}).get('assignments', {}).values() for r in rows if r.get('entity_id')}
    result = []
    for row in registry:
        if (row['entity_id'] in items or row['entity_id'] in bound_ids) and row.get('platform') in SIMPLE_HELPERS | FLOW_HELPERS:
            result.append({**row, 'name': items.get(row['entity_id'], {}).get('name', row['entity_id']),
                           'decision': items.get(row['entity_id'], {}).get('decision', 'manually_bound')})
    if len(result) > 200:
        raise InvalidSelection('Zu viele Helfer für eine Prüfung; Zone eingrenzen')
    return result


def inspect(rows, collections, roles):
    output = []
    for row in rows:
        platform = row['platform']
        matches = [cfg for cfg in collections.get(platform, [])
                   if isinstance(row.get('unique_id'), str) and cfg.get('id') == row['unique_id']]
        matched = platform in SIMPLE_HELPERS and len(matches) == 1 and not row.get('disabled')
        config = {}
        if matched:
            for field in SAFE_FIELDS[platform]:
                value = matches[0].get(field)
                if value is None:
                    continue
                if field == 'options':
                    if isinstance(value, list) and len(value) <= 100 and all(isinstance(x, str) and len(x) <= 255 for x in value):
                        config[field] = value[:]
                elif isinstance(value, (str, bool, int, float)) and len(str(value)) <= 255:
                    if isinstance(value, float) and not math.isfinite(value):
                        continue
                    config[field] = value
        warnings = []
        if platform == 'timer' and matched and config.get('restore') is not True:
            warnings.append('Timer-Restore ist nicht bestätigt. Nach HA-Neustart ist ein erneuter Quellen-/Fristabgleich erforderlich.')
        if not matched:
            warnings.append('Konfiguration nicht eindeutig über die unterstützte Sammlung bestätigt; keine Neuanlage ableiten.')
        output.append({'entity_id': row['entity_id'], 'name': row['name'], 'platform': platform,
                       'state': 'configuration_read' if matched else 'needs_separate_inspection',
                       'roles': sorted(k for k, ids in roles.items() if row['entity_id'] in ids),
                       'decision': row['decision'], 'config': config, 'warnings': warnings,
                       'ownership': 'existing_not_adopted'})
    return output
