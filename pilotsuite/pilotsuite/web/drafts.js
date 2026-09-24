// User-authored drafts and explicit read-only review. No execution or automatic saves.
let routineEditor = null;
let routineDirty = false;
let routineComparison = null;

function comparisonFor(draft) {
  const result = routineComparison;
  if (!result || result.zone_id !== selectionZone || result.draft_id !== draft.id
      || result.draft_revision !== draft.revision || result.zone_revision !== contextData?.revision
      || draft.source_status !== 'current' || draft.unavailable_targets.length
      || JSON.stringify(result.basis.source_ids) !== JSON.stringify([...(draft.current_pattern?.sources || [])].sort())) return null;
  return result;
}

function appendComparison(card, draft) {
  const result = comparisonFor(draft);
  if (!result) return;
  const panel = document.createElement('div'); panel.className = 'routine-comparison';
  const heading = document.createElement('h5');
  heading.textContent = result.items.length ? 'Mögliche Überschneidungen' : 'Keine direkten Entitätsbezüge gefunden';
  const detail = document.createElement('p');
  detail.textContent = `Momentaufnahme ${new Date(result.checked_at).toLocaleString()}. ${result.checked_entities.length} Entitäten geprüft. Gleiche Bezüge beweisen keine doppelte Automation; kein Treffer beweist keine Konfliktfreiheit. Geräte-/Bereichs-/Label-Ziele, dynamische Templates und indirekte Aufrufe sind nicht vollständig erfasst. Bedingungen, Aktionen, Zeitverhalten und Aktivierungsstatus sind ungeprüft. Risiko und Ausführung bleiben ungeprüft bzw. gesperrt.`;
  panel.append(heading, detail);
  for (const item of result.items) {
    const row = document.createElement('p');
    row.textContent = `${item.entity_id} · Zielbezüge: ${item.target_references.join(', ') || 'keine'} · Quellenbezüge: ${item.source_references.join(', ') || 'keine'} · Aktivierungsstatus ungeprüft`;
    panel.append(row);
    const inspect = document.createElement('button'); inspect.type = 'button';
    inspect.textContent = `Details prüfen: ${item.entity_id}`;
    inspect.disabled = selectionBusy || contextEditing || zoneFormOpen || !!selectionDraft?.dirty;
    inspect.addEventListener('click', () => compareRoutine(draft, item.entity_id)); panel.append(inspect);
  }
  if (result.inspection) appendInspection(panel, result.inspection, draft);
  card.append(panel);
}

