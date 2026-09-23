"""Derived review briefs; never an execution plan or another evidence store."""
from copy import deepcopy


def review_brief(pattern, report):
    """Keep preference, observation, rule strength and permission independent."""
    stats = pattern['statistics']
    window = stats['window_local']
    context = next((item for item in report.get('context_windows', [])
                    if item['start_hour'] == window['start_hour']
                    and item['day_group'] == stats['day_group']), None)
    preference = pattern.get('preference')
    state = {'accepted': 'review_requested', 'rejected': 'dismissed',
             'later': 'deferred'}.get(preference, 'unreviewed')
    warnings = ['Aktivierungen belegen keine Anwesenheitsdauer oder Schaltursache.',
                'Bestehende Automationen wurden noch nicht auf Überschneidung geprüft.']
    coverage = report.get('coverage', {})
    reobservation = report.get('reobservation', {})
    temporal = next((item for item in reobservation.get('windows', [])
                     if item['start_hour'] == window['start_hour']
                     and item['day_group'] == stats['day_group']), None)
    temporal_check = ({**temporal, **{key: reobservation[key] for key in
                       ('start', 'end', 'split_at', 'timezone', 'basis', 'limitations')}}
                      if temporal else None)
    if temporal_check:
        warnings.append('Zeitprüfung verwendet frühere 70 % und spätere 30 % des Aufbewahrungsfensters; '
                        'erneutes Auftreten ist keine Prognosegüte und keine unabhängige Live-Validierung.')
        if temporal_check['state'] == 'insufficient_earlier_evidence':
            warnings.append('Im früheren Abschnitt reichen die Belege nicht zur Musterbildung; '
                            'spätere Belege dürfen diese Schwelle nicht rückwirkend erfüllen.')
        elif temporal_check['state'] == 'insufficient_later_evidence':
            warnings.append('Keine späteren Belege im selben Fenster; das kann eine Beobachtungslücke sein.')
    if not coverage.get('sampled_slots'):
        warnings.append('Keine Beobachtbarkeitsstichproben vorhanden.')
    elif coverage.get('impaired_slots') or coverage.get('unobserved_slots_between_checks'):
        warnings.append('Die Zonenbeobachtung enthält Einschränkungen oder unbeobachtete Abschnitte.')
    if not report['config'].get('learning'):
        warnings.append('Lernfreigabe ist ausgeschaltet; dies sind aufbewahrte Belege.')
    nodes = [dict(id='source-'+str(i), kind='source', label=source)
             for i, source in enumerate(pattern['sources'])]
    nodes += [dict(id='observations', kind='statistics', label=f"{stats['activation_count']} Aktivierungen / {stats['distinct_day_count']} Tage"),
              dict(id='rule', kind='rule', label=pattern['algorithm']),
              dict(id='review', kind='review', label='Routine gemeinsam prüfen')]
    edges = [{'from': node['id'], 'to': 'observations'} for node in nodes if node['kind'] == 'source']
    edges += [{'from': 'observations', 'to': 'rule'}, {'from': 'rule', 'to': 'review'}]
    return deepcopy({
        'schema': 'pilotsuite-review-v1', 'pattern_id': pattern['id'],
        'title': pattern['title'], 'state': state, 'preference': preference,
        'statistics': stats, 'rule_strength': pattern['rule_strength'],
        'confidence': pattern['confidence'], 'risk': 'read_only',
        'algorithm': pattern['algorithm'], 'parameters': pattern['parameters'],
        'sources': pattern['sources'], 'context': context,
        'coverage': coverage, 'coverage_scope': 'whole_zone_retention_window',
        'temporal_check': temporal_check,
        'evidence_graph': {'nodes': nodes, 'edges': edges}, 'warnings': warnings,
        'next_steps': [
            'Gewünschten Komfort, Zielgeräte und zulässige Werte festlegen.',
            'Vorhandene HA-Automationen und Skripte auf Überschneidungen prüfen.',
            'Trigger, Bedingungen, Vorrang manueller Bedienung und Rückweg prüfen.',
            'Einen konkreten Entwurf separat freigeben, sichern und verifizieren.'],
        'execution': {'allowed': False, 'reason': 'review_only', 'actions': []},
    })
