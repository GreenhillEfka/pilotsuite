# PilotSuite capability and acceptance ledger

## Current candidate refinement — 2026-09-24

PR #50 now also contains review-note presentation counts, direct selected recheck,
conservative editor defaults after a changed inspection basis, and saved-text
comparison for concurrent edits. See REVIEW_NOTES_USABILITY.md. This is a bounded
UI refinement of ADR-030, not a new backend summary owner or action approval.
Backend, schema 8, release number alpha.22 and the publication gates are unchanged.
Twelve additional JavaScript cases pass locally; syntax checks pass. The existing
browser-editor contract is extended. Exact complete CI evidence belongs to the
latest PR #50 HEAD, not an earlier successful run. No local browser pass is claimed.
No HA-MCP action or fresh backup receipt was available; no live read/write or update.

## Previous Alpha.22 Store versioning — 2026-09-24

**PR #50**, branch `feat/revision-bound-review-notes`, is now versioned as
**0.1.0-alpha.22**. All five release markers and both changelogs are updated.
**Not merged, published, offered by a verified Store read, or installed.**
The last actual alpha.21 deployment receipt stays unchanged in RELEASE_STATE.json.

That previous continuation changed release metadata, added the note workflow to app
DOCS and ran the existing read-only source preflight in CI for a changed release
version. No additional runtime behavior, HA option, permission or architecture
change was part of versioning. No HA-MCP/native Store action was available in that
tool discovery. No fresh live HA metadata, backup, Store action or household change.

## Implemented review-note package

| Capability | Candidate implementation | Evidence / remaining gate |
|---|---|---|
| Persistent review notes | PlanStore, three dispositions, text up to 2000 characters, 20 notes per draft | Own assessment, not verified individual attribution or permission |
| Change detection | Draft/zone revisions, reference hash, config fingerprint and stale projection | GET/restart says not_rechecked; explicit inspection describes only last read |
| Save validation | Existing selected-automation inspection; no network under projection lock; bounded age and atomic revision/write checks | Synthetic API/store/concurrency tests; live app config-read capability not assumed |
| Conflict-safe editing | Text survives 409/503 and basis reload; changed basis resets editor selection to open; saved-text comparison | Dedicated editor browser contract and existing full-shell browser suite |
| Note overview | Independent assessment/freshness counts and explicit per-note recheck | Presentation only; no autosave, global verdict or additional collection |
| Deletion/export | Note deletion, monotonic tombstone revision, draft-delete revision guard and JSON export | No HA changes, evidence deletion or automatic exports |
| Migration | Existing owner migrates schema 7 to 8 after SQLite backup | Preservation/idempotence regressions; no verified live migration yet |
| Execution boundary | Apply remains denied; notes cannot grant permission | API denial and unchanged evidence/risk tests |

Feature HEAD `47ae62ead032c48ecc8c2c56cb2eae124f0a0a54` passed complete CI
`35923067713`: 215 Python, 16 JavaScript, full-shell browser, note-editor browser and
amd64 container. New source/CI evidence belongs to the **exact alpha.22 PR HEAD**;
read the final receipt in PR #50, not an earlier run. No new local full-suite pass
is claimed. The existing focused/CI evidence and old corrections remain in Git/PR
history. Tests and screenshots are synthetic, not actual household UI acceptance.

## Baseline capabilities

| Capability | Boundary | Separate limitation / acceptance |
|---|---|---|
| Supervisor app / update routine | Canonical version/tree association, scoped backup, native Store refresh | alpha.21 last verified installed; no independent image attestation or restore drill |
| Ingress workspace | Peer-restricted navigation, zone guide, pattern/draft workbench | Synthetic browser tests are not authenticated live acceptance |
| HA projection / readiness | Snapshot, stream, reconnect/backoff, quality/scope separation | Not physical sensor freshness, atomic snapshot or durable event replay |
| Habitus zones / roles | Stable logical zones, areas/extras, confirmed-only groups | No shadow topology or invented sensors |
| Typed references | Climate normalization, median/spread, illuminance and saved presence groups | Actual mapping/coverage review remains |
| Learning / context | Consent-gated bounded evidence and coarse ephemeral origin correlation | Counts, confidence, preference, strength and risk remain separate |
| History | Transient history/statistics and explicit interval-scoped evidence import | No Recorder clone or assumed coverage |
| Pattern workbench | Derived explanations and chronological reobservation | Not unbiased predictive validation or executable plans |
| Routine drafts | User intent/targets, revisions, source refresh, export/delete | Survive learning reset; schema 8 only in the candidate |
| Automation comparison | Bounded related-entity review and selected structural inspection | No semantic equivalence/safety verdict, template evaluation or automatic scan |
| Multi-user policy | Beyond shared revision-protected notes, planned | No inferred personal identity |
| Full brain graph / HA adapter / Assist / LLM / RAG | Planned or optional | No second semantic owner or direct LLM action path |
| HomeKit / broad Dev-Wiki UI / presets | Deferred | Inventory and actual capability first |
| Action catalog / execution / runtime recovery | Future work; apply denied | Operational app backup is not a runtime transaction engine |

## Publication gate and next step

Fresh installed-version information and completed PilotSuite-only app/data/options
backup verification are still required before publication. The last observed
auto_update setting was true; publishing could make the release eligible for an
automatic update. Do not change that option or treat the historical alpha.18 backup
`ae7a3fba` as a new alpha.21 recovery point. Missing tool access does not invalidate
the documented working Store route.

Versioning is complete; next verify backup and exact candidate source/CI, main/open
work and version uniqueness, then merge only with those gates satisfied. Verify main
CI, use the normal Store refresh if needed, update once and check runtime. No custom
bridge, speculative restart or weakened permissions. Follow RELEASE_RUNBOOK.md.
Actual authenticated assets/API/temporal/draft/inspection/note UI, existing app
read rights, Golden Zone/Recorder coverage, reconnect soak, traceable real habit
and a second unlike zone remain separately pending. No extra consent in tests.
Relative humidity alone never authorizes ventilation.

Contracts: REVIEW_NOTES.md, REVIEW_NOTES_USABILITY.md, ROUTINE_DRAFTS.md,
AUTOMATION_INSPECTION.md, AUTOMATION_REVIEW.md, PATTERN_WORKBENCH.md,
HISTORY_AND_TRENDS.md, OBSERVATION_LEARNING.md, SENSOR_REFERENCES.md and HABITUS_ZONES.md.
The prior complete candidate ledger is preserved at `47ae62e`; the old full ledger
stays unchanged in IMPLEMENTATION_HISTORY_2026-09-23.md. Old installed versions and
unversioned-candidate statements are historical, not current measurements.
