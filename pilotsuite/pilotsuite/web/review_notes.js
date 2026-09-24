// Review notes are explicit user assessments. This module never executes HA actions.
function reviewNoteState(note, draft, comparison, zoneRevision) {
  if (note.stale || note.draft_revision !== draft.revision || note.zone_revision !== zoneRevision
      || (draft.source_status && draft.source_status !== 'current') || draft.unavailable_targets?.length)
    return 'stale';
  const detail = comparison?.inspection;
  if (!detail || comparison.draft_id !== draft.id || comparison.zone_id !== draft.zone_id
      || comparison.draft_revision !== draft.revision || comparison.zone_revision !== zoneRevision
      || detail.entity_id !== note.automation_id
      || typeof detail.config_fingerprint !== 'string' || !detail.config_fingerprint
      || typeof note.config_fingerprint !== 'string' || !note.config_fingerprint) return 'not_rechecked';
  return detail.config_fingerprint === note.config_fingerprint ? 'matches_last_read' : 'config_changed';
}

// Presentation counts only: no overall "approved" state, score or new stored owner.
function summarizeReviewNotes(notes) {
  const summary = {total:0, open:0, needs_change:0, reviewed:0,
    stale:0, config_changed:0, not_rechecked:0, matches_last_read:0};
  for (const note of notes.items || []) {
    summary.total++;
    const disposition = ['open','needs_change','reviewed'].includes(note.disposition) ? note.disposition : 'open';
    const status = ['stale','config_changed','not_rechecked','matches_last_read'].includes(note.view_status)
      ? note.view_status : 'not_rechecked';
    summary[disposition]++; summary[status]++;
  }
  return summary;
}

function reviewNoteInitialDisposition(note, draft, comparison, zoneRevision) {
  if (!note || reviewNoteState(note, draft, comparison, zoneRevision) !== 'matches_last_read') return 'open';
  return ['open','needs_change','reviewed'].includes(note.disposition) ? note.disposition : 'open';
}

function reviewNoteBasisKey(draft, comparison, zoneRevision) {
  // Canonical ordering; changing counts/scores must not discard an authored assessment.
  return JSON.stringify([draft.id, draft.zone_id, draft.revision, zoneRevision,
    [...(draft.current_pattern?.sources || [])].sort(), [...(draft.fields?.target_ids || [])].sort(),
    comparison.inspection?.entity_id, comparison.inspection?.config_fingerprint]);
}

const reviewNoteLabels = {
  open:'Offen', needs_change:'Änderungsbedarf', reviewed:'Manuell geprüft – keine Freigabe',
  stale:'Entwurf oder Quellen geändert – erneut bewerten',
  not_rechecked:'Automationsstand noch nicht erneut geprüft',
  matches_last_read:'Passt zum zuletzt gelesenen Automationsstand',
  config_changed:'Automation geändert – erneut bewerten',
};

function projectReviewNotes(draft) {
  const notes = draft.review_notes || {revision:0, items:[], limit:20};
  const comparison = comparisonFor(draft);
  return {...notes, items:notes.items.map(note => ({...note,
    view_status:reviewNoteState(note, draft, comparison, contextData?.revision)})),
    execution:{allowed:false, actions:[]}};
}

let reviewNoteEditor = null;
let reviewNoteDirty = false;

