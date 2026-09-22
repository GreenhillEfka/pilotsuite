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
let zoneExtraSelection = new Set();
const decisionLabels = { relevant: 'Relevant', ignored: 'Ignoriert', unreviewed: 'Ungeprüft' };

function selectionControls() {
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
    cells[2].textContent = item.suggested_role || '—';
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
  renderSelection(); renderZoneView();
}

async function loadSelection(zone) {
  if (selectionBusy) return;
  selectionBusy = true; selectionZone = zone; renderSelection();
  try {
    const inventory = await json(`api/v1/selections/${encodeURIComponent(zone)}`);
    selectionDraft = new SelectionDraft(inventory); selectionConflict = false;
    await loadContext();
    text('selection-message', `${inventory.resolved ? 'Inventar geladen' : 'Zone derzeit nicht aufgelöst'} · Revision ${inventory.revision}. ${inventory.enabled === false ? 'Zone ist deaktiviert. ' : ''}Ungeprüft ist nicht gleich ignoriert.`);
  } catch (error) {
    // Do not display one zone's data under another zone's label.
    if (selectionDraft?.inventory.zone_id !== zone) selectionDraft = null;
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
  if (!document.hidden) load().catch((error) => {
    byId("error").textContent = error.message;
    byId("error").hidden = false;
  });
}, 15000);