function appendInspection(panel, inspection, draft) {
  const root = document.createElement('section'); root.className = 'automation-inspection';
  const h = document.createElement('h5'); h.textContent = `Detailprüfung · ${inspection.entity_id}`;
  const changes = {first_read:'Erste Detailprüfung.',unchanged:'Konfiguration seit der letzten Detailprüfung unverändert.',changed:'Konfiguration seit der letzten Detailprüfung geändert – erneut fachlich prüfen.'};
  const note = document.createElement('p'); note.textContent = `${changes[inspection.change_status]} Nur Aufbau und direkte Bezüge geprüft. Werte, Nachrichten und Templates werden nicht ausgewertet oder angezeigt. Keine Aussage über tatsächliche Ausführung, Gleichwertigkeit oder Sicherheit.`;
  root.append(h,note);
  const kinds = {state:'Zustand',numeric_state:'Zahlenwert',time:'Zeit',time_pattern:'Zeitraster',sun:'Sonne',event:'Ereignis',homeassistant:'HA-Start/Stopp',zone:'Zone',template:'Template',device:'Gerät',mqtt:'MQTT',calendar:'Kalender',webhook:'Webhook',tag:'Tag',geo_location:'Standort',trigger:'Auslöserbezug',and:'Alle Bedingungen',or:'Mindestens eine Bedingung',not:'Verneinung',service_call:'Dienstaufruf',choose:'Verzweigung',if:'Wenn/Dann',repeat:'Wiederholung',parallel:'Parallel',sequence:'Abfolge',delay:'Verzögerung',wait_template:'Template abwarten',wait_for_trigger:'Ereignis abwarten',variables:'Variablen',stop:'Abbruch',unsupported:'Nicht aufgeschlüsselt'};
  for (const [key,title] of [['triggers','Auslöser'],['conditions','Bedingungen'],['actions','Aktionen']]) {
    const heading = document.createElement('h6'); heading.textContent = title; root.append(heading);
    const list = document.createElement('ul');
    for (const step of inspection.sections[key]) {
      const row = document.createElement('li');
      row.textContent = `${kinds[step.kind] || 'Unbekannt'}${step.service ? ' · '+step.service : ''} · Quellen: ${step.source_references.join(', ') || 'keine direkten'} · Ziele: ${step.target_references.join(', ') || 'keine direkten'}${step.other_reference_count ? ' · weitere Bezüge: '+step.other_reference_count : ''}${step.limitations.length ? ' · offen/nicht vollständig ausgewertet' : ''}`;
      list.append(row);
    }
    if (!list.children.length) { const li=document.createElement('li');li.textContent='Keine aufgeschlüsselten Einträge.';list.append(li); }
    root.append(list);
  }
  const warnings = document.createElement('p');
  warnings.textContent = inspection.limitations.length ? 'Offene Grenzen: '+inspection.limitations.map(k=>({templates_not_evaluated:'Templates nicht ausgewertet',blueprint_not_expanded:'Blueprint nicht aufgelöst',unsupported_structure:'Unbekannter Aufbau',dynamic_or_invalid_entity_reference:'Dynamischer/unbekannter Entitätsbezug',indirect_target_not_resolved:'Geräte-/Bereichs-/Labelziel nicht aufgelöst',indirect_call_not_expanded:'Indirekter Aufruf nicht aufgelöst',unsupported_step:'Unbekannter Schritt',disabled_step:'Deaktivierter Schritt enthalten',dynamic_enablement:'Aktivierung dynamisch',ambiguous_section_aliases:'Mehrdeutige Abschnittsangaben'})[k] || 'Unbekanntes Verhalten').join('; ') : 'Keine zusätzlichen Strukturgrenzen erkannt. Verhalten und Risiko bleiben ungeprüft.';
  root.append(warnings);
  const alignment=document.createElement('p');alignment.textContent=`Musterquellen in Auslösern: ${inspection.alignment.source_trigger_references.join(', ') || 'keine direkten erkannt'}. Zielgeräte in Dienstaufrufen: ${inspection.alignment.target_action_references.join(', ') || 'keine direkten erkannt'}. Dies bewertet die Bezüge, nicht die Wirkung oder Gleichwertigkeit.`;root.append(alignment);
  const heading=document.createElement('h6');heading.textContent='Dein Prüfplan';root.append(heading);
  const labels={source_gap:'Musterquellen ohne direkten Auslöserbezug prüfen',target_gap:'Zielgeräte ohne direkten Dienstaufruf prüfen; indirekte Wirkung bleibt möglich',unknowns:'Unbekannte/dynamische Abläufe in HA klären',intent:'Komfortziel mit bestehendem Verhalten vergleichen',timing:'Zeitfenster, Auslöserwerte und Bedingungen in HA prüfen',manual_override:'Ausnahmen und Vorrang manueller Bedienung nachweisen',enabled:'Aktuellen Aktivierungsstatus in HA prüfen',risk:'Auswirkungen und Rückweg gesondert bewerten'};
  const plan=document.createElement('ol');
  for(const item of inspection.checklist) {const li=document.createElement('li');li.textContent=(labels[item.id] || 'Fachlich prüfen')+' · offen';plan.append(li);}
  const intent=document.createElement('p');intent.textContent=`Deine Angaben: Komfortziel ${draft.fields.goal ? 'vorhanden' : 'fehlt'}, manueller Vorrang ${draft.fields.manual_override ? 'vorhanden' : 'fehlt'}. Eigene Angaben sind noch kein Nachweis, dass die bestehende Automation sie erfüllt.`;
  root.append(plan,intent);panel.append(root);
}