function appendReviewNotes(card, draft) {
  const section = document.createElement('section'); section.className = 'review-notes';
  const heading = document.createElement('h5'); heading.textContent = 'Prüfzentrale · Bewertungen';
  const notes = projectReviewNotes(draft);
  const summary = summarizeReviewNotes(notes);
  const assessment = document.createElement('p'); assessment.className = 'review-note-summary';
  assessment.textContent = `Deine Bewertungen: ${summary.open} offen · ${summary.needs_change} mit Änderungsbedarf · ${summary.reviewed} manuell geprüft. Keine Ausführungsfreigaben.`;
  const freshness = document.createElement('p'); freshness.className = 'review-note-freshness';
  freshness.textContent = `Prüfgrundlagen: ${summary.stale + summary.config_changed} veraltet/geändert · ${summary.not_rechecked} nicht erneut gelesen · ${summary.matches_last_read} passend zum letzten Lesen. Risiko und fachliche Prüfpunkte bleiben gesondert offen.`;
  const comparison = comparisonFor(draft);
  const inspection = comparison?.inspection;
  const guidance = document.createElement('p');
  const sourceBlocked = draft.source_status !== 'current' || !!draft.unavailable_targets.length || !draft.fields.target_ids.length;
  guidance.textContent = sourceBlocked
    ? 'Nächster Schritt: Entwurfsgrundlage und bestätigte Zielgeräte prüfen. Alte Bewertungen bleiben erhalten; erneutes Lesen ist erst mit gültigem Bezug möglich.'
    : inspection
      ? 'Nächster Schritt: eigene Bewertung zur Detailprüfung festhalten oder bearbeiten. Die fachlichen Prüfpunkte bleiben offen; eine Bewertung erteilt keine Ausführungsfreigabe.'
      : notes.items.length
        ? 'Nächster Schritt: eine gespeicherte Automation direkt erneut prüfen. Es wird nur diese Auswahl gelesen, nichts automatisch bewertet oder gespeichert.'
        : 'Nächster Schritt: bestehende Automationen vergleichen und einen Treffer im Detail prüfen. Ohne Treffer ist Konfliktfreiheit nicht nachgewiesen.';
  if (globalThis.PilotSuiteReviewCompass?.forDraft(draft)) {
    guidance.textContent = 'Der Prüfkompass oben bündelt den nächsten Arbeitsschritt. Gespeicherte Bewertungen bleiben davon getrennt und erteilen keine Ausführungsfreigabe.';
  }
  section.append(heading, assessment, freshness, guidance);
  if (inspection) {
    const button = document.createElement('button'); button.type = 'button';
    button.textContent = 'Bewertung festhalten';
    button.disabled = selectionBusy || contextEditing || zoneFormOpen || !!selectionDraft?.dirty;
    button.addEventListener('click', () => openReviewNote(draft)); section.append(button);
  }
  if (!notes.items.length) {
    const empty = document.createElement('p'); empty.textContent = 'Noch keine eigene Bewertung gespeichert.';
    section.append(empty);
  }
  for (const note of notes.items) {
    const item = document.createElement('article'); item.className = 'review-note';
    const title = document.createElement('strong'); title.textContent = `${note.automation_id} · ${reviewNoteLabels[note.disposition] || 'Offen'}`;
    const state = document.createElement('p'); state.textContent = reviewNoteLabels[note.view_status];
    const textNode = document.createElement('p'); textNode.className = 'review-note-text'; textNode.textContent = note.text || 'Keine zusätzliche Notiz.';
    const basis = document.createElement('small');
    basis.textContent = `Entwurfsversion ${note.draft_revision} · zuletzt beim Speichern gelesen: ${new Date(note.checked_at).toLocaleString()}. Keine laufende Überwachung.`;
    const recheck = document.createElement('button'); recheck.type = 'button';
    recheck.textContent = `Erneut prüfen: ${note.automation_id}`;
    recheck.disabled = sourceBlocked || selectionBusy || contextEditing || zoneFormOpen || !!selectionDraft?.dirty;
    recheck.addEventListener('click', () => compareRoutine(draft, note.automation_id));
    const remove = document.createElement('button'); remove.type = 'button'; remove.textContent = `Bewertung löschen: ${note.automation_id}`;
    remove.disabled = selectionBusy || contextEditing || zoneFormOpen || !!selectionDraft?.dirty;
    remove.addEventListener('click', () => deleteReviewNote(draft, note));
    item.append(title, state, textNode, basis, recheck, remove); section.append(item);
  }
  card.append(section);
}

