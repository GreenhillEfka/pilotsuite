"""Derived review navigation, never an evidence store or an execution gate.

The canonical PlanStore supplies a single draft/zone/report transaction. Explicit
HA review routes may enrich ONLY the last two sections. GET has no HA I/O. Each
section owns its explanation and navigation priority; the UI only combines
same-basis server sections and orders their declared navigation suggestions.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import re

from .review_notes import scope_fingerprint

SCHEMA = 'pilotsuite-review-compass-v1'
CHECK_IDS = ('sources', 'evidence', 'intent', 'automations', 'notes')
MAX_NAVIGATION_AGE_SECONDS = 300
SAFE_INT = 2**53 - 1
FINGERPRINT = re.compile(r'[0-9a-f]{64}')
AUTOMATION = re.compile(r'automation\.[a-z0-9_]{1,244}')
STEPS = {
    'review_sources': (10, 'Quellenübersicht öffnen'),
    'edit_draft': (20, 'Entwurfsangaben prüfen'),
    'review_evidence': (30, 'Beobachtungsgrundlage ansehen'),
    'compare_automations': (40, 'Bestehende Automationen prüfen'),
    'open_matches': (40, 'Treffer für eine Detailprüfung auswählen'),
    'inspect_automation': (35, 'Ausgewählte Automation erneut lesen'),
    'write_note': (50, 'Eigene Bewertung zur Detailprüfung festhalten'),
    'review_limits': (60, 'Offene fachliche Grenzen ansehen'),
}


def _map(value):
    return value if isinstance(value, dict) else {}


def _count(value):
    return value if type(value) is int and 0 <= value <= SAFE_INT else None


def _ids(value):
    if (not isinstance(value, list) or len(value) > 20
            or any(not isinstance(v, str) or not v or len(v) > 255 for v in value)
            or len(value) != len(set(value))):
        return None
    return sorted(value)


def _date(value):
    if not isinstance(value, str):
        return False
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).tzinfo is not None
    except ValueError:
        return False


def _step(identity, automation_id=None):
    priority, label = STEPS[identity]
    result = {'id': identity, 'priority': priority, 'label': label}
    if automation_id is not None:
        if not isinstance(automation_id, str) or not AUTOMATION.fullmatch(automation_id):
            raise ValueError('Invalid navigation automation')
        result['automation_id'] = automation_id
    return result


def _check(identity, title, state, summary, *, facts=None, step=None):
    return {'id': identity, 'title': title, 'state': state, 'summary': summary,
            'facts': facts or [], 'next_step': step}


def _finish(compass):
    steps = [c['next_step'] for c in compass['checks'] if c.get('next_step')]
    compass['next_step'] = min(steps, key=lambda s: (s['priority'], s['id'])) if steps else _step('review_limits')
    compass['execution'] = {'allowed': False, 'reason': 'navigation_only', 'actions': []}
    return compass


def _notes_check(notes, basis, inspection=None):
    """Independent authored dispositions and basis freshness; no global verdict."""
    notes = _map(notes)
    items = notes.get('items', [])
    if not isinstance(items, list) or len(items) > 20:
        items = []
    counts = dict(total=0, open=0, needs_change=0, reviewed=0,
                  stale=0, not_rechecked=0, config_changed=0, matches_last_read=0)
    pending = []
    inspection = _map(inspection)
    for note in items:
        note = _map(note)
        counts['total'] += 1
        disposition = note.get('disposition')
        counts[disposition if disposition in ('open', 'needs_change', 'reviewed') else 'open'] += 1
        if (note.get('stale') is not False or note.get('draft_revision') != basis['draft_revision']
                or note.get('zone_revision') != basis['zone_revision']
                or note.get('scope_fingerprint') != basis['scope_fingerprint']):
            state = 'stale'
        elif (inspection.get('entity_id') == note.get('automation_id')
                and isinstance(note.get('config_fingerprint'), str)
                and FINGERPRINT.fullmatch(note['config_fingerprint'])):
            state = ('matches_last_read' if note['config_fingerprint'] == inspection.get('config_fingerprint')
                     else 'config_changed')
        else:
            state = 'not_rechecked'
        counts[state] += 1
        entity = note.get('automation_id')
        if state != 'matches_last_read' and isinstance(entity, str) and AUTOMATION.fullmatch(entity):
            pending.append(entity)
    facts = [
        {'label': 'Eigene Bewertungen', 'value': f"{counts['open']} offen · {counts['needs_change']} Änderungsbedarf · {counts['reviewed']} manuell geprüft"},
        {'label': 'Bezugsaktualität', 'value': f"{counts['stale'] + counts['config_changed']} verändert · {counts['not_rechecked']} nicht erneut gelesen · {counts['matches_last_read']} passend zum letzten Lesen"},
    ]
    if not items:
        state, summary = 'missing', 'Noch keine eigene Bewertung gespeichert. Eine Bewertung ist keine Ausführungsfreigabe.'
    elif counts['stale'] or counts['config_changed']:
        state, summary = 'stale', 'Mindestens eine Bewertungsgrundlage ist verändert. Eigene Texte bleiben erhalten.'
    elif counts['not_rechecked']:
        state, summary = 'unknown', 'Gespeicherte Bewertungen beweisen nicht den aktuellen HA-Konfigurationsstand.'
    else:
        state, summary = 'last_read', 'Die Bewertungsgrundlagen passen zum letzten ausgewählten Lesen, nicht zu einer laufenden Überwachung.'
    selected = inspection.get('entity_id')
    if isinstance(selected, str) and AUTOMATION.fullmatch(selected):
        selected_note = next((n for n in items if _map(n).get('automation_id') == selected), None)
        needs_authored_review = (not selected_note or selected_note.get('disposition') != 'reviewed'
                                 or selected_note.get('config_fingerprint') != inspection.get('config_fingerprint')
                                 or selected_note.get('stale') is not False)
        step = _step('write_note', selected) if needs_authored_review else (
            _step('inspect_automation', sorted(pending)[0]) if pending else None)
    else:
        step = _step('inspect_automation', sorted(pending)[0]) if pending else None
    result = _check('notes', 'Eigene Bewertungen', state, summary, facts=facts, step=step)
    result['counts'] = counts
    return result


def build_review_compass(draft, inventory, report):
    """Project only already-owned data; no reads, writes, clock or external calls."""
    if (draft.get('zone_id') != inventory.get('zone_id')
            or _count(draft.get('revision')) is None or draft['revision'] < 1
            or _count(inventory.get('revision')) is None):
        raise ValueError('Compass requires a matching canonical draft/zone basis')
    pattern = _map(draft.get('current_pattern'))
    fields, config = _map(draft.get('fields')), _map(report.get('config'))
    sources = _ids(pattern.get('sources'))
    targets = _ids(fields.get('target_ids'))
    notes = _map(draft.get('review_notes'))
    basis = {'zone_id': draft['zone_id'], 'draft_id': draft['id'],
             'draft_revision': draft['revision'], 'zone_revision': inventory['revision'],
             'review_revision': notes.get('revision', 0),
             'source_revision': draft.get('source_revision'),
             'source_ids': sources or [], 'target_ids': targets or [],
             'scope_fingerprint': scope_fingerprint(draft)}
    checks = []
    items = {i['entity_id']: i for i in inventory.get('items', [])
             if isinstance(i, dict) and isinstance(i.get('entity_id'), str)}
    valid_sources = [s for s in sources or [] if items.get(s, {}).get('decision') == 'relevant'
                     and s.startswith('binary_sensor.')
                     and items[s].get('suggested_role') in ('presence', 'motion', 'occupancy')
                     and items[s].get('state') in ('on', 'off')]
    saved_sources = _ids(_map(config.get('roles')).get('presence'))
    if not sources:
        state, summary = 'missing', 'Kein aktueller Musterbezug vorhanden. Der eigene Entwurf bleibt erhalten.'
    elif draft.get('source_status') != 'current' or sources != saved_sources:
        state, summary = 'stale', 'Der gespeicherte Entwurf bezieht sich nicht auf die aktuelle bestätigte Quellenauswahl.'
    elif len(valid_sources) != len(sources):
        state, summary = 'partial', 'Mindestens eine Musterquelle fehlt, ist nicht bestätigt oder in der HA-Projektion nicht auswertbar.'
    else:
        state, summary = 'observed', 'Die bestätigten Musterquellen sind in der gelesenen HA-Projektion auswertbar.'
    checks.append(_check('sources', 'Quellen', state, summary,
        facts=[{'label': 'Auswertbare Musterquellen', 'value': f'{len(valid_sources)} / {len(sources or [])}'},
               {'label': 'Grenze', 'value': 'Keine Prüfung der physischen Messfrische oder lückenloser Erreichbarkeit.'}],
        step=_step('edit_draft') if state == 'stale' else _step('review_sources') if state != 'observed' else None))

    stats = _map(pattern.get('statistics'))
    window = _map(stats.get('window_local'))
    temporal = _map(report.get('reobservation'))
    temporal_windows = temporal.get('windows', [])
    if not isinstance(temporal_windows, list):
        temporal_windows = []
    match = next((t for t in temporal_windows if isinstance(t, dict)
                  and t.get('start_hour') == window.get('start_hour')
                  and t.get('day_group') == stats.get('day_group')
                  and temporal.get('timezone') == stats.get('timezone')), None)
    events, days = _count(stats.get('activation_count')), _count(stats.get('distinct_day_count'))
    coverage = _map(report.get('coverage'))
    facts = []
    if events is not None and days is not None:
        facts.append({'label': 'Im selben lokalen Zeitfenster', 'value': f'{events} Aktivierungen / {days} getrennte Tage'})
    if window and isinstance(stats.get('timezone'), str):
        facts.append({'label': 'Zeitbezug', 'value': f"{window.get('start_hour')}–{window.get('end_hour')} Uhr · {stats['timezone']} · {stats.get('day_group')}"})
    valid_window = (type(window.get('start_hour')) is int and 0 <= window['start_hour'] <= 22
                    and window['start_hour'] % 2 == 0 and window.get('end_hour') == window['start_hour'] + 2
                    and stats.get('day_group') in ('all', 'weekday', 'weekend'))
    valid_temporal = bool(match) and all(_count(match.get(k)) is not None for k in
        ('training_events', 'training_days', 'later_events', 'later_days'))
    if valid_temporal:
        valid_temporal = (match['training_days'] <= match['training_events']
                          and match['later_days'] <= match['later_events']
                          and match['training_events'] + match['later_events'] == events
                          and (match.get('state') != 'reobserved' or match['later_events'] > 0))
    if not pattern or events is None or days is None or not 0 < days <= events or not valid_window:
        state, summary = 'unknown', 'Die aktuelle Beobachtungsgrundlage ist nicht auswertbar. Fehlende Daten sind kein Gegenbeweis.'
    elif not valid_temporal or match.get('state') not in ('reobserved', 'insufficient_earlier_evidence', 'insufficient_later_evidence'):
        state, summary = 'unknown', 'Keine zu diesem Fenster, Tagtyp und Zeitzone passende Nachbeobachtung verfügbar.'
    elif match['state'] == 'insufficient_earlier_evidence':
        state, summary = 'partial', 'Im früheren Abschnitt fehlen Belege zur Musterbildung. Spätere Belege schließen diese Lücke nicht rückwirkend.'
    elif match['state'] == 'insufficient_later_evidence':
        state, summary = 'partial', 'Im späteren Abschnitt fehlen erneute Belege. Eine Beobachtungslücke bleibt möglich.'
    else:
        state, summary = 'observed', 'Erneutes Auftreten im späteren Abschnitt beobachtet. Das belegt weder Prognosegüte noch eine gewünschte Automation.'
    if match:
        facts.append({'label': 'Früher / später', 'value': f"{match.get('training_events')} / {match.get('later_events')} Aktivierungen"})
    slots = _count(coverage.get('sampled_slots'))
    facts.append({'label': 'Beobachtbarkeit (ganze Zone)', 'value':
        'Keine auswertbaren Stichproben; keine Aussage über lückenlose Beobachtung.' if not slots else
        f"{slots} Stichproben; {coverage.get('impaired_slots', 0)} beeinträchtigt. Keine kontinuierliche Sensorabdeckung."})
    facts.append({'label': 'Grenzen', 'value': 'Rollendes 70/30-Fenster; keine unabhängige Vorhersageprüfung. Korrelation ist nicht Kausalität.'})
    if config.get('learning') is not True:
        facts.append({'label': 'Sammlung', 'value': 'Lernen aus: ausschließlich bereits aufbewahrte Belege. Keine neue Zustimmung abgeleitet.'})
    evidence = _check('evidence', 'Beobachtungsgrundlage', state, summary, facts=facts,
                     step=_step('review_evidence') if state != 'observed' else None)
    evidence['period'] = {k: temporal.get(k) for k in ('start', 'end', 'split_at', 'timezone', 'basis')}
    checks.append(evidence)

    missing = [k for k in ('goal', 'trigger', 'conditions', 'manual_override')
               if not isinstance(fields.get(k), str) or not fields[k].strip()]
    if not targets:
        missing.append('target_ids')
    unavailable = set(draft.get('unavailable_targets', []))
    unavailable.update(t for t in targets or [] if items.get(t, {}).get('decision') != 'relevant'
                       or items[t].get('state') in (None, 'unknown', 'unavailable'))
    if missing:
        state, summary = 'missing', 'Gewünschtes Verhalten und Zielauswahl sind noch nicht vollständig beschrieben.'
    elif unavailable:
        state, summary = 'partial', 'Mindestens ein gewähltes Ziel ist nicht mehr bestätigt oder derzeit nicht auswertbar.'
    else:
        state, summary = 'described', 'Ziel, Auslöser, Bedingungen und manueller Vorrang sind beschrieben – noch nicht fachlich nachgewiesen.'
    labels = {'goal': 'Komfortziel', 'trigger': 'Auslöser', 'conditions': 'Bedingungen',
              'manual_override': 'Manueller Vorrang', 'target_ids': 'Zielgeräte'}
    checks.append(_check('intent', 'Dein gewünschtes Ergebnis', state, summary,
        facts=[{'label': 'Fehlende Angaben', 'value': ', '.join(labels[k] for k in missing) or 'Keine Pflichtangabe fehlt.'},
               {'label': 'Zielauswahl', 'value': f'{len(targets or [])} gewählt · {len(unavailable)} ungeklärt'}],
        step=_step('edit_draft') if state != 'described' else None))
    checks.append(_check('automations', 'Bestehende Automationen', 'unknown',
        'Noch kein passender ausdrücklicher Vergleich in dieser Ansicht. GET liest keine HA-Konfiguration.',
        step=_step('compare_automations')))
    checks.append(_notes_check(notes, basis))
    return _finish({'schema': SCHEMA, 'basis': basis, 'checks': checks,
                    'comparison_checked_at': None, 'navigation_max_age_seconds': MAX_NAVIGATION_AGE_SECONDS})


def _valid_review(basis, report):
    return (report.get('schema') == 'pilotsuite-automation-reference-review-v1'
            and report.get('execution') == {'allowed': False, 'actions': []}
            and report.get('draft_id') == basis['draft_id'] and report.get('zone_id') == basis['zone_id']
            and report.get('draft_revision') == basis['draft_revision']
            and report.get('zone_revision') == basis['zone_revision']
            and report.get('basis') == {'source_ids': basis['source_ids'], 'target_ids': basis['target_ids']}
            and _date(report.get('checked_at')))


def with_automation_review(compass, draft, report):
    """Only server-created bounded reports; never accept these from HTTP clients."""
    result = deepcopy(compass)
    if not _valid_review(result['basis'], report):
        return result
    items = report.get('items')
    if (not isinstance(items, list) or len(items) > 100
            or any(not isinstance(_map(i).get('entity_id'), str)
                   or not AUTOMATION.fullmatch(i['entity_id']) for i in items)):
        return result
    detail = _map(report.get('inspection'))
    valid_detail = (isinstance(detail.get('entity_id'), str)
                    and AUTOMATION.fullmatch(detail['entity_id'])
                    and any(_map(i).get('entity_id') == detail['entity_id'] for i in items)
                    and isinstance(detail.get('config_fingerprint'), str)
                    and FINGERPRINT.fullmatch(detail['config_fingerprint']))
    if detail and not valid_detail:
        return result
    if valid_detail:
        summary = 'Eine ausgewählte Automation wurde strukturell gelesen. Gleichwertigkeit, Auswirkungen und Ausführung bleiben ungeprüft.'
        state, step = 'last_read', None
    elif items:
        summary = 'Direkte Entitätsbezüge gefunden. Wähle einen Treffer für die ausdrücklich begrenzte Detailprüfung.'
        state, step = 'partial', _step('open_matches')
    else:
        summary = 'Keine direkten Entitätsbezüge gefunden. Indirekte oder dynamische Abläufe bleiben ungeklärt; kein Nachweis von Konfliktfreiheit.'
        state, step = 'limited', _step('review_limits')
    result['checks'][3] = _check('automations', 'Bestehende Automationen', state, summary,
        facts=[{'label': 'Direkte Treffer', 'value': str(len(items))},
               {'label': 'Zuletzt ausdrücklich gelesen', 'value': report['checked_at']},
               {'label': 'Umfang', 'value': 'Eine ausgewählte Struktur.' if valid_detail else 'Begrenzte direkte Entitätsbezüge.'}], step=step)
    result['checks'][4] = _notes_check(draft.get('review_notes'), result['basis'], detail if valid_detail else None)
    result['comparison_checked_at'] = report['checked_at']
    result['inspection_basis'] = {'automation_id': detail.get('entity_id'),
                                  'config_fingerprint': detail.get('config_fingerprint')}
    # Saved notes remain separate; this projection contains counts, not private text.
    return _finish(result)


def with_saved_notes(compass, notes, report):
    """Refresh a save receipt only after the existing atomic revision/age guard."""
    if compass is None:
        return None
    result = deepcopy(compass)
    revision = _count(_map(notes).get('revision'))
    if (revision is None or revision != result['basis']['review_revision'] + 1
            or not _valid_review(result['basis'], report)):
        return result
    result['basis']['review_revision'] = revision
    result['checks'][4] = _notes_check(notes, result['basis'], _map(report.get('inspection')))
    return _finish(result)
