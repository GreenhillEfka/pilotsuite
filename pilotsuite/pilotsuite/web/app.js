const byId = (id) => document.getElementById(id);
const endpoint = (path) => new URL(path.replace(/^\//, ""), window.location.href).toString();

async function json(path, options = {}) {
  const response = await fetch(endpoint(path), {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = await response.json();
  if (!response.ok) {
    const error = new Error(body.message || `HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return body;
}

function text(id, value) { byId(id).textContent = value ?? "—"; }
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
  text("habitus-state", `${status.habitus.neuron_count} Neuronen`);
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
    name.textContent = `${item.zone_name ? item.zone_name + ' · ' : ''}${item.name.replaceAll("_", " ")}`;
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
    explanation.textContent = `${item.explanation} Regelstärke ${percent(item.severity)} · Konfidenz ${item.confidence == null ? "nicht bestimmt" : percent(item.confidence)} · Risiko ${item.risk}.`;
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
    const value = item.value === null ? "—" : `${item.value}${item.unit ? ` ${item.unit}` : ""}`;
    for (const content of [item.entity_id, item.kind, value, item.quality]) {
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
  const [status, moods, suggestions, zone] = await Promise.all([
    json("api/v1/status"),
    json("api/v1/moods"),
    json("api/v1/suggestions"),
    json("api/v1/golden-zone"),
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
let zoneExtraSelection = new Set();
const decisionLabels = { relevant: 'Relevant', ignored: 'Ignoriert', unreviewed: 'Ungeprüft' };

function selectionControls() {
  byId('zone-toggle').disabled = zoneToggleBusy || selectionBusy || zoneFormOpen || !selectionZone || !!selectionDraft?.dirty || selectionConflict;
  byId('selection-zone').disabled = selectionBusy || zoneFormOpen || !!selectionDraft?.dirty;
  byId('zone-new').disabled = selectionBusy || zoneFormOpen || !!selectionDraft?.dirty;
  byId('zone-edit').disabled = selectionBusy || zoneFormOpen || !!selectionDraft?.dirty || !selectionZone;
  byId('selection-save').disabled = selectionBusy || zoneFormOpen || selectionConflict || !selectionDraft?.dirty;
  byId('selection-discard').disabled = selectionBusy || zoneFormOpen || !selectionZone;
  byId('selection-recommend').disabled = selectionBusy || zoneFormOpen || selectionConflict || !selectionDraft;
  byId('selection-active').disabled = selectionBusy || zoneFormOpen || selectionConflict || !selectionDraft;
  byId('selection-active').checked = Boolean(selectionDraft?.active);
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
    checkbox.disabled = selectionBusy || zoneFormOpen || selectionConflict;
    checkbox.setAttribute('aria-label', `${item.name || item.entity_id}: relevant`);
    checkbox.addEventListener('change', () => {
      selectionDraft.set(item.entity_id, checkbox.checked ? 'relevant' : 'ignored');
      selectionChanged();
    });
    cells[0].append(checkbox);
    cells[1].textContent = item.name || item.entity_id;
    const id = document.createElement('small'); id.textContent = item.entity_id; cells[1].append(id);
    cells[2].textContent = item.suggested_role || '—';
    cells[3].textContent = item.missing ? 'Nicht im aktuellen Inventar' : (item.state ?? '—');
    cells[4].textContent = decisionLabels[decision] + (item.recommended ? ' · empfohlen' : '');
    if (decision !== 'unreviewed') {
      const reset = document.createElement('button'); reset.type = 'button'; reset.textContent = 'Ungeprüft setzen';
      reset.disabled = selectionBusy || zoneFormOpen || selectionConflict;
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
  text('selection-message', `${Object.keys(selectionDraft.changes).length} geänderte Entitäten. Modus nach Speichern: ${selectionDraft.active ? 'nur bestätigte Auswahl' : 'automatischer Umfang'}. ${selectionDraft.dirty ? 'Ungespeichert.' : 'Keine Änderungen.'}`);
  renderSelection(); renderZoneView();
}

async function loadSelection(zone) {
  if (selectionBusy) return;
  selectionBusy = true; selectionZone = zone; renderSelection();
  try {
    const inventory = await json(`api/v1/selections/${encodeURIComponent(zone)}`);
    selectionDraft = new SelectionDraft(inventory); selectionConflict = false;
    text('selection-message', `${inventory.resolved ? 'Inventar geladen' : 'Zone derzeit nicht aufgelöst'} · Revision ${inventory.revision}. ${inventory.enabled === false ? 'Zone ist deaktiviert. ' : ''}Ungeprüft ist nicht gleich ignoriert.`);
  } catch (error) {
    // Do not display one zone's data under another zone's label.
    if (selectionDraft?.inventory.zone_id !== zone) selectionDraft = null;
    text('selection-message', `Laden fehlgeschlagen: ${error.message}. Neu laden zum Wiederholen.`);
  } finally { selectionBusy = false; renderSelection(); renderZoneView(); }
}

byId('selection-zone').addEventListener('change', event => loadSelection(event.target.value));
byId('selection-active').addEventListener('change', event => {
  selectionDraft.active = event.target.checked;
  selectionChanged();
});
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
  if (selectionDraft.active !== Boolean(selectionDraft.inventory.applied_to_inference)) {
    const count = selectionDraft.inventory.items.filter(item => selectionDraft.decisions.get(item.entity_id) === 'relevant').length;
    const message = selectionDraft.active
      ? `Auswertung auf ${count} bestätigte Entitäten dieser Zone beschränken? Ungeprüfte und ignorierte Entitäten werden ausgeschlossen. Bei leerer Auswahl stehen keine Beobachtungen dieser Zone zur Verfügung.`
      : 'Zum automatischen Umfang zurückkehren? Dann werden auch ignorierte und ungeprüfte Entitäten wieder ausgewertet.';
    if (!window.confirm(message)) return;
  }
  selectionBusy = true; renderSelection();
  try {
    const inventory = await json(`api/v1/selections/${encodeURIComponent(selectionZone)}`, {
      method: 'PATCH', body: JSON.stringify({revision: selectionDraft.inventory.revision, changes: Object.fromEntries(changes), active: selectionDraft.active}),
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
  if (selectionDraft?.dirty || zoneFormOpen) { event.preventDefault(); event.returnValue = ''; }
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
  if (selectionBusy || selectionDraft?.dirty || zoneFormOpen) return;
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
  if (!document.hidden) load().catch((error) => {
    byId("error").textContent = error.message;
    byId("error").hidden = false;
  });
}, 15000);


function renderZoneTabs() {
  const locked = selectionBusy || zoneFormOpen || zoneToggleBusy || !!selectionDraft?.dirty;
  byId('zone-tabs').replaceChildren(...zoneDefinitions.map(zone => {
    const button = document.createElement('button'); button.type = 'button';
    button.id = `tab-${zone.zone_id}`;
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
}

function renderZoneView() {
  const zone = zoneDefinitions.find(z => z.zone_id === selectionZone);
  const result = zoneResults.find(z => z.zone_id === selectionZone);
  text('active-zone-name', zone?.name || 'Noch keine Zone');
  text('zone-toggle', zone?.enabled ? 'Auswertung pausieren' : 'Auswertung starten');
  const note = zone?.profile === 'observe' ? 'Neutrales Profil: Beobachtung und Datenqualität; noch keine gelernten Gewohnheiten.' : 'Erdkeller-Klimaregeln.';
  text('zone-state-message', !zone ? 'Mit + Neue Zone beginnen.' :
    `${zone.enabled ? 'Auswertung aktiv' : 'Pausiert – Entitäten können bereits ausgewählt werden'}. ${result?.evaluated_count ?? 0} Beobachtungen. ${note}${selectionDraft?.dirty ? ' Bitte Auswahl zuerst speichern oder verwerfen.' : ''}${zone.enabled && !result?.evaluated_count ? ' Noch keine auswertbaren Beobachtungen: relevante Entitäten und deren Zustände prüfen.' : ''}`);
  renderMoods(result?.moods || []);
  if (!result?.moods?.length) text('moods', zone?.enabled ? 'Noch keine Bewertung verfügbar.' : 'Zone pausiert. Auswahl speichern und Auswertung starten.');
  renderSuggestions(zone?.enabled ? dashboardSuggestions.filter(item => item.scope?.includes(selectionZone)) : []);
  renderObservations(result?.neurons || []);
  renderZoneTabs();
}

byId('zone-toggle').addEventListener('click', async () => {
  if (selectionBusy || zoneFormOpen || zoneToggleBusy || selectionDraft?.dirty || selectionConflict) return;
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