function reviewForm() {
  let form = byId('review-note-form');
  if (form) return form;
  form = document.createElement('form'); form.id = 'review-note-form'; form.className = 'review-note-form'; form.hidden = true;
  const fieldset = document.createElement('fieldset'); fieldset.id = 'review-note-fields';
  const legend = document.createElement('legend'); legend.textContent = 'Eigene Bewertung – keine Ausführungsfreigabe';
  const basis = document.createElement('p'); basis.id = 'review-note-basis';
  const stored = document.createElement('details'); stored.id = 'review-note-stored';
  const label = document.createElement('label'); label.htmlFor = 'review-note-disposition'; label.textContent = 'Deine Bewertung';
  const select = document.createElement('select'); select.id = 'review-note-disposition';
  for (const value of ['open','needs_change','reviewed']) {
    const option = document.createElement('option'); option.value = value; option.textContent = reviewNoteLabels[value]; select.append(option);
  }
  const noteLabel = document.createElement('label'); noteLabel.htmlFor = 'review-note-text'; noteLabel.textContent = 'Notiz (maximal 2000 Zeichen, keine Zugangsdaten)';
  const textarea = document.createElement('textarea'); textarea.id = 'review-note-text'; textarea.maxLength = 2000; textarea.rows = 5;
  const explanation = document.createElement('p');
  explanation.textContent = 'Beim Speichern wird die Automation erneut gelesen. Bei Änderungen wird nichts überschrieben. Bewertungen bleiben bei einem Lernreset erhalten und lassen sich einzeln löschen.';
  const message = document.createElement('p'); message.id = 'review-note-message'; message.setAttribute('role','status'); message.setAttribute('aria-live','polite');
  const actions = document.createElement('div'); actions.className = 'review-note-actions';
  const save = document.createElement('button'); save.type = 'submit'; save.textContent = 'Bewertung für diesen Prüfstand speichern';
  const reload = document.createElement('button'); reload.type = 'button'; reload.id = 'review-note-reload'; reload.textContent = 'Prüfstand neu laden (Text behalten)';
  reload.addEventListener('click', reloadReviewNoteBasis);
  const cancel = document.createElement('button'); cancel.type = 'button'; cancel.id = 'review-note-cancel'; cancel.textContent = 'Zurück ohne Speichern';
  cancel.addEventListener('click', () => {
    if (selectionBusy || (reviewNoteDirty && !confirm('Ungespeicherte Bewertung verwerfen?'))) return;
    closeReviewNote(); renderSelection(); renderLearning();
  });
  actions.append(save, reload, cancel);
  fieldset.append(legend, basis, stored, label, select, noteLabel, textarea, explanation, actions);
  form.append(fieldset, message);
  form.addEventListener('input', () => { reviewNoteDirty = true; });
  form.addEventListener('change', () => { reviewNoteDirty = true; });
  form.addEventListener('submit', saveReviewNote);
  byId('routine-form').after(form);
  return form;
}

function setReviewNoteBasis(draft, comparison) {
  reviewNoteEditor = {zone:selectionZone, draft, zoneRevision:contextData.revision,
    reviewRevision:draft.review_notes?.revision || 0, inspection:comparison.inspection,
    basisKey:reviewNoteBasisKey(draft, comparison, contextData.revision)};
  text('review-note-basis', `${comparison.inspection.entity_id} · Entwurfsversion ${draft.revision} · Detailprüfung ${new Date(comparison.checked_at).toLocaleString()}. Die Bewertung wird ausdrücklich an diesen Stand gebunden.`);
  const stored = byId('review-note-stored'); stored.replaceChildren();
  const heading = document.createElement('summary'); heading.textContent = 'Zuletzt gespeicherte Bewertung zum Vergleich';
  const detail = document.createElement('p'); detail.className = 'review-note-saved-copy';
  const note = draft.review_notes?.items.find(item => item.automation_id === comparison.inspection.entity_id);
  detail.textContent = note
    ? `${reviewNoteLabels[note.disposition] || 'Offen'} · Entwurfsversion ${note.draft_revision}\n${note.text || 'Keine zusätzliche Notiz.'}`
    : 'Keine gespeicherte Bewertung für diese Automation. Dein Text wird nicht automatisch gespeichert.';
  stored.append(heading, detail);
}

