# PilotSuite capability and acceptance ledger

## Development candidate — review notes

**Draft PR #50**, branch `feat/revision-bound-review-notes`, adds the bounded
review-note increment (ADR-030). **Not merged, versioned, published or installed.**
The last deployed alpha.21 receipt is retained in RELEASE_STATE.json; it was not
refreshed because HA-MCP was unavailable in tool discovery during this continuation.
No new backup or HA change was performed.

| Capability | Candidate implementation | Evidence / remaining gate |
|---|---|---|
| Persistent review notes | PlanStore, three user dispositions, text up to 2000 characters, 20 notes per draft | Explicit own assessment, not authenticated individual attribution or action permission |
| Change detection | Bound draft/zone revisions, reference hash and config fingerprint; conservative stale projection | GET/restart says not_rechecked; fresh inspection describes only last read |
| Save validation | Existing selected-automation inspection; no network under projection lock; bounded inspection age and atomic SQLite revision/write checks | Synthetic API/store/concurrency tests; live app config-read capability not assumed |
| Conflict-safe editing | Input preserved on 409/503; reload basis without discarding text; explicit save | Dedicated synthetic browser editor contract plus existing full-shell browser suite |
| Scoped deletion/export | Explicit note deletion, monotonic tombstone revision, draft-delete review-revision guard, combined JSON export | No HA writes, no evidence deletion, no automatic export |
| Storage migration | Schema 7 to 8 through existing owner, SQLite backup before additive table | Migration/preservation/idempotence regressions; no live migration yet |
| Execution boundary | Existing apply remains denied; notes cannot grant permission | API test confirms denial and unchanged evidence/risk |

Local evidence: six Python validation/projection tests and seven JavaScript state
regressions pass; compilation and syntax checks pass. Seventeen additional
backend/API tests and the browser editor flow are included in repository CI.
The initial run passed all 23 new Python cases, all 16 JavaScript tests, the existing
full-shell browser suite and amd64 container. Two legacy schema assertions and the
standalone browser fixture's missing UTF-8 declaration were corrected afterwards.
Read the **latest exact HEAD result and final receipt in PR #50**, not an earlier
run or this paragraph as a final acceptance claim. Local synthetic Chromium
navigation was blocked before execution; no local browser success is claimed.
No real household data in tests.

## Previously implemented baseline, retained unchanged in purpose

| Capability | Implemented boundary | Separate acceptance / limitation |
|---|---|---|
| Supervisor app and update routine | Canonical version/tree association, scoped operational backup, native Store refresh | alpha.21 last verified installed; no independent image attestation or restore drill |
| Ingress UI | Peer-restricted navigation, zone guide, pattern/draft workbench | Full synthetic browser regression; actual current authenticated UI still pending |
| HA projection / readiness | Snapshot, stream, reconnect/backoff, quality/scope separation | Not physical sensor freshness, not atomic HA snapshot or durable stream replay |
| Habitus zones / roles | Stable logical zones, multiple areas/extras, confirmed-only source groups | No independent shadow topology or invented sensors |
| Sensor references | Climate normalization, median/spread, illuminance and saved presence groups | Mapping/coverage must be reviewed in actual zones |
| Learning / context | Consent-gated bounded activity evidence, coarse ephemeral origin correlation | Counts, confidence, rule strength, preference and risk separate; no causal claim |
| Targeted history | Transient history/statistics, explicit interval-scoped import into existing evidence owner | No Recorder clone or implied historical coverage |
| Pattern workbench | Derived explanations and temporal reobservation | No unbiased predictive validation or executable action plan |
| Routine drafts | User intent/targets, revision guards, explicit source refresh, export/delete | Drafts survive learning reset; schema 7 baseline, 8 only in this candidate |
| Automation comparison | Explicit bounded transient related-entity review and selected structural inspection | No semantic equivalence/safety verdict, template evaluation or automatic household scan |
| Multi-user conflict policy | Planned beyond shared revision-protected workspace | No inferred personal identity |
| Full brain graph / native HA adapter / Assist / LLM / RAG | Planned or optional | No separate semantic owner or direct LLM action path |
| HomeKit / broad Dev-Wiki UI / presets | Deferred | Inventory and actual provider capability first |
| Action catalog / governed execution / runtime recovery | Future work; current apply denied | Operational app backups are not the future runtime transaction engine |

## Delivery and live acceptance

Current source baseline: PR #49 merge `c3e87fb81a24267b8584f2d68df25bd8f9539aba`.
Prior alpha.21 release: `1223f96f45053f7bf3d509bd7ad72c85b9f6cab1`, app tree
`3228fa2b5cae4d0db00dc7646aa6e39bb43b6b77`, CI `35914643847` passed.
Backup `ae7a3fba` contains alpha.18 and is not a fresh pre-candidate alpha.21 backup.

Before merge/publication, complete fresh live/source checks and PilotSuite-only
backup verification, assign a new unused release version, update all version
markers/changelogs, release preflight and exact candidate CI. Then exact main CI,
one normal update and runtime verification. No auto-merge while those gates remain.
See RELEASE_RUNBOOK.md; lack of the HA tool does not invalidate its working routine.

Still separate: authenticated assets/API/temporal/draft/inspection/note UI, existing
app configuration-read rights, real Golden Zone mappings/Recorder coverage,
reconnect soak, traceable real habit and second unlike zone. No learning/actuation
consent added by testing. Relative humidity alone never authorizes ventilation.

Contracts: REVIEW_NOTES.md, ROUTINE_DRAFTS.md, AUTOMATION_INSPECTION.md,
AUTOMATION_REVIEW.md, PATTERN_WORKBENCH.md, HISTORY_AND_TRENDS.md,
OBSERVATION_LEARNING.md, SENSOR_REFERENCES.md and HABITUS_ZONES.md.
Complete prior ledger: IMPLEMENTATION_HISTORY_2026-09-23.md (unchanged original
blob c7324a3d73365cc144caedf43fa3d2a6b9682287). Prior compact ledger remains at the
baseline commit. Historical installed versions are not current live measurements.
