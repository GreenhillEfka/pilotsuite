# Changelog

## [0.1.0-alpha.16] - 2026-09-23

- Zonen-Assistent mit konkretem nächsten Schritt und aufklappbarer Einrichtungsprüfung.
- Unterscheidet fehlende Quellen, pausierte Auswertung, Verbindung und freiwillige Lernfreigabe.
- Zeigt fehlende Belege je Zeitfenster ohne Zeitfenster zu vermischen oder Fertigdatum vorherzusagen.
- Direkte Navigation zu bestehenden Einstellungen; keine automatische Aktivierung oder neue Datensammlung.

## [0.1.0-alpha.15] - 2026-09-23

- Direkte Bereichsnavigation, konsistente deutsche Begriffe und mobile Formulare.
- Bearbeitungs- und Feedbackbestätigungen, Importgründe und klare Datumsvalidierung.
- Keine fremden Lernangaben nach Zonenwechsel; Tastaturfokus besser erhalten.
- Erweiterte Browserregression für Navigation und drei Bildschirmbreiten.
- Verspätete Kontextantworten überschreiben keine neueren Anzeigen oder Feedbacks.
- Konsistente Versionsmarker; verbindlicher Release-Ablauf und lesende Quellprüfung.

All notable changes follow [Semantic Versioning](https://semver.org/).

## [0.1.0-alpha.14] - 2026-09-23

- Pattern workbench: preference filters, evidence chains, matching light context and JSON review briefs.
- Review exports remain non-executable; feedback grants no action permission.
- Controlled Recorder metadata and history timeout failures.

## [0.1.0-alpha.13] - 2026-09-23

- Convert Home Assistant connection failures during scoped history and statistics
  requests into the existing bounded history error instead of a generic HTTP 500.
- Treat malformed Home Assistant WebSocket text frames as typed protocol errors.
- Preserve successful history responses, SQLite schema 6, consent, roles and the
  hard read-only boundary.

## [0.1.0-alpha.12] - 2026-09-23

- Add consent-gated, memory-only correlation between Home Assistant service and
  state contexts; persist only coarse origin categories without identifiers.
- Add scoped zone-history graphs for recorded states and hourly long-term statistics.
- Show virtual zone references, source ranges, presence/light timelines, weekly
  activity rasters and chronological re-observation checks with explicit gaps.
- Add one-time, interval-scoped retrospective activity consent. Import only
  confirmed presence activations into the existing activity-v1 store; never infer
  historical light context or actuation intent.
- Migrate to SQLite schema 6 with a pre-migration backup, import receipts and
  provenance; deduplicate imported evidence against live and previous evidence.
- Keep learning, historical import and every Home Assistant action disabled unless
  separately authorized. This release remains hard read-only.

## [0.1.0-alpha.11] - 2026-09-23

- Add per-zone activity thresholds, local IANA timezones and weekday/weekend grouping.
- Show source details, learning progress and bounded observation checkpoints.
- Add separately consented light/lux context at activity events, with explicit unknowns.
- Preserve evidence on parameter edits; bind preference to the detector configuration.
- Migrate to SQLite schema 5 with a pre-migration database backup; preserve roles and choices.
- Extend export, reset and retention to the new evidence. Context learning defaults off.
- No HA actuation. Downgrading requires restoring the matching App-and-data backup.

## [0.1.0-alpha.10] - 2026-09-23

- Separate activity observation statistics, deterministic rule-threshold ratios,
  nullable statistical confidence, read-only risk and durable user preference.
- Keep preference feedback independent from evidence counts and rule strength.
- Show every assessment dimension explicitly in the Ingress candidate card.
- Retain earlier flat activity fields as deprecated alpha API compatibility aliases.
- Add synthetic regression coverage; no production learning consent or HA action.

## [0.1.0-alpha.9] - 2026-09-22

- Derive virtual zone references from main sensor groups, including illuminance.
- Use the same explicit presence group for summary and consented learning.
- Preserve empty groups; display effective defaults before editing.
- Validate lux units and values; distinguish external comparison temperatures.
- Add API persistence, role-group and mobile browser regressions.

## [0.1.0-alpha.8] - 2026-09-22

- Fix direct module startup: define all role/learning API handlers before calling main.
- Add a real subprocess entrypoint regression: starts python -m pilotsuite.app and
  checks loopback HTTP health, using isolated data and no Home Assistant credentials.
- alpha.7 failed at route registration on the real App before startup/migration;
  alpha.8 supersedes it. Role groups and opt-in learning otherwise unchanged.

## [0.1.0-alpha.7] - 2026-09-22

- Evaluate confirmed relevant entities only; reject the legacy automatic bypass.
- Show compact per-zone capability cards and separate candidate/decision/evaluation counts.
- Add role groups (up to 20 sources): climate median with min/max, visible missing data,
  separate reference temperatures and presence-any logic without false absence.
- Add opt-in recurring-activity candidates from live off-to-on events, with 5-minute
  zone deduplication, 14-day retention and a global 5,000-evidence limit.
- Persist independent pattern feedback; expose consent, revoke, reset and export.
- SQLite schema 4 backs up older schemas; never infer roles, decisions or learning consent.
- No actor control, person identification, occupancy probability or causal claims.

## [0.1.0-alpha.6] - 2026-09-22

- Add visible tabs per Habitus zone with scoped evaluation, suggestions and observations.
- Add direct start/pause and name/source editing; fetch shared revision before activation.
- Replace HA-area multi-select with checkboxes for composing zones such as Bad + Toilette.
- Separate zone activation from the advanced entity-selection mode; explain unsaved edits.
- Preserve zone definitions, decisions, neutral profiles and the HA read-only boundary.
- Extend browser regression for multi-area creation, activation, rename, pause, conflicts,
  reload and tab isolation. Real HA interactive acceptance remains separate.

## [0.1.0-alpha.5] - 2026-09-22

- Add logical Habitus zones with stable IDs, multiple area sources and extra entities.
- Add zone editor and persistent relevant/ignored/unreviewed entity selection.
- Keep per-zone inference isolated and deduplicate global entity counts.
- Add SQLite schema 3, pre-migration backups, shared revision conflict protection,
  JSON export and a journal bounded to 5,000 transactions.
- New UI-created zones start paused with a neutral profile and curated selection.
- Preserve existing zone behavior on first migration; HA actuation stays disabled.
- Verify with 46 backend tests, four JavaScript tests, browser tests and amd64 CI build.
- Learning, contextual role priorities, import and permanent deletion remain deferred.

## [0.1.0-alpha.4] - 2026-09-22

- Separate transport readiness from zone and capability availability.
- Report missing climate evidence as null / not assessable, not zero.
- Exclude buttons and unrelated diagnostics from climate uncertainty.
- Display capability-specific availability and log safe readiness summaries.
- Add four regression tests (28 total); no HA actuation enabled.

## [0.1.0-alpha.3] - 2026-09-22

### Fixed
- Route repeated Ingress slashes internally without losing the external prefix.
  Omitting the default ingress_entry alone was not a proven fix.
- Normalize climate units and reject invalid readings; missing climate data is not stable.
- Separate severity from unknown confidence; keep proposal identity stable.
- Track event stream health, resynchronize after reconnect and back off on clean close.
- Reject older state updates and exclude disabled entities from the projection.

### Security
- Restrict UI/API to the Ingress TCP peer; allow loopback liveness probes only.
- Home Assistant mutations remain hard-disabled.

### Added
- Reviewed full vision, capability/acceptance ledger and revised learning-first roadmap.
- Regression tests and periodic dashboard refresh.
- Real Supervisor/browser acceptance is still pending.

## [0.1.0-alpha.2] - 2026-09-22

### Fixed

- Raised the bounded Home Assistant WebSocket receive limit to 32 MiB so larger
  state and registry snapshots do not close the connection at `aiohttp`'s
  4 MiB default.
- Report the actual WebSocket message type and transport error when a snapshot
  connection fails.

## [0.1.0-alpha.1] - 2026-09-22

### Added

- Canonical PilotSuite v21 repository and project memory
- Installable Home Assistant Supervisor App skeleton
- REST/WebSocket Home Assistant connector
- Registry-backed world model and area resolver
- Erdkeller Golden Zone configuration
- Deterministic neurons, moods, synapses, and suggestions
- Read-only policy gate and dry-run plans
- Ingress dashboard, API, audit trail, tests, and CI

### Security

- Hard-disabled Home Assistant mutations for the complete alpha release
- No Home Assistant config mounts, host networking, privileged capabilities, or secret persistence