async function compareRoutine(draft, automationId = null) {
  if (selectionBusy || contextEditing || zoneFormOpen || selectionDraft?.dirty) return;
  const zone = selectionZone, zoneRevision = contextData.revision;
  const previous = comparisonFor(draft)?.inspection;
  const payload = {revision:draft.revision,zone_revision:zoneRevision};
  if (automationId) Object.assign(payload,{automation_id:automationId,previous_fingerprint:previous?.entity_id===automationId ? previous.config_fingerprint : null});
  routineComparison = null; selectionBusy = true; contextGeneration++;
  renderSelection(); renderLearning(); text('routine-message', 'Bestehende Automationen werden ausschließlich lesend auf Entitätsbezüge geprüft …');
  try {
    const result = await json(`api/v1/zones/${encodeURIComponent(zone)}/drafts/${encodeURIComponent(draft.id)}/${automationId ? 'automation-inspection' : 'automation-review'}`,
      {method:'POST',body:JSON.stringify(payload)});
    if (zone !== selectionZone) return;
    if (!await loadContext()) return;
    routineComparison = result;
    const current = contextData?.drafts?.find(d => d.id === draft.id);
    if (!current || !comparisonFor(current)) {
      routineComparison = null; text('routine-message', 'Entwurf oder Bezug inzwischen geändert. Vergleich erneut starten.'); return;
    }
    text('routine-message', 'Bezugsprüfung abgeschlossen. Fachliche Prüfung bleibt offen; nichts verändert.');
  } catch(error) { if (zone === selectionZone) text('routine-message', `Vergleich nicht bestätigt: ${error.message}. Kein Ergebnis als konfliktfrei gewertet.`); }
  finally { selectionBusy = false; renderSelection(); renderLearning(); }
}
const routineKeys = ['title', 'goal', 'trigger', 'conditions', 'exceptions', 'manual_override'];
const routineLabels = {goal:'Komfortziel', trigger:'Auslöser', conditions:'Bedingungen', manual_override:'Vorrang manueller Bedienung', target_ids:'Zielgeräte'};

function routineStatus(draft) {
  const source = {current:'Musterbezug aktuell', zone_changed:'Zoneneinstellungen geändert – Bezug erneut prüfen', pattern_missing:'Muster nicht mehr belegt – Entwurf bleibt erhalten'};
  const state = {incomplete:'Unvollständig', needs_review:'Erneut prüfen', ready_for_review:'Angaben vollständig – fachliche Prüfung offen'};
  return `${state[draft.state]}. ${source[draft.source_status]}. Fehlend: ${draft.missing_fields.map(k => routineLabels[k] || k).join(', ') || 'keine Pflichtangaben'}${draft.unavailable_targets.length ? '. Nicht mehr bestätigte/verfügbare Ziele: ' + draft.unavailable_targets.join(', ') : ''}. ${comparisonFor(draft) ? 'Entitätsbezüge geprüft; fachlicher Automationsvergleich' : 'Automationsvergleich'} und Ausführungsrisiko: ungeprüft.`;
}

function renderRoutineDrafts() {
  const root = byId('routine-list');
  // Rebuild current information and restore keyboard focus by stable draft/control
  // identity. Never rerender from focusout: that can remove a pointer's target
  // between mousedown and click. Editors live outside the list and stay untouched.
  const active = document.activeElement;
  const activeCard = active?.closest('#routine-list > article');
  const focus = activeCard && ['BUTTON','SUMMARY'].includes(active.tagName)
    ? {id:activeCard.dataset.draftId,tag:active.tagName.toLowerCase(),label:active.textContent} : null;
  root.replaceChildren();
  const allDrafts = contextData?.drafts || [];
  const drafts = globalThis.PilotSuiteReviewCompass?.workspace(root, allDrafts) || allDrafts;
  if (!drafts.length) { root.textContent = allDrafts.length ? 'Kein Entwurf passt zu diesem Filter.' : 'Noch keine gespeicherten Entwürfe in dieser Zone.'; return; }
  for (const draft of drafts) {
    const card = document.createElement('article'); card.className = 'suggestion'; card.dataset.draftId = draft.id;
    const title = document.createElement('h4'); title.textContent = draft.fields.title;
    const detail = document.createElement('p'); detail.textContent = `${routineStatus(draft)} Revision ${draft.revision}.`;
    card.append(title, detail);
    globalThis.PilotSuiteReviewCompass?.render(card, draft);
    for (const [label, handler] of [['Entwurf bearbeiten', () => openRoutineEditor(draft)],
      ['Entwurf exportieren', () => exportRoutine(draft)], ['Bestehende Automationen prüfen', () => compareRoutine(draft)], ['Entwurf löschen', () => deleteRoutine(draft)]]) {
      const button = document.createElement('button'); button.type = 'button'; button.textContent = label;
      button.disabled = contextEditing || selectionBusy || zoneFormOpen || !!selectionDraft?.dirty;
      if (label === 'Bestehende Automationen prüfen') button.disabled ||= draft.source_status !== 'current' || !!draft.unavailable_targets.length || !draft.fields.target_ids.length;
      button.addEventListener('click', handler); card.append(button);
    }
    appendComparison(card, draft);
    if (typeof appendReviewNotes === 'function') appendReviewNotes(card, draft);
    root.append(card);
  }
  if (focus) {
    const card = [...root.children].find(item => item.dataset.draftId === focus.id);
    const control = card && [...card.querySelectorAll(focus.tag)].find(item => item.textContent === focus.label && !item.disabled);
    if (control) control.focus({preventScroll:true});
    else if (card) { card.tabIndex = -1; card.focus({preventScroll:true}); }
  }
}

