const byId = (id) => document.getElementById(id);
const endpoint = (path) => new URL(path.replace(/^\//, ""), window.location.href).toString();

async function json(path, options = {}) {
  let response;
  try { response = await fetch(endpoint(path), {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  }); } catch { throw new Error('Verbindung zu PilotSuite unterbrochen. Bitte erneut versuchen.'); }
  let body;
  try { body = await response.json(); }
  catch { throw new Error(`Antwort nicht lesbar (HTTP ${response.status}). Bitte die Home-Assistant-Oberfläche neu öffnen.`); }
  if (!response.ok) {
    const error = new Error(body.message || `HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return body;
}

function text(id, value) { byId(id).textContent = value ?? "—"; }
const displayLabels = {temperature:'Temperatur', humidity:'Feuchte', illuminance:'Helligkeit', motion:'Bewegung', occupancy:'Präsenz', presence:'Präsenz', light:'Licht', good:'Gut', unknown:'Unbekannt', unavailable:'Nicht verfügbar', invalid:'Ungültig', read_only:'Nur Prüfung', low:'Gering', medium:'Mittel', high:'Hoch'};
const displayLabel = value => displayLabels[value] || value;
const displayNumber = value => typeof value === 'number' ? value.toLocaleString('de-DE', {maximumFractionDigits: 2}) : value;
const moodLabels = {humidity_high:'Feuchte erhöht', humidity_low:'Feuchte niedrig', temperature_high:'Temperatur erhöht', temperature_low:'Temperatur niedrig', uncertainty:'Fehlende Klimawerte', alert:'Auffälligkeit', stable:'Stabilität', system_health:'Datenverbindung'};
function percent(value) { return value == null ? "Nicht bewertbar" : `${Math.round(Number(value) * 100)}%`; }

function renderStatus(status) {
  const ha = status.home_assistant;
  text("ha-state", status.ready ? "Bereit" : "Nicht bereit");
  text("ha-detail", ha.connected ? `Letzter Abgleich ${formatTime(ha.last_refresh_at)}` : (ha.last_error || "Verbindung ausstehend"));
  const zone = status.golden_zone;
  text("zone-state", zone.missing_area_ids.length ? "Bereich fehlt" : `${zone.entity_count} Entitäten`);
  text("zone-detail", zone.resolved_area_ids.join(", ") || `Gesucht: ${zone.requested_area_ids.join(", ")}`);
  const labels = {temperature: "Temperatur", humidity: "Feuchte", motion: "Bewegung", presence: "Präsenz", light: "Licht", illuminance: "Helligkeit"};
  const states = {available: "verfügbar", partial: "teilweise verfügbar", unavailable: "Messwerte fehlen", not_present: "nicht vorhanden"};
  const capabilities = Object.entries(status.capabilities || {}).map(([name, item]) => `${labels[name] || name}: ${states[item.status] || item.status}`);
  text("zone-detail", `${zone.resolved_area_ids.join(", ") || "Bereich fehlt"} · ${capabilities.join(" · ")}`);
  text("habitus-state", `${status.habitus.neuron_count} Beobachtungen`);
  text("habitus-detail", `${status.habitus.suggestion_count} Vorschläge · ${status.habitus.ruleset}`);
  if (status.selection?.active_area_ids.length) {
    text('habitus-detail', `${status.habitus.suggestion_count} Vorschläge · ${status.selection.evaluated_count} ausgewertet, ${status.selection.excluded_count} durch Auswahl ausgeschlossen`);
  }
  text("release-state", status.version);
}

function renderMoods(items) {
  const root = byId("moods");
  root.replaceChildren();
  for (const item of items) {
    const row = document.createElement("div");
    row.className = "mood-row";
    const name = document.createElement("span");
    name.textContent = `${item.zone_name ? item.zone_name + ' · ' : ''}${moodLabels[item.name] || item.name.replaceAll("_", " ")}`;
    const bar = document.createElement("div");
    bar.className = "bar";
    const fill = document.createElement("i");
    fill.style.width = item.score == null ? "0%" : percent(item.score);
    bar.append(fill);
    const score = document.createElement("strong");
    score.textContent = percent(item.score);
    row.append(name, bar, score);
    root.append(row);
  }
}

function renderSuggestions(items) {
  const root = byId("suggestions");
  root.replaceChildren();
  text("suggestion-count", String(items.length));
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "Keine auffällige Regel aktiv.";
    root.append(empty);
    return;
  }
  for (const item of items) {
    const box = document.createElement("div");
    box.className = "suggestion";
    const title = document.createElement("h3");
    title.textContent = item.title;
    const explanation = document.createElement("p");
    explanation.textContent = `${item.explanation} Regelstärke ${percent(item.severity)} · Statistische Sicherheit ${item.confidence == null ? "nicht bestimmt" : percent(item.confidence)} · Risiko ${displayLabel(item.risk)}.`;
    box.append(title, explanation);
    root.append(box);
  }
}

function renderObservations(items) {
  const root = byId("observations");
  root.replaceChildren();
  text("observation-count", String(items.length));
  for (const item of items) {
    const row = document.createElement("tr");
    const value = item.value == null ? "—" : `${displayNumber(item.value)}${item.unit ? ` ${item.unit}` : ""}`;
    for (const content of [item.entity_id, displayLabel(item.kind), value, displayLabel(item.quality)]) {
      const cell = document.createElement("td");
      cell.textContent = String(content);
      row.append(cell);
    }
    row.lastElementChild.className = item.quality === "good" ? "quality-good" : "quality-bad";
    root.append(row);
  }
}

function formatTime(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("de-DE", { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(new Date(value));
}

async function load() {
  byId("error").hidden = true;
  const [status, suggestions] = await Promise.all([
    json("api/v1/status"),
    json("api/v1/suggestions"),
  ]);
  renderStatus(status);
  dashboardSuggestions = suggestions.items;
  if (!selectionInitialized) {
    selectionInitialized = true;
    try { await reloadZones(); }
    catch (error) { selectionInitialized = false; throw error; }
  } else {
    const data = await json('api/v1/zones');
    zoneDefinitions = data.items; zoneResults = data.results || [];
  }
  if (!contextEditing && !selectionBusy && selectionZone) await loadContext();
  renderZoneView();
}

async function refresh() {
  const button = byId("refresh");
  button.disabled = true;
  button.textContent = "Gleiche ab …";
  try {
    await json("api/v1/refresh", { method: "POST", body: "{}" });
    await load();
  } catch (error) {
    byId("error").textContent = error.message;
    byId("error").hidden = false;
  } finally {
    button.disabled = false;
    button.textContent = "Jetzt abgleichen";
  }
}

let selectionInitialized = false;
let selectionDraft = null;
let selectionBusy = false;
let selectionConflict = false;
let selectionZone = '';
let zoneDefinitions = [];
let zoneEditing = null;
let zoneFormOpen = false;
let zoneSaving = false;
let zoneCatalog = [];
let zoneResults = [];
let dashboardSuggestions = [];
let zoneToggleBusy = false;
let contextEditing = false;
let contextData = null;
let contextGeneration = 0;
let zoneExtraSelection = new Set();
const decisionLabels = { relevant: 'Relevant', ignored: 'Ignoriert', unreviewed: 'Ungeprüft' };

function selectionControls() {
  const editMessage = selectionBusy ? 'Vorgang läuft …' : selectionDraft?.dirty ? 'Ungespeicherte Entitätenauswahl. Bitte speichern oder verwerfen, bevor du die Zone wechselst.' : zoneFormOpen || contextEditing ? 'Bearbeitung geöffnet. Zum Wechseln bitte speichern oder abbrechen.' : '';
  text('edit-status', editMessage); byId('edit-status').hidden = !editMessage;
  byId('refresh').disabled = selectionBusy || zoneFormOpen || contextEditing || !!selectionDraft?.dirty;
  byId('zone-toggle').disabled = zoneToggleBusy || selectionBusy || zoneFormOpen || contextEditing || !selectionZone || !!selectionDraft?.dirty || selectionConflict;
  byId('selection-zone').disabled = selectionBusy || zoneFormOpen || contextEditing || !!selectionDraft?.dirty;
  byId('zone-new').disabled = selectionBusy || zoneFormOpen || contextEditing || !!selectionDraft?.dirty;
  byId('zone-edit').disabled = selectionBusy || zoneFormOpen || contextEditing || !!selectionDraft?.dirty || !selectionZone;
  byId('selection-save').disabled = selectionBusy || zoneFormOpen || contextEditing || selectionConflict || !selectionDraft?.dirty;
  byId('selection-discard').disabled = selectionBusy || zoneFormOpen || contextEditing || !selectionZone;
  byId('selection-recommend').disabled = selectionBusy || zoneFormOpen || contextEditing || selectionConflict || !selectionDraft;
  byId('context-edit').disabled = selectionBusy || zoneFormOpen || contextEditing || !!selectionDraft?.dirty || !selectionZone;
  byId('learning-reset').disabled = selectionBusy || zoneFormOpen || contextEditing || !!selectionDraft?.dirty || !selectionZone;
  renderZoneTabs();
}

function renderSelection() {
  selectionControls();
  const root = byId('selection-rows');
  root.replaceChildren();
  if (!selectionDraft) return;
  const query = byId('selection-search').value.toLocaleLowerCase('de');
  const filter = byId('selection-filter').value;
  const inventory = selectionDraft.inventory;
  const items = [...inventory.items, ...inventory.missing.map(item => ({...item, missing: true}))];
  for (const item of items) {
    const decision = selectionDraft.decisions.get(item.entity_id);
    if (filter === 'missing' ? !item.missing : filter !== 'all' && decision !== filter) continue;
    if (![item.entity_id, item.name, item.suggested_role].join(' ').toLocaleLowerCase('de').includes(query)) continue;
    const row = document.createElement('tr');
    const cells = Array.from({length: 5}, () => document.createElement('td'));
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox'; checkbox.checked = decision === 'relevant';
    checkbox.indeterminate = decision === 'unreviewed';
    checkbox.disabled = selectionBusy || zoneFormOpen || contextEditing || selectionConflict;
    checkbox.setAttribute('aria-label', `${item.name || item.entity_id}: relevant`);
    checkbox.addEventListener('change', () => {
      selectionDraft.set(item.entity_id, checkbox.checked ? 'relevant' : 'ignored');
      selectionChanged();
    });
    cells[0].append(checkbox);
    cells[1].textContent = item.name || item.entity_id;
    const id = document.createElement('small'); id.textContent = item.entity_id; cells[1].append(id);
    cells[2].textContent = displayLabel(item.suggested_role) || '—';
    cells[3].textContent = item.missing ? 'Nicht im aktuellen Inventar' : (item.state ?? '—');
    cells[4].textContent = decisionLabels[decision] + (item.recommended ? ' · empfohlen' : '');
    if (decision !== 'unreviewed') {
      const reset = document.createElement('button'); reset.type = 'button'; reset.textContent = 'Ungeprüft setzen';
      reset.disabled = selectionBusy || zoneFormOpen || contextEditing || selectionConflict;
      reset.addEventListener('click', () => { selectionDraft.set(item.entity_id, 'unreviewed'); selectionChanged(); });
      cells[4].append(document.createElement('br'), reset);
    }
    row.append(...cells); root.append(row);
  }
  if (!root.children.length) {
    const row = document.createElement('tr'); const cell = document.createElement('td');
    cell.colSpan = 5; cell.textContent = 'Keine passenden Entitäten.'; row.append(cell); root.append(row);
  }
}

function selectionChanged() {
  text('selection-message', `${Object.keys(selectionDraft.changes).length} geänderte Entitäten. Nur bestätigte Entitäten werden ausgewertet. ${selectionDraft.dirty ? 'Ungespeichert.' : 'Keine Änderungen.'}`);
  renderSelection(); renderZoneView(); renderDailyBrief(); renderFoundationJourney();
}

async function loadSelection(zone) {
  if (selectionBusy) return;
  contextGeneration++;
  if (typeof historyInvalidate === "function") historyInvalidate();
  const zoneChanged = selectionZone !== zone;
  selectionBusy = true; selectionZone = zone;
  // A same-zone reload is also a new basis check, even while inventory is pending.
  invalidateDailyBrief('Alltagsbrief wird für die ausgewählte Zone geladen …');
  if (zoneChanged) {
    contextData = null;
    byId('learning-export').removeAttribute('href');
    routineComparison = null;
    for (const id of ['learning-sources','learning-period','learning-progress','learning-coverage','context-observations','learned-patterns','module-overview','pattern-summary','context-message','zone-guide-steps','routine-list','routine-message']) byId(id).replaceChildren();
    if (typeof closeRoutineEditor === 'function') closeRoutineEditor();
    text('zone-guide-next', 'Zonenstatus wird geladen …');
    text('learning-status', 'Lernstatus wird geladen …');
  }
  renderSelection();
  try {
    const inventory = await json(`api/v1/selections/${encodeURIComponent(zone)}`);
    selectionDraft = new SelectionDraft(inventory); selectionConflict = false;
    await loadContext();
    text('selection-message', `${inventory.resolved ? 'Inventar geladen' : 'Zone derzeit nicht aufgelöst'} · Revision ${inventory.revision}. ${inventory.enabled === false ? 'Zone ist deaktiviert. ' : ''}Ungeprüft ist nicht gleich ignoriert.`);
  } catch (error) {
    if (zone === selectionZone) invalidateDailyBrief('Alltagsbrief nicht verfügbar. Auswahl neu laden.');
    // Do not display one zone's data under another zone's label.
    if (selectionDraft?.inventory.zone_id !== zone) selectionDraft = null;
    if (!contextData) {
      text('learning-status', 'Lernstatus nicht verfügbar. Auswahl neu laden, um es erneut zu versuchen.');
      text('zone-guide-next', 'Zonenstatus nicht verfügbar. Auswahl neu laden.');
    }
    text('selection-message', `Laden fehlgeschlagen: ${error.message}. Neu laden zum Wiederholen.`);
  } finally { selectionBusy = false; renderSelection(); renderZoneView(); }
}

byId('selection-zone').addEventListener('change', event => loadSelection(event.target.value));
for (const id of ['selection-search', 'selection-filter']) byId(id).addEventListener('input', renderSelection);
byId('selection-recommend').addEventListener('click', () => { selectionDraft.recommend(); selectionChanged(); });
byId('selection-discard').addEventListener('click', () => {
  if (selectionDraft?.dirty && !window.confirm('Ungespeicherte Änderungen verwerfen und aktuellen Stand laden?')) return;
  loadSelection(selectionZone);
});
byId('selection-save').addEventListener('click', async () => {
  if (selectionBusy || selectionConflict || !selectionDraft?.dirty) return;
  const changes = Object.entries(selectionDraft.changes);
  if (changes.length > 500) { text('selection-message', 'Bitte höchstens 500 Änderungen auf einmal speichern.'); return; }
  selectionBusy = true; renderSelection();
  try {
    const inventory = await json(`api/v1/selections/${encodeURIComponent(selectionZone)}`, {
      method: 'PATCH', body: JSON.stringify({revision: selectionDraft.inventory.revision, changes: Object.fromEntries(changes), active: true}),
    });
    selectionDraft = new SelectionDraft(inventory);
    text('selection-message', `Gespeichert. ${inventory.enabled === false ? 'Zone ist deaktiviert; Entscheidungen bleiben gespeichert.' : inventory.applied_to_inference ? 'Bestätigte Auswahl ist für die Auswertung aktiv.' : 'Automatischer Umfang bleibt aktiv.'}`);
    await load();
  } catch (error) {
    selectionConflict = error.status === 409;
    text('selection-message', selectionConflict
      ? 'Zwischenzeitlich geändert. Dein Entwurf bleibt sichtbar. Bitte verwerfen / neu laden und Auswahl erneut prüfen.'
      : `Speichern nicht bestätigt: ${error.message}. Entwurf bleibt erhalten; bei Unsicherheit neu laden.`);
  } finally { selectionBusy = false; renderSelection(); }
});
window.addEventListener('beforeunload', event => {
  if (selectionDraft?.dirty || zoneFormOpen || contextEditing) { event.preventDefault(); event.returnValue = ''; }
});

async function reloadZones(preferred = selectionZone) {
  const data = await json('api/v1/zones');
  zoneDefinitions = data.items; zoneResults = data.results || [];
  byId('selection-zone').replaceChildren(...zoneDefinitions.map(zone => {
    const option = document.createElement('option'); option.value = zone.zone_id;
    option.textContent = zone.name + (zone.enabled ? '' : ' (deaktiviert)'); return option;
  }));
  const target = zoneDefinitions.find(z => z.zone_id === preferred) || zoneDefinitions[0];
  if (target) { byId('selection-zone').value = target.zone_id; await loadSelection(target.zone_id); }
  else { selectionZone = ''; selectionDraft = null; text('selection-message', 'Noch keine Habitus-Zone. Lege eine neue Zone an.'); renderSelection(); }
}

function renderExtraChoices() {
  const query = byId('zone-extra-search').value.toLowerCase();
  const options = zoneCatalog.filter(item => zoneExtraSelection.has(item.entity_id) || (!item.disabled && `${item.name} ${item.entity_id}`.toLowerCase().includes(query)))
    .sort((a,b) => Number(zoneExtraSelection.has(b.entity_id)) - Number(zoneExtraSelection.has(a.entity_id))).slice(0, 600);
  byId('zone-extras').replaceChildren(...options.map(item => {
    const option = document.createElement('option'); option.value = item.entity_id;
    option.textContent = `${item.name || item.entity_id} · ${item.entity_id}${item.disabled ? ' (nicht verfügbar)' : ''}`;
    option.selected = zoneExtraSelection.has(item.entity_id); return option;
  }));
}

async function openZoneEditor(existing) {
  if (selectionBusy || selectionDraft?.dirty || zoneFormOpen || contextEditing) return;
  zoneFormOpen = true; byId('zone-editor').open = true; renderSelection();
  try {
    const [areas, catalog, zones] = await Promise.all([json('api/v1/areas'), json('api/v1/entity-catalog'), json('api/v1/zones')]);
    zoneEditing = existing ? zones.items.find(z => z.zone_id === selectionZone) : null;
    if (existing && !zoneEditing) throw new Error('Zone nicht mehr vorhanden. Neu laden.');
    const zone = zoneEditing || {name: '', area_ids: [], extra_entity_ids: [], enabled: false, profile: 'observe'};
    byId('zone-name').value = zone.name; byId('zone-profile').value = zone.profile;
    const allAreas = new Map(areas.items.map(a => [a.area_id, a.name || a.area_id]));
    for (const id of zone.area_ids) if (!allAreas.has(id)) allAreas.set(id, `${id} (nicht verfügbar)`);
    byId('zone-areas').replaceChildren(...[...allAreas].map(([id, name]) => {
      const label = document.createElement('label'); const input = document.createElement('input');
      input.type = 'checkbox'; input.value = id; input.checked = zone.area_ids.includes(id);
      label.append(input, document.createTextNode(name)); return label;
    }));
    zoneExtraSelection = new Set(zone.extra_entity_ids);
    const allEntities = new Map(catalog.items.map(e => [e.entity_id, e]));
    for (const id of zoneExtraSelection) if (!allEntities.has(id)) allEntities.set(id, {entity_id: id, disabled: true});
    zoneCatalog = [...allEntities.values()].sort((a,b) => Number(zoneExtraSelection.has(b.entity_id)) - Number(zoneExtraSelection.has(a.entity_id)));
    byId('zone-extra-search').value = ''; renderExtraChoices();
    text('zone-form-title', existing ? 'Zone bearbeiten' : 'Neue Zone');
    text('zone-message', 'Zusätzliche Entitäten: bis zu 600 Treffer sichtbar. Suche eingrenzen; ausgewählte Einträge bleiben erhalten.');
    byId('zone-form').hidden = false; byId('zone-name').focus();
  } catch (error) { zoneFormOpen = false; text('zone-message', error.message); renderSelection(); }
}
byId('zone-new').addEventListener('click', () => openZoneEditor(false));
byId('zone-edit').addEventListener('click', () => openZoneEditor(true));
byId('zone-extra-search').addEventListener('input', renderExtraChoices);
byId('zone-extras').addEventListener('change', () => {
  for (const option of byId('zone-extras').options) {
    if (option.selected) zoneExtraSelection.add(option.value); else zoneExtraSelection.delete(option.value);
  }
});
byId('zone-cancel').addEventListener('click', () => {
  if (zoneSaving) return;
  zoneFormOpen = false; byId('zone-form').hidden = true; renderSelection();
});
byId('zone-form').addEventListener('submit', async event => {
  event.preventDefault(); if (zoneSaving) return;
  const definition = {name: byId('zone-name').value, profile: byId('zone-profile').value,
    enabled: zoneEditing?.enabled ?? false, area_ids: [...byId('zone-areas').querySelectorAll('input:checked')].map(o => o.value), extra_entity_ids: [...zoneExtraSelection]};
  zoneSaving = true; byId('zone-fields').disabled = true;
  try {
    const payload = {definition}; if (zoneEditing) payload.revision = zoneEditing.revision;
    const saved = await json(`api/v1/zones${zoneEditing ? '/' + encodeURIComponent(zoneEditing.zone_id) : ''}`, {method: zoneEditing ? 'PATCH' : 'POST', body: JSON.stringify(payload)});
    zoneFormOpen = false; byId('zone-form').hidden = true;
    text('zone-message', 'Zone gespeichert. Jetzt die relevanten Entitäten prüfen.');
    await reloadZones(saved.zone_id); await load();
  } catch (error) { text('zone-message', error.status === 409 ? 'Zone oder Entitätenauswahl zwischenzeitlich geändert. Entwurf bleibt erhalten. Abbrechen und erneut öffnen, um den aktuellen Stand zu laden.' : error.message); }
  finally { zoneSaving = false; byId('zone-fields').disabled = false; renderSelection(); }
});

byId("refresh").addEventListener("click", refresh);
load().catch((error) => {
  byId("error").textContent = error.message;
  byId("error").hidden = false;
});

// Refresh the display without forcing additional HA snapshots.
setInterval(() => {
  if (!document.hidden && !selectionBusy && !contextEditing && !zoneFormOpen && !selectionDraft?.dirty && !document.activeElement?.closest('#zone-tabs, #learned-patterns, #zone-summary')) load().catch((error) => {
    byId("error").textContent = error.message;
    byId("error").hidden = false;
  });
}, 15000);


function renderZoneTabs() {
  const focusedId = byId('zone-tabs').contains(document.activeElement) ? document.activeElement.id : null;
  const locked = selectionBusy || zoneFormOpen || contextEditing || zoneToggleBusy || !!selectionDraft?.dirty;
  byId('zone-tabs').replaceChildren(...zoneDefinitions.map(zone => {
    const button = document.createElement('button'); button.type = 'button';
    button.id = `tab-${zone.zone_id}`;
    button.tabIndex = zone.zone_id === selectionZone ? 0 : -1;
    button.setAttribute('role', 'tab'); button.setAttribute('aria-selected', String(zone.zone_id === selectionZone));
    button.textContent = `${zone.name}${zone.enabled ? '' : ' · pausiert'}`;
    button.disabled = locked;
    button.addEventListener('click', async () => {
      byId('selection-search').value = ''; byId('selection-filter').value = 'all';
      byId('selection-zone').value = zone.zone_id;
      await loadSelection(zone.zone_id);
      document.getElementById(`tab-${zone.zone_id}`)?.focus();
    });
    button.addEventListener('keydown', event => {
      const tabs = [...byId('zone-tabs').children]; let index = tabs.indexOf(button);
      if (event.key === 'ArrowRight') index = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') index = (index + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') index = 0;
      else if (event.key === 'End') index = tabs.length - 1;
      else return;
      event.preventDefault(); tabs[index].click();
    });
    return button;
  }));
  if (focusedId) byId(focusedId)?.focus({preventScroll:true});
}

function renderZoneView() {
  const zone = zoneDefinitions.find(z => z.zone_id === selectionZone);
  const result = zoneResults.find(z => z.zone_id === selectionZone);
  text('active-zone-name', zone?.name || 'Noch keine Zone');
  text('zone-toggle', zone?.enabled ? 'Auswertung pausieren' : 'Auswertung starten');
  const note = zone?.profile === 'observe' ? 'Neutrales Profil: Beobachtung und Datenqualität. Aktivitätsmuster findest du unter Lernen.' : 'Erdkeller-Klimaregeln; Aktivitätsmuster findest du unter Lernen.';
  text('zone-state-message', !zone ? 'Mit + Neue Zone beginnen.' :
    `${zone.enabled ? 'Auswertung aktiv' : 'Pausiert – Entitäten können bereits ausgewählt werden'}. ${result?.evaluated_count ?? 0} Beobachtungen. ${note}${selectionDraft?.dirty ? ' Bitte Auswahl zuerst speichern oder verwerfen.' : ''}${zone.enabled && !result?.evaluated_count ? ' Noch keine auswertbaren Beobachtungen: relevante Entitäten und deren Zustände prüfen.' : ''}`);
  renderCompactSummary(result);
  renderMoods(result?.moods || []);
  if (!result?.moods?.length) text('moods', zone?.enabled ? 'Noch keine Bewertung verfügbar.' : 'Zone pausiert. Auswahl speichern und Auswertung starten.');
  renderSuggestions(zone?.enabled ? dashboardSuggestions.filter(item => item.scope?.includes(selectionZone)) : []);
  renderObservations(result?.neurons || []);
  renderZoneTabs();
}

byId('zone-toggle').addEventListener('click', async () => {
  if (selectionBusy || zoneFormOpen || contextEditing || zoneToggleBusy || selectionDraft?.dirty || selectionConflict) return;
  const current = zoneDefinitions.find(z => z.zone_id === selectionZone);
  if (!current) return;
  zoneToggleBusy = true; selectionBusy = true; renderSelection();
  try {
    // Definitions and selections share a revision; fetch it after the latest selection save.
    const fresh = await json('api/v1/zones');
    const zone = fresh.items.find(z => z.zone_id === selectionZone);
    if (!zone) throw new Error('Zone nicht mehr vorhanden. Bitte neu laden.');
    const {name, area_ids, extra_entity_ids, profile} = zone;
    await json(`api/v1/zones/${encodeURIComponent(zone.zone_id)}`, {
      method: 'PATCH', body: JSON.stringify({revision: zone.revision,
        definition: {name, area_ids, extra_entity_ids, profile, enabled: !current.enabled}}),
    });
    selectionBusy = false;
    await reloadZones(zone.zone_id); await load();
  } catch (error) {
    text('zone-state-message', `Änderung nicht bestätigt: ${error.message}. Bitte neu laden und Status prüfen.`);
  } finally { zoneToggleBusy = false; selectionBusy = false; renderSelection(); }
});


function renderCompactSummary(result) {
  const inventory = selectionDraft?.inventory;
  const items = inventory?.items || [];
  const count = key => items.filter(i => i.decision === key).length;
  text('zone-counts', `${items.length} Kandidaten · ${count('relevant')} relevant · ${count('unreviewed')} ungeprüft · ${count('ignored')} ignoriert · ${result?.evaluated_count ?? 0} ausgewertete Beobachtungen`);
  const labels = {temperature: 'Temperatur', humidity: 'Feuchte', illuminance: 'Helligkeit', presence: 'Präsenz / Bewegung', light: 'Licht'};
  const statuses = {not_selected: 'Keine Hauptsensoren ausgewählt', ambiguous: 'Hauptsensoren auswählen', unavailable: 'Messwert nicht verfügbar', not_present: 'Kein bestätigter Sensor', partial: 'Teilweise verfügbar'};
  byId('zone-summary').replaceChildren(...Object.entries(labels).map(([kind, label]) => {
    const card = document.createElement('article'); card.className = 'card';
    const title = document.createElement('span'); title.textContent = label;
    const value = document.createElement('strong'); const info = result?.summary?.[kind];
    value.textContent = !info ? (zoneDefinitions.find(z => z.zone_id === selectionZone)?.enabled ? 'Keine Bewertung' : 'Pausiert') : (info.status === 'available' || info.status === 'partial')
      ? info.value != null ? `${Number(info.value).toLocaleString('de-DE', {maximumFractionDigits: 1})} ${info.unit || ''}` : `${info.on} von ${info.total} aktiv${info.status === 'partial' ? ' · Daten fehlen' : ''}`
      : statuses[info.status] || info.status;
    card.append(title, value);
    const ids = [...new Set([...(info?.requested_sources || []), ...(info?.sources || [])])];
    if (ids.length) {
      const detail = document.createElement('details');
      const heading = document.createElement('summary'); heading.textContent = `Quellen prüfen (${ids.length})`;
      detail.append(heading);
      for (const id of ids) {
        const line = document.createElement('p');
        const item = items.find(i => i.entity_id === id);
        line.textContent = `${item?.name || id} · ${id}${info.sources.includes(id) ? '' : ' · nicht in der Auswertung verfügbar'}`;
        detail.append(line);
      }
      card.append(detail);
    }
    if (info?.aggregation === 'any_on') {
      const source = document.createElement('small');
      source.textContent = `Zonenreferenz: ${info.active === true ? 'Aktivität' : info.active === false ? 'alle Quellen inaktiv' : 'unbekannt'} · ${(info.sources || []).join(', ') || 'keine Hauptquelle'}`;
      card.append(source);
    }
    if (info?.sources?.length && info.aggregation === 'median') { const source = document.createElement('small'); source.textContent = `${info.valid_count} gültige Hauptsensoren · automatischer Referenzwert${info.status === 'partial' ? ' · Daten fehlen' : ''} · Median; Min ${info.min} / Max ${info.max} ${info.unit || ''}`; card.append(source); }
    return card;
  }));
}

async function loadContext() {
  const zone = selectionZone;
  const generation = ++contextGeneration;
  invalidateDailyBrief('Alltagsbrief wird neu geprüft …', true);
  let result;
  try { result = await json(`api/v1/zones/${encodeURIComponent(zone)}/context`); }
  catch (error) {
    if (zone !== selectionZone || generation !== contextGeneration) return false;
    invalidateDailyBrief('Alltagsbrief nicht verfügbar. Neu laden zum Wiederholen.');
    throw error;
  }
  // A zone can be revisited, and overlapping reads can finish out of order.
  if (zone !== selectionZone || generation !== contextGeneration) return false;
  contextData = result;
  if (typeof historyCheckRevision === "function") historyCheckRevision();
  renderLearning();
  return true;
}
function renderZoneGuide() {
  const guide = contextData?.guide;
  const root = byId('zone-guide-steps'); root.replaceChildren();
  const next = byId('zone-guide-next'); next.replaceChildren();
  if (!guide) { next.textContent = 'Einrichtungshinweise derzeit nicht verfügbar.'; return; }
  const labels = {complete:'Erfüllt', attention:'Prüfen', paused:'Pausiert', optional:'Optional', waiting:'Belege abwarten', review:'Zur Prüfung'};
  const targets = new Set(['zone-setup','entity-details','zone-overview','learning-section','pattern-workbench']);
  function link(step) {
    const a = document.createElement('a'); a.textContent = step.title;
    if (targets.has(step.target)) {
      a.href = '#' + step.target;
      a.addEventListener('click', () => {
        const target = byId(step.target);
        if (target?.tagName === 'DETAILS') target.open = true;
      });
    }
    return a;
  }
  next.append(link(guide.next_step), document.createTextNode(' · ' + guide.next_step.detail));
  for (const step of guide.steps) {
    const li = document.createElement('li');
    li.append(link(step), document.createTextNode(` — ${labels[step.state] || step.state}. ${step.detail}`));
    root.append(li);
  }
}
// Keep invalidation local to this view: never erase unsaved configuration/editor data.
function invalidateDailyBrief(message = 'Alltagsbrief derzeit nicht verfügbar. Neu laden zum Wiederholen.', retainView = false) {
  invalidateFoundationJourney();
  const root = byId('daily-brief');
  if (!root) return;
  root._invalidBriefContexts ||= new WeakSet();
  if (contextData && typeof contextData === 'object') root._invalidBriefContexts.add(contextData);
  const focusWasInside = root.contains(document.activeElement);
  // Keep only presentation state, never a candidate or evidence. Reapply it
  // after a matching fresh response; errors, zone changes and edits discard it.
  if (retainView && root._briefRenderKey) {
    root._briefSuspendedView = {key: root._briefRenderKey, scope: root._briefScope,
      open: !!root.querySelector('details')?.open,
      focus: root.querySelector('details > summary') === document.activeElement ? 'summary' :
        root.querySelector('a[data-pattern-id]') === document.activeElement ? 'candidate' : null};
  } else if (!retainView) {
    root._briefSuspendedView = null;
  }
  root._briefRenderKey = null;
  root.replaceChildren();
  root.textContent = message;
  if (focusWasInside) { root.tabIndex = -1; root.focus(); }
}

const invalidFoundationContexts = new WeakSet();
function invalidateFoundationJourney() {
  if (contextData && typeof contextData === 'object') invalidFoundationContexts.add(contextData);
  const root=byId('foundation-journey'), detail=byId('foundation-detail');
  if (root) { root.replaceChildren(); root.textContent='Zonenbasis noch nicht bestätigt. Wird beim nächsten erfolgreichen Laden aktualisiert.'; }
  if (detail) detail.replaceChildren();
}
function renderFoundationJourney() {
  const root=byId('foundation-journey'), detail=byId('foundation-detail');
  if (!root || !detail) return;
  const f=contextData?.foundation, journey=f?.setup_journey;
  const stale=!contextData || invalidFoundationContexts.has(contextData)
    || f?.zone_id!==selectionZone || f?.revision!==contextData.revision;
  if (stale || selectionDraft?.dirty || contextEditing || zoneFormOpen) {
    root.textContent='Zonenbasis nicht bestätigt oder Bearbeitung offen. Keine Übernahme freigegeben.';
    detail.replaceChildren(); return;
  }
  root.replaceChildren(); detail.replaceChildren();
  if (!journey) { root.textContent='Zonenbasis derzeit nicht verfügbar.'; return; }
  const labels={ready:'Quellen zugeordnet', attention:'Prüfen', unverified:'Ungeprüft', optional:'Optional',
    planned:'Vorbereitet', locked:'Gesperrt', needs_sources:'Quellen fehlen'};
  const modules={presence:'Anwesenheit',lighting:'Beleuchtung',media:'Musik',climate:'Raumklima'};
  const roles={presence:'Anwesenheit',light:'Leuchten',climate:'Klimaregler',temperature:'Temperatur',
    'one_of:illuminance/daylight_binary':'Lux oder Helligkeitsindikator'};
  for (const step of (journey.steps || []).slice(0,5)) {
    const card=document.createElement('article'); card.className='card';
    const title=document.createElement('strong'); title.textContent=step.title;
    const state=document.createElement('span'); state.className='tag'; state.textContent=labels[step.state]||'Ungeprüft';
    const p=document.createElement('small'); p.textContent=step.summary;
    card.append(title,state,p); root.append(card);
  }
  const note=document.createElement('p');
  note.textContent='Planungsansicht, keine laufende Zonensteuerung. Timer, Helferanlage und Automationsübernahme bleiben gesperrt.';
  detail.append(note);
  const counts=f.helper_reconciliation?.counts;
  if (counts) {
    const p=document.createElement('p');
    p.textContent=`Helferhinweise: ${counts.inspect||0} exakte Registertreffer prüfen · ${counts.unverified||0} Bestand ungeklärt · ${counts.conflict||0} Namenskonflikte.`;
    detail.append(p);
  }
  if (f.presence_contract) {
    const p=document.createElement('p');
    p.textContent=`Zugeordneter Raumstatus: ${f.presence_contract.logical_owner||'keiner'} · ${(f.presence_contract.raw_sources||[]).length} weitere Quellen. Keine geprüfte Timerfunktion.`;
    detail.append(p);
  }
  if (f.capability_matrix) {
    const list=document.createElement('ul');
    for (const item of (f.capability_matrix.items||[]).slice(0,4)) {
      const li=document.createElement('li');
      li.textContent=`${modules[item.module]||item.module}: ${labels[item.state]||'Ungeprüft'}${(item.missing||[]).length?' · fehlt '+item.missing.map(x=>roles[x]||x).join(', '):''}`;
      list.append(li);
    }
    detail.append(list);
  }
}
function renderDailyBrief() {
  const root = byId('daily-brief');
  if (!root) return;
  const object = value => value && typeof value === 'object' && !Array.isArray(value);
  const integer = value => Number.isSafeInteger(value) && value >= 0;
  const closed = value => object(value) && value.allowed === false &&
    Array.isArray(value.actions) && value.actions.length === 0;
  // Python bounds Unicode code points, not JavaScript UTF-16 code units.
  const shortString = (value, size) => typeof value === 'string' &&
    value.length <= size * 2 && Array.from(value).length <= size;
  const boundedText = (value, size = 500) => typeof value === 'string'
    ? Array.from(value.slice(0, size * 2)).slice(0, size).join('').replace(/[\u0000-\u001f\u007f]/g, '').trim() : '';
  const textRows = value => Array.isArray(value)
    ? value.slice(0, 8).map(item => boundedText(item)).filter(Boolean) : [];
  const renderedContext = contextData;
  const inventory = selectionDraft?.inventory;
  const brief = contextData?.daily_brief;
  if (!object(brief) || !object(inventory) || !object(contextData) ||
      root._invalidBriefContexts?.has(contextData) ||
      brief.schema !== 'pilotsuite-daily-brief-v1' ||
      inventory.zone_id !== selectionZone || brief.zone_id !== selectionZone ||
      !integer(inventory.revision) || !integer(brief.revision) ||
      !integer(contextData.revision) || brief.revision !== inventory.revision ||
      contextData.revision !== inventory.revision ||
      (contextData.zone_id !== undefined && contextData.zone_id !== selectionZone) ||
      !closed(brief.execution)) {
    invalidateDailyBrief('Alltagsbrief nicht für den aktuellen Zonenstand bestätigt. Neu laden zum Wiederholen.');
    return;
  }
  if (selectionDraft.dirty === true) {
    invalidateDailyBrief('Ungespeicherte Auswahl: Alltagsbrief nach Speichern oder Verwerfen erneut laden.');
    return;
  }
  // Cross-check the projection against its existing parent response. This is
  // transport/UI consistency validation, not a second detector or permission owner.
  const sourceSet = value => {
    if (!Array.isArray(value) || value.length > 20 || value.some(id =>
        typeof id !== 'string' || id !== id.trim() || id.length > 255 || !/^[a-z0-9_]+\.[a-z0-9_]+$/.test(id))) return null;
    const result = new Set(value);
    return result.size === value.length ? result : null;
  };
  const preferenceMatches = value => object(value) &&
    ((value.preference === null && value.state === 'unreviewed') ||
     (value.preference === 'accepted' && value.state === 'review_requested'));
  const currentBasis = value => {
    if (!object(value) || inventory.enabled !== true || contextData.enabled !== true ||
        contextData.eligible !== true || contextData.config?.learning !== true ||
        contextData.collection_state !== 'collecting' || brief.truncated !== false ||
        !['sampled', 'partial'].includes(brief.coverage_state) ||
        !preferenceMatches(value)) return false;
    const sources = sourceSet(value.source_ids);
    const roles = sourceSet(contextData.config?.roles?.presence);
    const collecting = sourceSet(contextData.collecting_sources);
    if (!sources?.size || !roles?.size || !collecting?.size ||
        !Array.isArray(inventory.items) || inventory.items.length > 2000 ||
        !Array.isArray(contextData.reviews) || contextData.reviews.length > 200) return false;
    for (const id of sources) {
      const items = inventory.items.filter(item => object(item) && item.entity_id === id);
      if (!roles.has(id) || !collecting.has(id) || items.length !== 1 ||
          items[0].decision !== 'relevant' || !['on', 'off'].includes(items[0].state)) return false;
    }
    const matches = contextData.reviews.filter(review => object(review) &&
      review.pattern_id === value.pattern_id && review.zone_id === selectionZone &&
      review.revision === inventory.revision);
    if (matches.length !== 1 || matches[0].schema !== 'pilotsuite-review-v1' ||
        matches[0].risk !== 'read_only' || !closed(matches[0].execution) ||
        !preferenceMatches(matches[0]) || matches[0].preference !== value.preference ||
        matches[0].state !== value.state) return false;
    const originalSources = sourceSet(matches[0].sources);
    return originalSources?.size === sources.size && [...sources].every(id => originalSources.has(id));
  };
  let candidate = null;
  if (brief.candidate !== null && brief.candidate !== undefined) {
    const value = brief.candidate;
    const stats = value?.statistics;
    const window = stats?.window_local;
    if (!object(value) || !closed(value.execution) || !currentBasis(value) ||
        value.basis_kind !== 'retained_review' || value.navigation !== 'pattern_workbench' ||
        value.basis?.zone_id !== selectionZone || value.basis?.revision !== inventory.revision ||
        !shortString(value.pattern_id, 128) || !value.pattern_id ||
        !shortString(value.title, 240) || !value.title.trim() ||
        !['unreviewed', 'review_requested'].includes(value.state) ||
        !object(stats) || !integer(stats.activation_count) || stats.activation_count < 1 ||
        !integer(stats.distinct_day_count) || stats.distinct_day_count < 1 ||
        stats.distinct_day_count > stats.activation_count || !object(window) ||
        !integer(window.start_hour) || !integer(window.end_hour) ||
        window.start_hour >= window.end_hour || window.end_hour > 24 ||
        typeof stats.timezone !== 'string' || stats.timezone.length > 128 ||
        !Array.isArray(brief.withheld_reasons) || brief.withheld_reasons.length > 0) {
      invalidateDailyBrief('Der Prüfkandidat hat keine konsistente Grundlage. Neu laden zum Wiederholen.');
      return;
    }
    candidate = {id: value.pattern_id, title: boundedText(value.title, 240),
      evidence: `${stats.activation_count} Aktivierungen an ${stats.distinct_day_count} Tagen · ` +
        `${window.start_hour}–${window.end_hour} Uhr ${boundedText(stats.timezone, 128)} · aufbewahrte Belege`};
  }
  const counts = object(brief.excluded) ? brief.excluded : {};
  const model = {zone: selectionZone, revision: inventory.revision, candidate,
    observations: Array.isArray(brief.observations) ? brief.observations.slice(0, 8)
      .map(item => boundedText(item?.summary)).filter(Boolean) : [],
    reasons: textRows(brief.withheld_reasons), cautions: textRows(brief.cautions),
    limits: textRows(brief.limits),
    dismissed: integer(counts.dismissed) ? counts.dismissed : null,
    deferred: integer(counts.deferred) ? counts.deferred : null};
  const renderKey = JSON.stringify(model);
  const navigateCurrentBrief = event => {
    // Editing/feedback may update the surrounding app before this view renders.
    // Recheck only navigation relevance; this is never an execution grant.
    if (contextData !== renderedContext || selectionDraft?.inventory !== inventory ||
        selectionZone !== model.zone || inventory.revision !== model.revision ||
        contextData?.revision !== model.revision || selectionDraft?.dirty === true ||
        root._invalidBriefContexts?.has(contextData) || !currentBasis(brief.candidate)) {
      event.preventDefault();
      invalidateDailyBrief('Der Prüfstand hat sich geändert. Alltagsbrief nach Speichern oder Verwerfen erneut laden.');
      return;
    }
    const target = byId('pattern-workbench');
    if (!target) return;
    if (target.tagName === 'DETAILS') target.open = true;
    target.tabIndex = -1;
    target.focus();
  };
  // Keep the DOM/focus, but refresh the handler to the latest verified response.
  if (root._briefRenderKey === renderKey) {
    const link = root.querySelector('a[data-pattern-id]');
    if (link) link.onclick = navigateCurrentBrief;
    return;
  }
  const scope = JSON.stringify([model.zone, model.revision]);
  const suspended = root._briefSuspendedView;
  const resume = suspended?.key === renderKey && suspended?.scope === scope ? suspended : null;
  root._briefSuspendedView = null;
  const wasOpen = root._briefScope === scope && (root.querySelector('details')?.open || resume?.open);
  const focusWasInside = root.contains(document.activeElement);
  root.replaceChildren();
  const paragraph = (value, muted = false) => {
    const p = document.createElement('p');
    if (muted) p.className = 'muted';
    p.textContent = value;
    root.append(p);
    return p;
  };
  paragraph('Bestätigtes Inventar: ' + (model.observations.join(' · ') || 'derzeit nicht auswertbar.'));
  if (candidate) {
    const p = paragraph('');
    const strong = document.createElement('strong'); strong.textContent = 'Zur Prüfung: ';
    const link = document.createElement('a');
    link.href = '#pattern-workbench'; link.textContent = candidate.title;
    link.dataset.patternId = candidate.id;
    link.onclick = navigateCurrentBrief;
    p.append(strong, link);
    paragraph(candidate.evidence, true);
    paragraph('In der Musterwerkbank prüfen. Keine Ausführung oder Freigabe.', true);
  } else {
    paragraph('Derzeit kein ausreichend belegter Prüfkandidat.');
  }
  for (const reason of model.reasons) paragraph(reason, true);
  for (const caution of model.cautions) paragraph('Hinweis: ' + caution, true);
  if (model.dismissed === null || model.deferred === null) {
    paragraph('Zurückgestellte Muster: Anzahl nicht bestätigt.', true);
  } else if (model.dismissed || model.deferred) {
    paragraph(`Nicht erneut vorgeschlagen: ${model.dismissed} abgelehnt, ${model.deferred} vertagt.`, true);
  }
  if (model.limits.length) {
    const details = document.createElement('details');
    details.open = Boolean(wasOpen);
    const summary = document.createElement('summary'); summary.textContent = 'Grundlage und Grenzen';
    details.append(summary);
    for (const limit of model.limits) {
      const p = document.createElement('p'); p.textContent = limit; details.append(p);
    }
    root.append(details);
  }
  root._briefRenderKey = renderKey;
  root._briefScope = scope;
  if (focusWasInside) { root.tabIndex = -1; root.focus(); }
  // Do not steal focus if the user moved it elsewhere while the request ran.
  if (resume?.focus && document.activeElement === root) {
    const target = root.querySelector(resume.focus === 'summary' ? 'details > summary' : 'a[data-pattern-id]');
    target?.focus({preventScroll: true});
  }
}
function renderLearning() {
  renderRoutineDrafts();
  renderZoneGuide();
  renderDailyBrief();
  renderFoundationJourney();
  if (!contextData?.config) return;
  const cfg = contextData.config;
  const moduleRoot = byId('module-overview'); moduleRoot.replaceChildren();
  const moduleStates = {active:'Aktiv', paused:'Pausiert', off:'Ausgeschaltet', collecting:'Sammlung bereit', disconnected:'Verbindung fehlt', no_source:'Quelle fehlt', planned:'Geplant', blocked:'Gesperrt'};
  for (const module of contextData.modules || []) {
    const card = document.createElement('article'); card.className='card';
    const name = document.createElement('strong'); name.textContent=module.name;
    const state = document.createElement('p'); state.textContent=`${moduleStates[module.state] || module.state}${module.configurable ? ' · Konfiguration: '+module.configurable : ''}`;
    card.append(name,state); moduleRoot.append(card);
  }
  text('learning-status', `${cfg.learning ? contextData.eligible ? 'Lernfreigabe aktiv' : 'Freigegeben, aber Zone oder Lernquelle derzeit nicht auswertbar' : 'Lernen ausgeschaltet'} · ${contextData.event_count} Aktivierungen gespeichert · maximal 14 Tage.`);
  const states = {off:'Lernen ausgeschaltet', paused:'Zone pausiert – keine Sammlung', disconnected:'Datenverbindung nicht bereit – Sammlung nicht bestätigt', no_source:'Keine auswertbare Lernquelle', collecting:'Lernfreigabe aktiv – Sammlung bereit'};
  if (contextData.collection_state) text('learning-status', `${states[contextData.collection_state]} · ${contextData.event_count} Aktivierungen gespeichert · maximal ${contextData.retention_days} Tage.`);
  const sourceIds = cfg.roles.presence || [];
  const sourceName = id => contextData.candidates?.find(i => i.entity_id === id)?.name || id;
  text('learning-sources', `Gespeicherte Präsenzgruppe: ${sourceIds.map(sourceName).join(', ') || 'keine'}. Auswertbare Quellen: ${(contextData.collecting_sources || []).map(sourceName).join(', ') || 'keine'}.`);
  text('learning-status', byId('learning-status').textContent + ` Davon ${contextData.historical_event_count || 0} historische Belege.`);
  const progress = contextData.progress;
  const timeBasis = contextData.time_basis || 'UTC';
  const dayLabels = {all:'alle Tage', weekday:'Mo–Fr', weekend:'Sa–So'};
  const date = value => {
    if (!value) return 'noch keine';
    try { return new Date(value).toLocaleString('de-DE', {timeZone:timeBasis}) + ' ' + timeBasis; }
    catch { return new Date(value).toISOString(); }
  };
  text('learning-period', `Lernfreigabe seit: ${date(cfg.consented_at ? cfg.consented_at * 1000 : null)}. Ältester aufbewahrter Beleg: ${date(progress?.first_evidence_at)}. Letzter Beleg: ${date(progress?.last_evidence_at)}. Keine Aussage über lückenlose Beobachtung.`);
  const progressRoot = byId('learning-progress'); progressRoot.replaceChildren();
  if (!progress?.windows?.length) text('learning-progress', cfg.learning ? 'Noch keine Aktivierungen gespeichert. Prüfe Präsenzquellen und Lernstatus; ein Muster benötigt Belege an mehreren Tagen.' : 'Zum Start Hauptsensoren prüfen und Lernen für diese Zone freigeben.');
  for (const window of progress?.windows || []) {
    const row = document.createElement('p');
    row.textContent = `${String(window.start_hour).padStart(2,'0')}–${String(window.end_hour).padStart(2,'0')} Uhr ${timeBasis} (${dayLabels[window.day_group] || 'alle Tage'}): ${window.events} Aktivierungen an ${window.days} Tagen. ${window.missing_events || window.missing_days ? `Noch mindestens ${window.missing_events} Aktivierungen und ${window.missing_days} weitere Tage in diesem Zeitfenster nötig.` : 'Mindestbelege erreicht – Muster prüfen.'}`;
    progressRoot.append(row);
  }
  const coverage = contextData.coverage;
  const checkLabels={ready:'bereit',disconnected:'Verbindung fehlt',no_source:'Quelle fehlt',partial_source:'Quellen teilweise verfügbar',paused:'pausiert'};
  const checkDetails=Object.entries(coverage?.states || {}).map(([key,count]) => `${checkLabels[key] || key}: ${count}`).join(', ');
  text('learning-coverage', coverage?.sampled_slots
    ? `${coverage.sampled_slots} Fünf-Minuten-Abschnitte mit Prüfungen: ${coverage.ready_only_slots} ohne gemeldete Einschränkung, ${coverage.impaired_slots} mit Einschränkungen. ${coverage.unobserved_slots_between_checks} Abschnitte zwischen erster und letzter Prüfung ohne Stichprobe. Gemeldete Zustände (können sich überlappen): ${checkDetails}. Keine lückenlose Sensorüberwachung und keine Anwesenheitsmessung.`
    : 'Noch keine Stichproben zur Beobachtbarkeit. Ohne Lernfreigabe werden keine gespeichert.');
  const contextRoot = byId('context-observations'); contextRoot.replaceChildren();
  if (!cfg.context_learning) {
    const note = document.createElement('p'); note.textContent='Kontextsammlung ausgeschaltet. Vorhandene Belege laufen aus; Reset löscht sie sofort.'; contextRoot.append(note);
  }
  if (!contextData.context_windows?.length) {
    const note = document.createElement('p'); note.textContent='Noch keine Kontextbelege. Zusätzliche Freigabe und ausdrücklich gespeicherte Licht-/Helligkeitsgruppen erforderlich, um bekannte Werte zu erfassen.'; contextRoot.append(note);
  }
  for (const entry of contextData.context_windows || []) {
    const card = document.createElement('article'); card.className='card';
    const title = document.createElement('strong'); title.textContent=`${entry.start_hour}–${entry.end_hour} Uhr ${timeBasis} · ${dayLabels[entry.day_group] || 'alle Tage'}`;
    const stats = document.createElement('p'); stats.textContent=`${entry.activations} Aktivierungen an ${entry.days} Tagen: Licht an ${entry.light_on}, aus ${entry.light_off}, unbekannt ${entry.light_unknown}. Helligkeit: ${entry.lux_median == null ? 'unbekannt' : Number(entry.lux_median).toLocaleString('de-DE')+' lx Median'} aus ${entry.lux_count} bekannten Werten. Quellen: ${(entry.sources || []).join(', ') || 'keine auswertbaren'}.`;
    const proposal = document.createElement('p'); proposal.textContent=entry.review_ready ? entry.proposal : 'Weitere Belege mit bekanntem Lichtzustand nötig. Keine Schaltfreigabe.';
    card.append(title, stats, proposal); contextRoot.append(card);
  }
  byId('learning-export').href = endpoint(`api/v1/zones/${encodeURIComponent(selectionZone)}/context/export`);
  const root = byId('learned-patterns'); root.replaceChildren();
  text('pattern-summary', 'Noch keine aktuellen Muster.');
  if (!contextData.patterns?.length) { root.textContent = `Noch kein Musterkandidat: mindestens ${progress?.required_events ?? 5} beobachtete Aktivierungen an ${progress?.required_days ?? 3} verschiedenen lokalen Tagen derselben Tagesgruppe im gleichen Zwei-Stunden-Fenster nötig.`; return; }
  const filter = byId('pattern-filter').value;
  const visible = contextData.patterns.filter(p => filter === 'all' || (filter === 'open' ? !p.preference : p.preference === filter));
  text('pattern-summary', `${visible.length} von ${contextData.patterns.length} aktuellen Mustern. Abgelaufene Muster werden nicht als aktuelle Vorschläge angezeigt.`);
  if (!visible.length) root.textContent = 'Keine Muster in dieser Auswahl.';
  for (const pattern of visible) {
    const card = document.createElement('article'); card.className = 'suggestion';
    const title = document.createElement('h3'); title.textContent = pattern.title;
    const stats = pattern.statistics || {};
    const originLabels = {user_context:'Nutzerkontext',parented_service_context:'verketteter Serviceaufruf (mögliche Automation / mögliches Skript)',service_context:'Serviceaufruf ohne belegten Auslöser',derived_context:'abgeleiteter Kontext ohne beobachteten Service',unknown:'unbekannt'};
    const origins = Object.entries(stats.origins || {}).map(([key,count]) => `${originLabels[key] || key}: ${count}`).join(', ') || 'noch keine Herkunftshinweise';
    const evidence = document.createElement('p'); evidence.textContent = `${stats.activation_count ?? 0} Aktivierungen (davon ${stats.historical_activation_count || 0} historisch) an ${stats.distinct_day_count ?? 0} Tagen; insgesamt ${stats.observed_zone_activations ?? 0} erfasst. Quelle: ${(pattern.sources || []).join(', ')}. Herkunftshinweise: ${origins}. Keine Anwesenheitswahrscheinlichkeit; Kontextverkettung beweist weder eine konkrete Automation noch manuelle Bedienung. ${pattern.proposal}`;
    const assessment = document.createElement('p'); assessment.textContent = `Regelstärke: Schwelle erfüllt (Ereignisse ×${pattern.rule_strength?.event_ratio ?? '—'}, Tage ×${pattern.rule_strength?.day_ratio ?? '—'}). Konfidenz: ${pattern.confidence == null ? 'nicht bestimmt' : percent(pattern.confidence)}. Risiko: ${pattern.risk === 'read_only' ? 'nur Prüfung, keine Aktion' : pattern.risk}.`;
    const feedback = document.createElement('p'); feedback.textContent = `Deine Präferenz: ${{accepted:'Passt', rejected:'Nicht hilfreich', later:'Später prüfen'}[pattern.preference] || 'noch offen'}`;
    card.append(title, evidence, assessment, feedback);
    const draftButton = document.createElement('button'); draftButton.type = 'button';
    draftButton.textContent = 'Routine entwerfen';
    draftButton.disabled = selectionBusy || contextEditing || zoneFormOpen || !!selectionDraft?.dirty;
    draftButton.addEventListener('click', () => createRoutineDraft(pattern.id));
    card.append(draftButton);
    const review = contextData.reviews?.find(item => item.pattern_id === pattern.id);
    if (review) {
      const details = document.createElement('details');
      const heading = document.createElement('summary'); heading.textContent = 'Belegkette und Prüfentwurf'; details.append(heading);
      const chain = document.createElement('ol'); chain.setAttribute('aria-label', 'Belegkette');
      for (const node of review.evidence_graph.nodes) {
        const item = document.createElement('li'); item.textContent = node.label; chain.append(item);
      }
      details.append(chain);
      const temporal = document.createElement('p'); temporal.className = 'temporal-check';
      const check = review.temporal_check;
      const checkLabels = {reobserved:'Später erneut beobachtet', insufficient_earlier_evidence:'Frühere Belege reichen noch nicht', insufficient_later_evidence:'Spätere Belege fehlen'};
      temporal.textContent = check
        ? `Zeitlich getrennte Prüfung: ${checkLabels[check.state] || 'Nicht auswertbar'}. Früher: ${check.training_events} Aktivierungen an ${check.training_days} Tagen; später: ${check.later_events} an ${check.later_days} Tagen. Zeitraum ${new Date(check.start * 1000).toLocaleString('de-DE')} bis ${new Date(check.end * 1000).toLocaleString('de-DE')}; Trennung ${new Date(check.split_at * 1000).toLocaleString('de-DE')} (Browserzeit). Gruppierung: ${check.timezone}. Keine Genauigkeitsquote; fehlende Belege können Datenlücken sein.`
        : 'Zeitlich getrennte Prüfung: noch nicht verfügbar.';
      details.append(temporal);
      const warnings = document.createElement('p'); warnings.textContent = review.warnings.join(' '); details.append(warnings);
      const ctx = document.createElement('p'); ctx.textContent = review.context
        ? `Kontext im selben Zeitfenster: Licht an ${review.context.light_on}, aus ${review.context.light_off}, unbekannt ${review.context.light_unknown}. Gleichzeitiges Auftreten ist keine Schaltfolge.`
        : 'Kein passender Lichtkontext für dieses Zeitfenster vorhanden.';
      details.append(ctx);
      const steps = document.createElement('ol');
      for (const step of review.next_steps) { const item = document.createElement('li'); item.textContent = step; steps.append(item); }
      details.append(steps);
      const download = document.createElement('button'); download.type = 'button'; download.textContent = 'Prüfentwurf als JSON exportieren';
      download.addEventListener('click', () => {
        const url = URL.createObjectURL(new Blob([JSON.stringify(review, null, 2)], {type:'application/json'}));
        const link = document.createElement('a'); link.href=url; link.download='pilotsuite-review.json'; link.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      });
      details.append(download); card.append(details);
    }
    for (const [decision, label] of [['accepted','Passt'], ['rejected','Nicht hilfreich'], ['later','Später prüfen']]) {
      const button = document.createElement('button'); button.type = 'button'; button.textContent = label;
      button.setAttribute('aria-pressed', String(pattern.preference === decision));
      button.disabled = selectionBusy || contextEditing;
      button.addEventListener('click', async () => {
        const zone = selectionZone;
        contextGeneration++;
        selectionBusy = true; renderSelection(); renderLearning();
        try { contextData = await json(`api/v1/zones/${encodeURIComponent(zone)}/feedback`, {method:'POST', body:JSON.stringify({pattern_id:pattern.id, decision})}); text('context-message', `Bewertung „${label}“ gespeichert. Keine Automation aktiviert.`); }
        catch(error) { text('context-message', `Feedback nicht bestätigt: ${error.message}`); }
        finally { selectionBusy = false; renderSelection(); renderLearning(); }
      });
      card.append(button);
    }
    root.append(card);
  }
}
const roleKinds = {temperature:['temperature'], humidity:['humidity'], illuminance:['illuminance'], daylight_binary:['daylight_binary'], light:['light'], presence:['motion','occupancy','presence','input_boolean'], climate:['climate'], media:['media_player'], atmosphere:['input_select'], reference_temperature:['temperature']};
byId('pattern-filter').addEventListener('change', renderLearning);
function renderRolePreview() {
  const parts = Object.keys(roleKinds).filter(k => k !== 'reference_temperature').map(role => {
    const count = byId(`role-${role}`).querySelectorAll('input:checked').length;
    const labels = {temperature:'Temperatur', humidity:'Feuchte', illuminance:'Helligkeit', daylight_binary:'Ausreichend Tages-/Raumlicht', presence:'Präsenz / Bewegung', light:'Leuchtenzustand', climate:'Heiz-/Klimaregler', media:'Medienplayer', atmosphere:'Atmosphärenwunsch'};
    return `${labels[role]}: ${count} Hauptsensoren → ${count ? 'automatischer Referenzwert' : 'keine Auswertung'}`;
  });
  text('role-preview', parts.join(' · '));
}
byId('context-edit').addEventListener('click', async () => {
  if (selectionBusy || contextEditing || zoneFormOpen || selectionDraft?.dirty) return;
  contextEditing = true; renderSelection();
  try {
    if (!await loadContext()) return;
    for (const [role, kinds] of Object.entries(roleKinds)) {
      const select = byId(`role-${role}`); select.replaceChildren();
      const current = (contextData.effective_roles || contextData.config.roles)[role] || [];
      const candidates = (contextData.candidates || []).filter(i => kinds.includes(i.suggested_role));
      for (const id of current) if (!candidates.some(i=>i.entity_id===id)) candidates.push({entity_id:id,name:`${id} (aktuell nicht verfügbar / nicht relevant)`});
      if (!candidates.length) select.textContent='Keine bestätigten Sensoren dieses Typs.';
      for (const item of candidates) {
        const label=document.createElement('label'); const input=document.createElement('input'); input.type='checkbox'; input.value=item.entity_id; input.checked=current.includes(item.entity_id);
        input.addEventListener('change', renderRolePreview);
        label.append(input, document.createTextNode(item.name || item.entity_id)); select.append(label);
        const hint=document.createElement('small');
        hint.textContent = item.suggested_role === 'input_boolean'
          ? 'Logischer HA-Helfer · zählt nach ausdrücklicher Zuordnung als eine Präsenzquelle.'
          : item.entity_id;
        label.append(hint);
      }
    }
    renderRolePreview();
    byId('learning-consent').checked=contextData.config.learning;
    byId('detector-events').value=contextData.config.detector?.min_events ?? 5;
    byId('detector-days').value=contextData.config.detector?.min_days ?? 3;
    byId('detector-timezone').value=contextData.config.detector?.timezone || 'UTC';
    byId('detector-day-mode').value=contextData.config.detector?.day_mode || 'all';
    byId('context-learning-consent').checked=!!contextData.config.context_learning;
    byId('context-learning-consent').disabled=!contextData.config.learning;
    byId('context-form').hidden=false;
    byId('context-form').scrollIntoView({block:'start'});
    byId('context-form').querySelector('input:not(:disabled)')?.focus({preventScroll:true});
  } catch(error) { contextEditing=false; text('context-message',error.message); renderSelection(); }
});
byId('learning-consent').addEventListener('change', () => {
  byId('context-learning-consent').disabled=!byId('learning-consent').checked;
  if (!byId('learning-consent').checked) byId('context-learning-consent').checked=false;
});
byId('context-cancel').addEventListener('click', () => { if (selectionBusy) return; contextEditing=false; byId('context-form').hidden=true; text('context-message','Bearbeitung abgebrochen. Der gespeicherte Stand gilt.'); renderSelection(); byId('context-edit').focus(); });
byId('context-form').addEventListener('submit', async event => {
  event.preventDefault(); if (selectionBusy) return;
  const roles=Object.fromEntries(Object.keys(roleKinds).map(k=>[k,[...byId(`role-${k}`).querySelectorAll('input:checked')].map(i=>i.value).sort()]));
  const learning=byId('learning-consent').checked;
  const detector={min_events:Number(byId('detector-events').value), min_days:Number(byId('detector-days').value),timezone:byId('detector-timezone').value.trim(),day_mode:byId('detector-day-mode').value};
  const context_learning=learning && byId('context-learning-consent').checked;
  const contextSourceChanged=['light','illuminance'].some(k => JSON.stringify(roles[k] || []) !== JSON.stringify(contextData.config.roles[k] || []));
  if (contextSourceChanged && contextData.context_windows?.length && !window.confirm('Licht-/Helligkeitsquellen wechseln? Alte Kontextbelege werden gelöscht; Aktivitätsbelege bleiben erhalten.')) return;
  if (context_learning && (!contextData.config.context_learning || contextSourceChanged) && !window.confirm('Lichtzustand und Helligkeit bei Aktivierungen bis 14 Tage speichern? Dies erweitert die Beobachtung, erteilt aber keine Schaltfreigabe.')) return;
  const sourceChanged=JSON.stringify(roles.presence || []) !== JSON.stringify(contextData.config.roles.presence || []);
  if (sourceChanged && contextData.event_count && !window.confirm('Lernquelle wechseln? Vorhandene Lernbelege und Musterfeedback dieser Zone werden gelöscht.')) return;
  if (learning && (!contextData.config.learning || sourceChanged) && !window.confirm(`Lernen für ${roles.presence || 'keine ausgewählte Quelle'} freigeben? Bis 14 Tage Aktivierungen speichern, Zeitfenster in ${detector.timezone}, höchstens 5.000 Belege insgesamt. Keine Aktorsteuerung.`)) return;
  contextGeneration++;
  selectionBusy=true; byId('context-fields').disabled=true; renderSelection();
  try {
    contextData=await json(`api/v1/zones/${encodeURIComponent(selectionZone)}/context`, {method:'PATCH',body:JSON.stringify({revision:contextData.revision,roles,learning,detector,context_learning})});
    contextEditing=false; byId('context-form').hidden=true;
    text('context-message','Rollen und Lernfreigabe gespeichert.');
    selectionBusy=false; await loadSelection(selectionZone); await load();
  } catch(error) { text('context-message',`Speichern nicht bestätigt: ${error.message}. Bei Konflikt abbrechen und neu öffnen.`); }
  finally { selectionBusy=false; byId('context-fields').disabled=false; renderSelection(); renderLearning(); }
});
byId('learning-reset').addEventListener('click', async () => {
  if (selectionBusy || contextEditing || selectionDraft?.dirty || !window.confirm('Lernbelege und Musterfeedback dieser Zone löschen und Lernen ausschalten? Die Entitätenauswahl bleibt erhalten.')) return;
  selectionBusy=true; renderSelection();
  try {
    if (!await loadContext()) return;
    contextGeneration++;
    contextData=await json(`api/v1/zones/${encodeURIComponent(selectionZone)}/context`, {method:'PATCH',body:JSON.stringify({revision:contextData.revision,roles:contextData.config.roles,learning:false,reset:true})});
    text('context-message','Lernbelege und Feedback gelöscht. Lernen ausgeschaltet.');
    selectionBusy=false; await loadSelection(selectionZone); await load();
  } catch(error) { text('context-message',`Löschen nicht bestätigt: ${error.message}`); }
  finally { selectionBusy=false; renderSelection(); renderLearning(); }
});