function openReviewNote(draft) {
  if (selectionBusy || contextEditing || zoneFormOpen || selectionDraft?.dirty) return;
  const comparison = comparisonFor(draft);
  if (!comparison?.inspection) return;
  const form = reviewForm();
  setReviewNoteBasis(draft, comparison);
  const existing = draft.review_notes?.items.find(note => note.automation_id === comparison.inspection.entity_id);
  byId('review-note-text').value = existing?.text || '';
  byId('review-note-disposition').value = reviewNoteInitialDisposition(existing, draft, comparison, contextData.revision);
  const changed = existing && reviewNoteState(existing, draft, comparison, contextData.revision) !== 'matches_last_read';
  text('review-note-message', changed ? 'Gespeicherte Bewertung gehört zu einem anderen oder ungeprüften Stand. Text übernommen, Bewertung auf Offen gesetzt. Erneut beurteilen; noch nichts gespeichert.' : '');
  reviewNoteDirty = false; contextEditing = true; contextGeneration++;
  form.hidden = false; renderSelection(); renderLearning();
  form.scrollIntoView({block:'start'}); byId('review-note-text').focus();
}

function closeReviewNote() {
  reviewNoteEditor = null; reviewNoteDirty = false; contextEditing = false;
  byId('review-note-form').hidden = true;
}

async function saveReviewNote(event) {
  event.preventDefault();
  if (!reviewNoteEditor || selectionBusy) return;
  const editor = reviewNoteEditor;
  if (editor.zone !== selectionZone) return;
  const payload = {revision:editor.draft.revision, zone_revision:editor.zoneRevision,
    review_revision:editor.reviewRevision, automation_id:editor.inspection.entity_id,
    config_fingerprint:editor.inspection.config_fingerprint,
    disposition:byId('review-note-disposition').value, text:byId('review-note-text').value};
  selectionBusy = true; contextGeneration++; byId('review-note-fields').disabled = true;
  // An attempted fresh read supersedes the old transient result, even on failure.
  routineComparison = null; renderSelection(); renderLearning();
  try {
    const result = await json(`api/v1/zones/${encodeURIComponent(editor.zone)}/drafts/${encodeURIComponent(editor.draft.id)}/review-notes`,
      {method:'PUT', body:JSON.stringify(payload)});
    if (editor.zone !== selectionZone) return;
    const current = contextData.drafts.find(draft => draft.id === editor.draft.id);
    if (current) current.review_notes = result.review_notes;
    routineComparison = result.automation_review;
    closeReviewNote();
    text('routine-message', 'Bewertung gespeichert. Keine Automation verändert oder freigegeben.');
    // Confirmed save is not relabeled as failed merely because the next GET fails.
    try { await loadContext(); }
    catch (_) { text('routine-message', 'Bewertung gespeichert; Ansicht konnte nicht neu geladen werden.'); }
  } catch (error) {
    if (editor.zone === selectionZone) text('review-note-message', `Speichern nicht bestätigt: ${error.message}. Deine Eingaben bleiben erhalten. Bei Änderungen den Prüfstand neu laden und erneut beurteilen.`);
  } finally {
    selectionBusy = false; byId('review-note-fields').disabled = false; renderSelection(); renderLearning();
  }
}

