const byId = (id) => document.getElementById(id);
const endpoint = (path) => new URL(path.replace(/^\//, ""), window.location.href).toString();

async function json(path, options = {}) {
  const response = await fetch(endpoint(path), {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.message || `HTTP ${response.status}`);
  return body;
}

function text(id, value) { byId(id).textContent = value ?? "—"; }
function percent(value) { return `${Math.round(Number(value || 0) * 100)}%`; }

function renderStatus(status) {
  const ha = status.home_assistant;
  text("ha-state", status.ready ? "Bereit" : "Nicht bereit");
  text("ha-detail", ha.connected ? `Letzter Abgleich ${formatTime(ha.last_refresh_at)}` : (ha.last_error || "Verbindung ausstehend"));
  const zone = status.golden_zone;
  text("zone-state", zone.missing_area_ids.length ? "Bereich fehlt" : `${zone.entity_count} Entitäten`);
  text("zone-detail", zone.resolved_area_ids.join(", ") || `Gesucht: ${zone.requested_area_ids.join(", ")}`);
  text("habitus-state", `${status.habitus.neuron_count} Neuronen`);
  text("habitus-detail", `${status.habitus.suggestion_count} Vorschläge · ${status.habitus.ruleset}`);
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
    fill.style.width = percent(item.score);
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
