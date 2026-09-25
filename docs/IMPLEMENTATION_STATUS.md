# PilotSuite capability and acceptance ledger

## Alpha.24 candidate — integrated daily brief, not installed

PR #54 continues cumulative R2 in the verified full source tree. Pure, bounded
projection validates scope, current selected sources, consent/readiness, coverage,
evidence partitions and preference before highlighting one retained review. Safe
text rendering, activation-time basis checks, same-zone reload invalidation and
focus/draft preservation use the existing context transport and evidence owners.
No migration, new collector or execution permission. Read-only Apply stays denied.

The original failed CI and uncollected test functions are corrected. 41 projector
unit cases plus six actual API/store cases are included in normal unittest discovery.
The full-application browser flow is added to regular CI. Local browser access to
the fixture server was administrator-blocked; only isolated component checks ran
locally. Exact PR/main CI, publication, installation and real Ingress acceptance
must be read separately. Details: DAILY_BRIEF_HARDENING.md.

Fresh native observation confirms Alpha.23 installed/started and ready/connected/
fresh/zone-resolved. Presence/light remain partial. No HA changes during integration.

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
acceptance. Those historical delivery checks used authorized GitHub/HA tools; no local
full-suite or browser run was claimed for the Alpha.22 delivery. Historical focused-test evidence remains in Git/PR history.

## Baseline capabilities

| Capability | Boundary | Separate limitation / acceptance |
|---|---|---|
| Supervisor app / update routine | Canonical version/tree association, scoped backup, native Store refresh | alpha.23 installed/readiness rechecked; no independent image attestation or restore drill |
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

## Remaining acceptance

Finish exact Alpha.24 candidate CI and the existing scoped release routine. Do not
repeat Alpha.23 installation or blindly replay backup/Store operations.
Then authenticate the real UI and verify existing app configuration-read capability
and data preservation separately, without changing permissions or learning consent.
Golden Zone/Recorder coverage, reconnect soak, traceable real habits and a second
unlike consented zone remain independent product gates. Relative humidity alone
never authorizes ventilation. The resumed development mandate remains unchanged.

Contracts: REVIEW_COMPASS.md, REVIEW_NOTES.md, REVIEW_NOTES_USABILITY.md,
ROUTINE_DRAFTS.md, AUTOMATION_INSPECTION.md, AUTOMATION_REVIEW.md,
PATTERN_WORKBENCH.md, HISTORY_AND_TRENDS.md, OBSERVATION_LEARNING.md,
SENSOR_REFERENCES.md and HABITUS_ZONES.md. Historical full ledgers remain in Git and
IMPLEMENTATION_HISTORY_2026-09-23.md; older pending/paused prose is not current state.