async function reloadReviewNoteBasis() {
  if (!reviewNoteEditor || selectionBusy) return;
  const editor = reviewNoteEditor;
  if (editor.zone !== selectionZone) return;
  selectionBusy = true; contextGeneration++; byId('review-note-fields').disabled = true;
  routineComparison = null; renderSelection(); renderLearning();
  try {
    if (!await loadContext() || editor.zone !== selectionZone) return;
    const draft = contextData.drafts.find(item => item.id === editor.draft.id);
    if (!draft) throw new Error('Entwurf inzwischen gelöscht');
    const report = await json(`api/v1/zones/${encodeURIComponent(editor.zone)}/drafts/${encodeURIComponent(draft.id)}/automation-inspection`,
      {method:'POST', body:JSON.stringify({revision:draft.revision, zone_revision:contextData.revision,
        automation_id:editor.inspection.entity_id, previous_fingerprint:editor.inspection.config_fingerprint})});
    if (editor.zone !== selectionZone) return;
    routineComparison = report;
    if (!comparisonFor(draft)) { routineComparison = null; throw new Error('Prüfgrundlage inzwischen geändert'); }
    const changed = editor.basisKey !== reviewNoteBasisKey(draft, report, contextData.revision)
      || editor.reviewRevision !== (draft.review_notes?.revision || 0);
    setReviewNoteBasis(draft, report);
    if (changed) {
      byId('review-note-disposition').value = 'open';
      reviewNoteDirty = true; // Programmatic field changes must also protect unsaved work.
      byId('review-note-stored').open = true;
    }
    text('review-note-message', `Prüfstand neu geladen; dein Text wurde beibehalten. ${changed ? 'Grundlage oder gespeicherte Bewertungen geändert: Auswahl auf Offen gesetzt. ' : ''}Detailprüfung und zuletzt gespeicherte Bewertung vergleichen, dann ausdrücklich speichern. Keine automatische Übernahme oder Zusammenführung.`);
  } catch (error) {
    if (editor.zone === selectionZone) text('review-note-message', `Prüfstand nicht bestätigt: ${error.message}. Text bleibt erhalten; keine Bewertung gespeichert.`);
  } finally {
    selectionBusy = false; byId('review-note-fields').disabled = false; renderSelection(); renderLearning();
  }
}

async function deleteReviewNote(draft, note) {
  if (selectionBusy || contextEditing || !confirm('Diese Bewertung und Notiz dauerhaft löschen? Entwurf, Lernbelege und HA bleiben unverändert.')) return;
  const zone = selectionZone;
  selectionBusy = true; contextGeneration++; renderSelection(); renderLearning();
  try {
    const result = await json(`api/v1/zones/${encodeURIComponent(zone)}/drafts/${encodeURIComponent(draft.id)}/review-notes`,
      {method:'DELETE', body:JSON.stringify({revision:draft.revision, zone_revision:contextData.revision,
        review_revision:draft.review_notes.revision, automation_id:note.automation_id})});
    if (zone !== selectionZone) return;
    const current = contextData.drafts.find(item => item.id === draft.id);
    if (current) current.review_notes = result;
    text('routine-message', 'Bewertung gelöscht. Entwurf und HA bleiben unverändert.');
    try { await loadContext(); }
    catch (_) { text('routine-message', 'Bewertung gelöscht; Prüfkompass konnte nicht neu geladen werden. Gespeicherten Stand erneut laden.'); }
  } catch (error) {
    if (zone === selectionZone) text('routine-message', `Löschen nicht bestätigt: ${error.message}. Gespeicherten Stand neu laden.`);
  } finally { selectionBusy = false; renderSelection(); renderLearning(); }
}

if (typeof module !== 'undefined' && module.exports)
  module.exports = {reviewNoteState, summarizeReviewNotes, reviewNoteInitialDisposition, reviewNoteBasisKey};
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', event => {
    if (reviewNoteDirty || (reviewNoteEditor && selectionBusy)) { event.preventDefault(); event.returnValue = ''; }
  });
  const css = document.createElement('link'); css.rel = 'stylesheet'; css.href = endpoint('assets/review_notes.css'); document.head.append(css);
  renderLearning();
}
