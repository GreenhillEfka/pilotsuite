"""Reference overlap is a review aid, never semantic equivalence or permission."""
from datetime import UTC, datetime


def reference_review(draft, zone_revision, relations):
    targets = set(draft['fields']['target_ids'])
    sources = set(draft['current_pattern']['sources'])
    matches = {}
    for entity, automations in relations.items():
        for automation in automations:
            match = matches.setdefault(automation, {'entity_id': automation,
                'target_references': [], 'source_references': [], 'enabled': 'unknown'})
            if entity in targets: match['target_references'].append(entity)
            if entity in sources: match['source_references'].append(entity)
    items = sorted(matches.values(), key=lambda i: (not bool(i['target_references']), i['entity_id']))
    return {'schema': 'pilotsuite-automation-reference-review-v1',
            'draft_id': draft['id'], 'draft_revision': draft['revision'],
            'zone_id': draft['zone_id'], 'zone_revision': zone_revision,
            'checked_at': datetime.now(UTC).isoformat(),
            'basis': {'target_ids': sorted(targets), 'source_ids': sorted(sources)},
            'state': 'references_found' if items else 'no_references_found',
            'method': 'ha_search_related_entity', 'coverage': 'limited',
            'duplicate_assessment': 'not_determined', 'risk': 'not_assessed',
            'checked_entities': sorted(relations), 'items': items,
            'limitations': ['device_area_label_targets', 'dynamic_templates',
                            'indirect_scripts_groups_scenes', 'conditions_timing_actions',
                            'enabled_state'],
            'execution': {'allowed': False, 'actions': []}}
