"""Configuration progress from existing owners; never a claim of live acceptance."""
from __future__ import annotations


def setup_journey(foundation, *, config=None, inventory=None, imported_automations=()):
    config = config or {}
    inventory = inventory or {}
    structure = config.get('zone_structure') or {}
    presence = config.get('zone_presence_v2') or {}
    spec = presence.get('spec') if isinstance(presence.get('spec'), dict) else {}
    sources = spec.get('sources') if isinstance(spec.get('sources'), list) else []
    package = presence.get('package') or {}
    bindings = (foundation.get('organization') or {}).get('assignments', {})
    existing = bindings.get('presence_output', [])
    relevant = sum(row.get('decision') == 'relevant' for row in inventory.get('items', []))
    missing = sum(row.get('decision') == 'relevant' for row in inventory.get('missing', []))
    steps = []

    def add(key, title, state, summary, action=None):
        steps.append({'id':key, 'title':title, 'state':state, 'summary':summary, 'action':action})

    if structure.get('label_id'):
        add('zone', 'Zone & Tags', 'configured',
            f"Zonenlabel verbunden; {len(structure.get('members', {}))} Mitglieder gespeichert. HA-Abgleich ausdrücklich prüfen.", 'zone')
    elif structure.get('label_name'):
        add('zone', 'Zone & Tags', 'attention',
            'Neues Zonenlabel „'+structure['label_name']+'“ geplant. Label und Mitglieder gemeinsam abgleichen.', 'labels')
    else:
        add('zone', 'Zone & Tags', 'attention',
            'Bereiche und Zusatzentitäten mit einem vorhandenen oder neuen Zonenlabel verbinden.', 'zone')

    if sources:
        state, action = 'configured', 'presence'
        summary = 'Die aktuelle Gültigkeit zeigt der Zonenstatus; Speicherung allein ist kein Anwesenheitsbeleg.'
        if not inventory.get('enabled'):
            state, action = 'paused', 'evaluation'
            summary = 'Die gesamte Zone ist pausiert. Den Start der Auswertung in der Einrichtung prüfen. '
            if presence.get('mode') == 'publish':
                summary += 'Beim Start gilt die gespeicherte Veröffentlichung in das eigene HA-Ausgangspaket.'
            elif presence.get('mode') == 'paused':
                summary += 'Das Präsenzmodul bleibt danach separat pausiert.'
            else:
                summary += 'Der gespeicherte Vergleich verändert keine HA-Steuerung.'
        elif presence.get('mode') == 'paused':
            state = 'paused'
            summary = 'Das Präsenzmodul ist pausiert; die Zone selbst ist für Auswertung aktiv. Betriebsart im Präsenzeditor prüfen.'
        add('presence', 'Präsenz & Nachlauf', state,
            f"{len(sources)} Quellen und Nachlauf gespeichert. " + summary, action)
    else:
        add('presence', 'Präsenz & Nachlauf', 'attention',
            f'{relevant} relevante Entitäten; {missing} bestätigte Quellen fehlen. '
            'Passende Präsenzquellen werden im Editor vorbefüllt. Nachlauf und Quellen dort einmal speichern.', 'presence' if relevant else 'entities')

    if package:
        add('output', 'Status in Home Assistant', 'configured',
            'Eigenes Ausgangspaket angelegt. '+('Veröffentlichung gewählt; laufende Bestätigung im Zonenstatus prüfen.' if presence.get('mode')=='publish' else
             'Veröffentlichung ist aus; der Vergleich verändert die bestehende Steuerung nicht.'), 'presence')
    elif existing:
        unresolved = any(not row.get('entity_id') or row.get('disabled') for row in existing)
        add('output', 'Status in Home Assistant', 'attention' if unresolved else 'configured',
            'Gespeicherter Bestandsstatus nicht eindeutig aufgelöst; keinen Ersatz anlegen.' if unresolved else
            'Vorhandener öffentlicher Präsenzsensor zugeordnet. Seine bestehende Steuerung bleibt zuständig.', 'existing')
    else:
        add('output', 'Status in Home Assistant', 'unverified',
            'Vorhandenen Zonenstatus verbinden oder ein eigenes Helfer-/Sensorpaket gemeinsam prüfen. Anlage und Veröffentlichung sind getrennte Schritte.', 'existing')

    lighting = foundation.get('modules', {}).get('lighting', {})
    light_config = config.get('zone_lighting') or {}
    if light_config.get('spec'):
        add('lighting', 'Licht', 'paused' if light_config.get('mode')=='paused' else 'configured',
            'Lichtvergleich gespeichert. Nutzt die eigene Zonenpräsenz; vorhandene HA-Lichtsteuerung bleibt zuständig.', 'lightmodule')
    else:
        add('lighting', 'Licht', 'planned' if lighting.get('lights') else 'attention',
            'Lichtquellen zugeordnet. Auf der geklärten Präsenz zunächst Lichtverhalten prüfen; noch keine neue Steuerung.' if lighting.get('lights') else
            'Leuchten und unabhängige Helligkeitsquelle zuordnen. Präsenz, manuelle Bedienung und vorhandene Lichtregeln bleiben maßgeblich.', 'lightmodule' if lighting.get('lights') and sources else 'lighting')
    add('later', 'Später erweitern', 'planned',
        'Klima, Multimedia und Mustererkennung folgen nach der Grundkonfiguration. Sie blockieren die Zoneneinrichtung nicht.')
    actionable = next((step for step in steps if step['state'] in ('attention','paused','unverified')), steps[3])
    return {'schema':'pilotsuite-zone-setup-journey-v2', 'steps':steps, 'next_step':actionable,
            'basis':'saved_configuration_not_household_acceptance',
            'principles':['progressive_disclosure','explain_before_apply','reuse_before_create',
                          'one_responsible_control_path','manual_override_first'],
            'execution':{'allowed':False,'actions':[]}}
