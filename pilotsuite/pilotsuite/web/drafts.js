// User-authored drafts only. No executable actions, HA calls or automatic saves.
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
  }
  card.append(panel);
}

async function compareRoutine(draft) {
  if (selectionBusy || contextEditing || zoneFormOpen || selectionDraft?.dirty) return;
  const zone = selectionZone, zoneRevision = contextData.revision;
  routineComparison = null; selectionBusy = true; contextGeneration++;
  renderSelection(); renderLearning(); text('routine-message', 'Bestehende Automationen werden ausschließlich lesend auf Entitätsbezüge geprüft …');
  try {
    const result = await json(`api/v1/zones/${encodeURIComponent(zone)}/drafts/${encodeURIComponent(draft.id)}/automation-review`,
      {method:'POST',body:JSON.stringify({revision:draft.revision,zone_revision:zoneRevision})});
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
  const root = byId('routine-list'); root.replaceChildren();
  const drafts = contextData?.drafts || [];
  if (!drafts.length) { root.textContent = 'Noch keine gespeicherten Entwürfe in dieser Zone.'; return; }
  for (const draft of drafts) {
    const card = document.createElement('article'); card.className = 'suggestion';
    const title = document.createElement('h4'); title.textContent = draft.fields.title;
    const detail = document.createElement('p'); detail.textContent = `${routineStatus(draft)} Revision ${draft.revision}.`;
    card.append(title, detail);
    for (const [label, handler] of [['Entwurf bearbeiten', () => openRoutineEditor(draft)],
      ['Entwurf exportieren', () => exportRoutine(draft)], ['Bestehende Automationen prüfen', () => compareRoutine(draft)], ['Entwurf löschen', () => deleteRoutine(draft)]]) {
      const button = document.createElement('button'); button.type = 'button'; button.textContent = label;
      button.disabled = contextEditing || selectionBusy || zoneFormOpen || !!selectionDraft?.dirty;
      if (label === 'Bestehende Automationen prüfen') button.disabled ||= draft.source_status !== 'current' || !!draft.unavailable_targets.length || !draft.fields.target_ids.length;
      button.addEventListener('click', handler); card.append(button);
    }
    appendComparison(card, draft);
    root.append(card);
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
  if (selectionBusy || contextEditing || !confirm('Diesen eigenen Entwurf dauerhaft löschen? Musterbelege und HA bleiben unverändert.')) return;
  const zone = selectionZone; selectionBusy = true; contextGeneration++; renderSelection(); renderLearning();
  try {
    await json(`api/v1/zones/${encodeURIComponent(zone)}/drafts/${encodeURIComponent(draft.id)}`, {method:'DELETE', body:JSON.stringify({revision:draft.revision})});
    if (zone === selectionZone) { await loadContext(); text('routine-message', 'Entwurf gelöscht.'); }
  } catch (error) { if (zone === selectionZone) text('routine-message', `Löschen nicht bestätigt: ${error.message}`); }
  finally { selectionBusy = false; renderSelection(); renderLearning(); }
}

function exportRoutine(draft) {
  const review = comparisonFor(draft);
  const url = URL.createObjectURL(new Blob([JSON.stringify({schema:'pilotsuite-routine-draft-v1', ...draft,
    automation_check:review ? 'limited_reference_review' : 'not_checked', automation_review:review}, null, 2)], {type:'application/json'}));
  const link = document.createElement('a'); link.href = url; link.download = 'pilotsuite-routine-draft.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
