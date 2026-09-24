# PilotSuite capability and acceptance ledger

## Alpha.23 candidate — PR #52, not deployed

Prüfkompass is integrated with the existing PlanStore, canonical current report,
explicit comparison/inspection routes, note-save response and routine workbench.
Five independently explained sections, one basis-checked next action, transient
zone filter/sort, explicit export, responsive panels and preserved input/focus.
No new SQLite schema, data owner, background HA scan, learning or Apply permission.
The routine-drafts HEAD request now follows its GET path (regression covered).

247 Python and 48 JavaScript tests passed locally against the real repository.
New full-app synthetic browser test is wired into CI alongside both existing
browser flows; local navigation is blocked by administrative policy, not bypassed.
Exact candidate CI and release status belong in PR #52. No new live acceptance,
backup, deployment or version switch occurred yet. Production is the Alpha.22
receipt below. See REVIEW_COMPASS.md and DEVELOPMENT_MANDATE.md.


## Current delivery — 2026-09-24

**Alpha.22 is published, offered by the normal Store, installed and started.**
PR #50 candidate `ca6ba76f90c706cd3f7158aa07eec1605c81089a` was merged without force
at `7990f5a3225aec53548dd8cb5bc79e74707b9fd9`. Candidate CI `35928225010` and exact
release main CI `35929637405` completed successfully, including tests, both browser
flows and amd64 build. Candidate logs confirm 215 Python and 28 JavaScript tests.
Release/source contracts passed; the application tree is
`0d427053cdf246e63e044a11c15494f18dbeab08`. No code or version change in this delivery.

Fresh PilotSuite-only backup `33908293` completed before publication; native details
verified alpha.21, 54005760 bytes, no HA configuration/database/folders, no failed
components and no key requirement. One native Store refresh offered alpha.22; one
matching app update completed. Metadata and logs verified version/start,
hard_read_only, readiness, stream, fresh snapshot and resolved zone. Options and
auto_update=true remained unchanged. No other app, HA configuration, consent,
permission or actor was changed. No additional restart, rebuild or restore drill.

RELEASE_STATE.json is the actual deployment receipt. Authenticated live browser
acceptance, independent installed-image/checkout attestation and independent live
migration/data-preservation inspection are not implied by these runtime checks.
The handoff changes documentation only; it does not replace the deployed app tree.

## Implemented review-note package

| Capability | Delivered implementation | Evidence / remaining gate |
|---|---|---|
| Persistent review notes | PlanStore, three dispositions, text up to 2000 characters, 20 notes per draft | Own assessment, not verified individual attribution or permission |
| Change detection | Draft/zone revisions, reference hash, config fingerprint and stale projection | GET/restart says not_rechecked; explicit inspection describes only last read |
| Save validation | Existing selected-automation inspection; no network under projection lock; bounded age and atomic revision/write checks | Synthetic API/store/concurrency tests; live app config-read capability not assumed |
| Conflict-safe editing | Text survives 409/503 and basis reload; changed basis resets editor selection to open; saved-text comparison | Dedicated editor browser contract and existing full-shell browser suite |
| Note overview | Independent assessment/freshness counts and explicit per-note recheck | Presentation only; no autosave, global verdict or additional collection |
| Deletion/export | Note deletion, monotonic tombstone revision, draft-delete revision guard and JSON export | No HA changes, evidence deletion or automatic exports |
| Migration | Existing owner migrates schema 7 to 8 after SQLite backup | Synthetic preservation/idempotence regressions; no independent live database inspection |
| Execution boundary | Apply remains denied; notes cannot grant permission | API denial and unchanged evidence/risk tests |

ADR-030 and REVIEW_NOTES_USABILITY.md define the delivered package and editor
refinement. Exact candidate and release-main CI are recorded above, not replaced by
earlier feature runs. Tests and screenshots are synthetic, not actual household UI
acceptance. The delivery used authorized GitHub/HA tools; no local full-suite or
browser run is claimed. Historical focused-test evidence remains in Git/PR history.

## Baseline capabilities

| Capability | Boundary | Separate limitation / acceptance |
|---|---|---|
| Supervisor app / update routine | Canonical version/tree association, scoped backup, native Store refresh | alpha.22 installed/runtime verified; no independent image attestation or restore drill |
| Ingress workspace | Peer-restricted navigation, zone guide, pattern/draft workbench | Synthetic browser tests are not authenticated live acceptance |
| HA projection / readiness | Snapshot, stream, reconnect/backoff, quality/scope separation | Not physical sensor freshness, atomic snapshot or durable event replay |
| Habitus zones / roles | Stable logical zones, areas/extras, confirmed-only groups | No shadow topology or invented sensors |
| Typed references | Climate normalization, median/spread, illuminance and saved presence groups | Actual mapping/coverage review remains |
| Learning / context | Consent-gated bounded evidence and coarse ephemeral origin correlation | Counts, confidence, preference, strength and risk remain separate |
| History | Transient history/statistics and explicit interval-scoped evidence import | No Recorder clone or assumed coverage |
| Pattern workbench | Derived explanations and chronological reobservation | Not unbiased predictive validation or executable plans |
| Routine drafts | User intent/targets, revisions, source refresh, export/delete | Survive learning reset; schema 8 shipped, live data-preservation acceptance separate |
| Automation comparison | Bounded related-entity review and selected structural inspection | No semantic equivalence/safety verdict, template evaluation or automatic scan |
| Multi-user policy | Beyond shared revision-protected notes, planned | No inferred personal identity |
| Full brain graph / HA adapter / Assist / LLM / RAG | Planned or optional | No second semantic owner or direct LLM action path |
| HomeKit / broad Dev-Wiki UI / presets | Deferred | Inventory and actual capability first |
| Action catalog / execution / runtime recovery | Future work; apply denied | Operational app backup is not a runtime transaction engine |

## Remaining acceptance and next step

The Alpha.22 publication, Store offering, installation and runtime gates are complete.
If the installed version still matches alpha.22, do not repeat backup/update/rebuild/
restart. Follow RELEASE_RUNBOOK.md for future releases, with a fresh scoped backup
before publication while auto_update is enabled. `33908293` is this delivery's
alpha.21 recovery point; the historical `ae7a3fba` contains alpha.18. No recovery ran.

Actual authenticated assets/API/temporal/draft/inspection/note UI, existing app
read rights, Golden Zone/Recorder coverage, reconnect soak, traceable real habits
and a second unlike zone remain separately pending. No extra consent or household
scan in tests; no permission weakening to obtain acceptance. Relative humidity
alone never authorizes ventilation. A future derived review-requirements summary
is distinct from presentation-only note counters and would not authorize execution.
No such feature was implemented as part of delivery. A paused recurring task stays
paused unless explicitly resumed.

Contracts: REVIEW_NOTES.md, REVIEW_NOTES_USABILITY.md, ROUTINE_DRAFTS.md,
AUTOMATION_INSPECTION.md, AUTOMATION_REVIEW.md, PATTERN_WORKBENCH.md,
HISTORY_AND_TRENDS.md, OBSERVATION_LEARNING.md, SENSOR_REFERENCES.md and HABITUS_ZONES.md.
The prior candidate ledger is preserved at `ca6ba76`; the old full ledger remains
in IMPLEMENTATION_HISTORY_2026-09-23.md. Earlier access blockers and unpublished
candidate statements are historical, not current measurements.
