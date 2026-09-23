"""Read-only setup guidance derived from canonical zone and learning projections."""
from copy import deepcopy


def zone_guide(inventory, report, status, summary):
    steps = []

    def add(key, state, title, detail, target):
        steps.append(dict(id=key, state=state, title=title, detail=detail, target=target))

    relevant = sum(i['decision'] == 'relevant' for i in inventory['items'])
    missing = sum(i['decision'] == 'relevant' for i in inventory['missing'])
    add('scope', 'complete' if inventory['resolved'] else 'attention',
        'Zonenquellen', 'Bereiche und zusätzliche Quellen sind aufgelöst.' if inventory['resolved'] else
        'Mindestens ein Bereich fehlt oder die Zone hat keine auflösbare Quelle.', 'zone-setup')
    add('selection', 'complete' if relevant and not missing else 'attention', 'Bewusste Auswahl',
        f'{relevant} aktuell vorhandene Entitäten bestätigt; {missing} bestätigte Quellen fehlen. '
        'Ungeprüfte Entitäten bleiben ausgeschlossen.', 'entity-details')
    add('evaluation', 'complete' if inventory['enabled'] else 'paused', 'Zonenauswertung',
        'Auswertung ist aktiviert.' if inventory['enabled'] else
        'Die Zone ist pausiert. Einstellungen bleiben erhalten.', 'zone-overview')
    add('connection', 'complete' if status['ready'] else 'attention', 'Datenverbindung',
        'Ereignisstrom und Snapshot sind bereit; dies bestätigt keine physische Sensorfrische.' if status['ready'] else
        'HA-Verbindung oder Snapshot ist nicht bereit. Zuerst den Systemstatus prüfen.', 'zone-overview')

    roles = report['config']['roles']
    presence = summary.get('presence', {})
    selected = roles.get('presence', [])
    source_state = ('optional' if not selected else 'paused' if not inventory['enabled'] else
                    'complete' if presence.get('status') == 'available' else 'attention')
    add('presence', source_state, 'Präsenzgruppe für optionales Lernen',
        'Keine Präsenzgruppe gespeichert. Reine Zonenbeobachtung funktioniert auch ohne Lernen.' if not selected else
        'Quellenprüfung pausiert mit der Zone.' if not inventory['enabled'] else
        f"{presence.get('valid', 0)} von {len(selected)} gespeicherten Quellen auswertbar. "
        'Fehlende oder ungültige Quellen bedeuten keine Abwesenheit.', 'learning-section')
    learning = report['config']['learning']
    add('consent', 'complete' if learning else 'optional', 'Lernfreigabe',
        'Freigabe ist gespeichert. Sie erlaubt keine Geräteaktionen.' if learning else
        'Lernen ist ausgeschaltet. Du kannst bei reiner Beobachtung bleiben oder es bewusst freigeben.', 'learning-section')

    patterns = report.get('patterns', [])
    windows = report.get('progress', {}).get('windows', [])
    # Never pool events/days from unrelated local windows or invent an arrival date.
    nearest = min(windows, key=lambda w: (w['missing_days'], w['missing_events'], w['start_hour'], w.get('day_group', 'all')), default=None)
    if patterns:
        detail = f'{len(patterns)} aktuelle Muster zur Prüfung; eine Bewertung ist keine Schaltfreigabe.'
        if not learning:
            detail += ' Sie beruhen auf aufbewahrten Belegen; neue Sammlung ist ausgeschaltet.'
        evidence_state = 'review'
    elif not learning:
        detail, evidence_state = 'Ohne Lernfreigabe werden keine neuen Aktivierungen gesammelt.', 'optional'
    elif report['collection_state'] != 'collecting':
        detail, evidence_state = 'Neue Sammlung ist derzeit nicht bereit. Vorhandene Belege bleiben getrennt davon erhalten.', 'attention'
    elif nearest:
        group = {'all': 'alle Tage', 'weekday': 'Mo–Fr', 'weekend': 'Sa–So'}[nearest.get('day_group', 'all')]
        detail = (f"Im Fenster {nearest['start_hour']:02d}–{nearest['end_hour']:02d} Uhr "
                  f"({report.get('time_basis', 'UTC')}, {group}) fehlen mindestens "
                  f"{nearest['missing_events']} Aktivierungen und {nearest['missing_days']} weitere Beobachtungstage. "
                  'Andere Zeitfenster werden nicht addiert. Kein vorhergesagtes Fertigdatum.')
        evidence_state = 'waiting'
    else:
        detail, evidence_state = 'Sammlung ist bereit, aber noch ohne Belege. Auf frische Aktivierungen warten; keine Aktivierung künstlich erzeugen.', 'waiting'
    add('evidence', evidence_state, 'Muster prüfen', detail, 'pattern-workbench')
    actionable = next((s for s in steps if s['state'] in ('attention', 'paused')), None)
    next_step = actionable or next((s for s in steps if s['state'] == 'review'), None) or steps[-1]
    return deepcopy({'schema': 'pilotsuite-zone-guide-v1', 'steps': steps, 'next_step': next_step,
                     'nearest_window': nearest, 'selection': {'relevant': relevant, 'missing_relevant': missing},
                     'learning_optional': True, 'execution_allowed': False,
                     'basis': 'current_configuration_and_retained_evidence_not_acceptance'})