function renderZoneTabs() {
  const locked = selectionBusy || zoneFormOpen || contextEditing || zoneToggleBusy || !!selectionDraft?.dirty;
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
    value.textContent = !info ? 'Zone pausiert / keine Bewertung' : (info.status === 'available' || info.status === 'partial')
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
  contextData = await json(`api/v1/zones/${encodeURIComponent(selectionZone)}/context`);
  renderLearning();
}
function renderLearning() {
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
  const progress = contextData.progress;
  const date = value => value ? new Date(value).toLocaleString('de-DE', {timeZone:'UTC'}) + ' UTC' : 'noch keine';
  text('learning-period', `Lernfreigabe seit: ${date(cfg.consented_at ? cfg.consented_at * 1000 : null)}. Ältester aufbewahrter Beleg: ${date(progress?.first_evidence_at)}. Letzter Beleg: ${date(progress?.last_evidence_at)}. Keine Aussage über lückenlose Beobachtung.`);
  const progressRoot = byId('learning-progress'); progressRoot.replaceChildren();
  for (const window of progress?.windows || []) {
    const row = document.createElement('p');
    row.textContent = `${String(window.start_hour).padStart(2,'0')}–${String(window.end_hour).padStart(2,'0')} Uhr UTC: ${window.events} Aktivierungen an ${window.days} Tagen. ${window.missing_events || window.missing_days ? `Noch mindestens ${window.missing_events} Aktivierungen und ${window.missing_days} weitere Tage in diesem Zeitfenster nötig.` : 'Mindestbelege erreicht – Muster prüfen.'}`;
    progressRoot.append(row);
  }
  byId('learning-export').href = endpoint(`api/v1/zones/${encodeURIComponent(selectionZone)}/context/export`);
  const root = byId('learned-patterns'); root.replaceChildren();
  if (!contextData.patterns?.length) { root.textContent = `Noch kein Musterkandidat: mindestens ${progress?.required_events ?? 5} beobachtete Aktivierungen an ${progress?.required_days ?? 3} verschiedenen UTC-Tagen im gleichen Zwei-Stunden-Fenster nötig.`; return; }
  for (const pattern of contextData.patterns) {
    const card = document.createElement('article'); card.className = 'suggestion';
    const title = document.createElement('h3'); title.textContent = pattern.title;
    const evidence = document.createElement('p'); evidence.textContent = `${pattern.events} Aktivierungen an ${pattern.days.length} Tagen; insgesamt ${pattern.observed_total} erfasst. Quelle: ${(pattern.sources || []).join(', ')}. Keine Anwesenheitswahrscheinlichkeit. ${pattern.proposal}`;
    const feedback = document.createElement('p'); feedback.textContent = `Dein Feedback: ${{accepted:'Passt', rejected:'Nicht hilfreich', later:'Später prüfen'}[pattern.feedback] || 'noch offen'}`;
    card.append(title, evidence, feedback);
    for (const [decision, label] of [['accepted','Passt'], ['rejected','Nicht hilfreich'], ['later','Später prüfen']]) {
      const button = document.createElement('button'); button.type = 'button'; button.textContent = label;
      button.disabled = selectionBusy || contextEditing;
      button.addEventListener('click', async () => {
        const zone = selectionZone;
        selectionBusy = true; renderSelection(); renderLearning();
        try { contextData = await json(`api/v1/zones/${encodeURIComponent(zone)}/feedback`, {method:'POST', body:JSON.stringify({pattern_id:pattern.id, decision})}); }
        catch(error) { text('context-message', `Feedback nicht bestätigt: ${error.message}`); }
        finally { selectionBusy = false; renderSelection(); renderLearning(); }
      });
      card.append(button);
    }
    root.append(card);
  }
}
const roleKinds = {temperature:['temperature'], humidity:['humidity'], illuminance:['illuminance'], light:['light'], presence:['motion','occupancy','presence'], reference_temperature:['temperature']};
function renderRolePreview() {
  const parts = Object.keys(roleKinds).filter(k => k !== 'reference_temperature').map(role => {
    const count = byId(`role-${role}`).querySelectorAll('input:checked').length;
    const labels = {temperature:'Temperatur', humidity:'Feuchte', illuminance:'Helligkeit', presence:'Präsenz / Bewegung', light:'Licht'};
    return `${labels[role]}: ${count} Hauptsensoren → ${count ? 'automatischer Referenzwert' : 'keine Auswertung'}`;
  });
  text('role-preview', parts.join(' · '));
}
byId('context-edit').addEventListener('click', async () => {
  if (selectionBusy || contextEditing || zoneFormOpen || selectionDraft?.dirty) return;
  contextEditing = true; renderSelection();
  try {
    await loadContext();
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
      }
    }
    renderRolePreview();
    byId('learning-consent').checked=contextData.config.learning;
    byId('detector-events').value=contextData.config.detector?.min_events ?? 5;
    byId('detector-days').value=contextData.config.detector?.min_days ?? 3;
    byId('context-form').hidden=false;
  } catch(error) { contextEditing=false; text('context-message',error.message); renderSelection(); }
});
byId('context-cancel').addEventListener('click', () => { if (selectionBusy) return; contextEditing=false; byId('context-form').hidden=true; renderSelection(); });
byId('context-form').addEventListener('submit', async event => {
  event.preventDefault(); if (selectionBusy) return;
  const roles=Object.fromEntries(Object.keys(roleKinds).map(k=>[k,[...byId(`role-${k}`).querySelectorAll('input:checked')].map(i=>i.value).sort()]));
  const learning=byId('learning-consent').checked;
  const detector={min_events:Number(byId('detector-events').value), min_days:Number(byId('detector-days').value)};
  const sourceChanged=JSON.stringify(roles.presence || []) !== JSON.stringify(contextData.config.roles.presence || []);
  if (sourceChanged && contextData.event_count && !window.confirm('Lernquelle wechseln? Vorhandene Lernbelege und Musterfeedback dieser Zone werden gelöscht.')) return;
  if (learning && (!contextData.config.learning || sourceChanged) && !window.confirm(`Lernen für ${roles.presence || 'keine ausgewählte Quelle'} freigeben? Bis 14 Tage Aktivierungen speichern, Zeitfenster in UTC, höchstens 5.000 Belege insgesamt. Keine Aktorsteuerung.`)) return;
  selectionBusy=true; byId('context-fields').disabled=true; renderSelection();
  try {
    contextData=await json(`api/v1/zones/${encodeURIComponent(selectionZone)}/context`, {method:'PATCH',body:JSON.stringify({revision:contextData.revision,roles,learning,detector})});
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
    await loadContext();
    contextData=await json(`api/v1/zones/${encodeURIComponent(selectionZone)}/context`, {method:'PATCH',body:JSON.stringify({revision:contextData.revision,roles:contextData.config.roles,learning:false,reset:true})});
    text('context-message','Lernbelege und Feedback gelöscht. Lernen ausgeschaltet.');
    selectionBusy=false; await loadSelection(selectionZone); await load();
  } catch(error) { text('context-message',`Löschen nicht bestätigt: ${error.message}`); }
  finally { selectionBusy=false; renderSelection(); renderLearning(); }
});