function openRoutineEditor(draft) {
  if (contextEditing || selectionBusy || zoneFormOpen || selectionDraft?.dirty) return;
  contextGeneration++; // Invalidate reads that began before editing.
  contextEditing = true;
  routineEditor = {draft, zone:selectionZone, zoneRevision:contextData.revision};
  routineDirty = false;
  byId('routine-form').hidden = false;
  for (const key of routineKeys) byId('routine-' + key).value = draft.fields[key];
  byId('routine-refresh-source').checked = false;
  byId('routine-refresh-source').disabled = !draft.current_pattern;
  const pattern = draft.current_pattern;
  text('routine-source', `${routineStatus(draft)} ${pattern ? 'Aktueller Bezug: ' + pattern.title + '. Quellen: ' + pattern.sources.join(', ') : 'Belege werden nicht im Entwurf kopiert.'}`);
  const targets = byId('routine-targets'); targets.replaceChildren();
  const candidates = contextData.draft_target_candidates || [];
  const ids = [...new Set([...candidates.map(i => i.entity_id), ...draft.fields.target_ids])];
  for (const id of ids) {
    const item = candidates.find(i => i.entity_id === id);
    const label = document.createElement('label'), input = document.createElement('input');
    input.type = 'checkbox'; input.value = id; input.checked = draft.fields.target_ids.includes(id);
    label.append(input, document.createTextNode(`${item?.name || id} · ${id}${item ? '' : ' · nicht mehr bestätigt/verfügbar'}`)); targets.append(label);
  }
  if (!ids.length) targets.textContent = 'Keine bestätigten Zielgeräte vorhanden. Entwurf kann unvollständig gespeichert werden.';
  renderSelection(); renderLearning();
  byId('routine-form').scrollIntoView({block:'start'}); byId('routine-title').focus();
}

function closeRoutineEditor() {
  if (routineEditor) contextEditing = false;
  routineEditor = null; routineDirty = false;
  byId('routine-form').hidden = true;
}

async function createRoutineDraft(patternId) {
  if (selectionBusy || contextEditing || zoneFormOpen || selectionDraft?.dirty) return;
  const zone = selectionZone, revision = contextData.revision;
  selectionBusy = true; contextGeneration++; renderSelection(); renderLearning();
  let draft;
  try {
    draft = await json(`api/v1/zones/${encodeURIComponent(zone)}/drafts`, {method:'POST', body:JSON.stringify({pattern_id:patternId, zone_revision:revision})});
    if (zone !== selectionZone) return;
    if (!await loadContext()) { draft = null; return; }
    text('routine-message', 'Entwurf gespeichert. Ziele und gewünschtes Verhalten ergänzen.');
  } catch (error) { draft = null; if (zone === selectionZone) text('routine-message', `Anlegen nicht bestätigt: ${error.message}. Neu laden zeigt, ob der Entwurf gespeichert wurde.`); }
  finally { selectionBusy = false; renderSelection(); renderLearning(); }
  if (draft && zone === selectionZone) openRoutineEditor(draft);
}

