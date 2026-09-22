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
    name.textContent = item.name.replaceAll("_", " ");
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
  renderMoods(moods.items);
  renderSuggestions(suggestions.items);
  renderObservations(zone.neurons || []);
  if (!selectionInitialized) {
    selectionInitialized = true;
    const zones = status.golden_zone.requested_area_ids;
    byId('selection-zone').replaceChildren(...zones.map(id => {
      const option = document.createElement('option');
      option.value = id; option.textContent = id; return option;
    }));
    if (zones.length) await loadSelection(zones[0]);
    else text('selection-message', 'Keine Zone konfiguriert.');
  }
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
const decisionLabels = { relevant: 'Relevant', ignored: 'Ignoriert', unreviewed: 'Ungeprüft' };

function selectionControls() {
  byId('selection-zone').disabled = selectionBusy || !!selectionDraft?.dirty;
  byId('selection-save').disabled = selectionBusy || selectionConflict || !selectionDraft?.dirty;
  byId('selection-discard').disabled = selectionBusy || !selectionZone;
  byId('selection-recommend').disabled = selectionBusy || selectionConflict || !selectionDraft;
  byId('selection-active').disabled = selectionBusy || selectionConflict || !selectionDraft;
  byId('selection-active').checked = Boolean(selectionDraft?.active);
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
    checkbox.disabled = selectionBusy || selectionConflict;
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
      reset.disabled = selectionBusy || selectionConflict;
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
  renderSelection();
}

async function loadSelection(zone) {
  if (selectionBusy) return;
  selectionBusy = true; selectionZone = zone; renderSelection();
  try {
    const inventory = await json(`api/v1/selections/${encodeURIComponent(zone)}`);
    selectionDraft = new SelectionDraft(inventory); selectionConflict = false;
    text('selection-message', `${inventory.resolved ? 'Inventar geladen' : 'Zone derzeit nicht aufgelöst'} · Revision ${inventory.revision}. Ungeprüft ist nicht gleich ignoriert.`);
  } catch (error) {
    // Do not display one zone's data under another zone's label.
    if (selectionDraft?.inventory.zone_id !== zone) selectionDraft = null;
    text('selection-message', `Laden fehlgeschlagen: ${error.message}. Neu laden zum Wiederholen.`);
  } finally { selectionBusy = false; renderSelection(); }
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
    text('selection-message', `Gespeichert. ${inventory.applied_to_inference ? 'Bestätigte Auswahl ist für die Auswertung aktiv.' : 'Automatischer Umfang bleibt aktiv.'}`);
    await load();
  } catch (error) {
    selectionConflict = error.status === 409;
    text('selection-message', selectionConflict
      ? 'Zwischenzeitlich geändert. Dein Entwurf bleibt sichtbar. Bitte verwerfen / neu laden und Auswahl erneut prüfen.'
      : `Speichern nicht bestätigt: ${error.message}. Entwurf bleibt erhalten; bei Unsicherheit neu laden.`);
  } finally { selectionBusy = false; renderSelection(); }
});
window.addEventListener('beforeunload', event => {
  if (selectionDraft?.dirty) { event.preventDefault(); event.returnValue = ''; }
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