byId('routine-form').addEventListener('input', () => { routineDirty = true; });
byId('routine-form').addEventListener('change', () => { routineDirty = true; });
byId('routine-form').addEventListener('submit', async event => {
  event.preventDefault();
  if (!routineEditor || selectionBusy) return;
  const {draft, zone, zoneRevision} = routineEditor;
  const fields = Object.fromEntries(routineKeys.map(k => [k, byId('routine-'+k).value]));
  fields.target_ids = [...byId('routine-targets').querySelectorAll('input:checked')].map(i => i.value);
  const payload = {revision:draft.revision, zone_revision:zoneRevision, fields, refresh_source:byId('routine-refresh-source').checked};
  selectionBusy = true; contextGeneration++; byId('routine-fields').disabled = true; renderSelection();
  try {
    await json(`api/v1/zones/${encodeURIComponent(zone)}/drafts/${encodeURIComponent(draft.id)}`, {method:'PATCH', body:JSON.stringify(payload)});
    if (zone !== selectionZone) return;
    closeRoutineEditor(); await loadContext(); text('routine-message', 'Entwurf gespeichert. Keine Automation erstellt oder aktiviert.');
  } catch (error) { if (zone === selectionZone) text('routine-message', `Speichern nicht bestätigt: ${error.message}. Deine Eingaben bleiben geöffnet. Bei Konflikt gespeicherten Stand neu laden.`); }
  finally { selectionBusy = false; byId('routine-fields').disabled = false; renderSelection(); renderLearning(); }
});

byId('routine-cancel').addEventListener('click', () => {
  if (selectionBusy || (routineDirty && !confirm('Ungespeicherte Änderungen am Entwurf verwerfen?'))) return;
  closeRoutineEditor(); renderSelection(); renderLearning();
});
byId('routine-reload').addEventListener('click', async () => {
  if (!routineEditor || selectionBusy || (routineDirty && !confirm('Eigene ungespeicherte Eingaben verwerfen und gespeicherten Stand laden?'))) return;
  const id = routineEditor.draft.id, zone = routineEditor.zone;
  selectionBusy = true; renderSelection();
  try {
    if (!await loadContext()) return;
    const draft = contextData?.drafts?.find(d => d.id === id);
    if (zone !== selectionZone) return;
    closeRoutineEditor(); selectionBusy = false;
    if (draft) openRoutineEditor(draft); else text('routine-message', 'Der Entwurf wurde inzwischen entfernt.');
  } catch (error) { text('routine-message', `Neu laden fehlgeschlagen: ${error.message}`); }
  finally { selectionBusy = false; renderSelection(); renderLearning(); }
});

async function deleteRoutine(draft) {
  if (selectionBusy || contextEditing || !confirm('Diesen eigenen Entwurf samt Bewertungen dauerhaft löschen? Musterbelege und HA bleiben unverändert.')) return;
  const zone = selectionZone; selectionBusy = true; contextGeneration++; renderSelection(); renderLearning();
  try {
    await json(`api/v1/zones/${encodeURIComponent(zone)}/drafts/${encodeURIComponent(draft.id)}`, {method:'DELETE', body:JSON.stringify({revision:draft.revision, review_revision:draft.review_notes?.revision || 0})});
    if (zone === selectionZone) { await loadContext(); text('routine-message', 'Entwurf gelöscht.'); }
  } catch (error) { if (zone === selectionZone) text('routine-message', `Löschen nicht bestätigt: ${error.message}`); }
  finally { selectionBusy = false; renderSelection(); renderLearning(); }
}

function exportRoutine(draft) {
  const review = comparisonFor(draft);
  const url = URL.createObjectURL(new Blob([JSON.stringify({schema:'pilotsuite-routine-draft-v1', ...draft,
    review_compass:globalThis.PilotSuiteReviewCompass?.forDraft(draft) || draft.review_compass,
    review_notes:typeof projectReviewNotes === 'function' ? projectReviewNotes(draft) : draft.review_notes,
    automation_check:review?.inspection ? 'structural_review' : review ? 'limited_reference_review' : 'not_checked', automation_review:review}, null, 2)], {type:'application/json'}));
  const link = document.createElement('a'); link.href = url; link.download = 'pilotsuite-routine-draft.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Separate same-origin module; existing Ingress/CSP protection remains unchanged.
const reviewNotesScript = document.createElement('script');
reviewNotesScript.src = endpoint('assets/review_notes.js');
reviewNotesScript.addEventListener('error', () => text('routine-message', 'Prüfnotizen konnten nicht geladen werden. Ansicht neu laden.'));
document.head.append(reviewNotesScript);


const reviewCompassScript = document.createElement('script');
reviewCompassScript.src = endpoint('assets/review_compass.js');
reviewCompassScript.addEventListener('error', () => text('routine-message', 'Prüfkompass konnte nicht geladen werden. Vorhandene Entwurfsfunktionen bleiben verfügbar.'));
document.head.append(reviewCompassScript);
