# PilotSuite implementation status

## Current release and evidence — 2026-09-23

**0.1.0-alpha.21 is installed and started in Home Assistant.**
Release commit: `1223f96f45053f7bf3d509bd7ad72c85b9f6cab1`.
App tree: `3228fa2b5cae4d0db00dc7646aa6e39bb43b6b77`.
Release CI `35914643847` and pre-deployment current-main CI `35915002481` passed
test, Chromium browser and amd64 container jobs. The release receipt records 192
Python and nine JavaScript tests; this continuation checked those existing CI runs,
not a new local execution of the suite.

Native Store refresh now works with `ha_manage_app(action="check_updates")`.
Fresh scoped backup `ae7a3fba` was completed and verified before one normal update.
Runtime confirms alpha.21, hard read-only, connected stream, fresh snapshot,
resolved Golden Zone and readiness. No new role, learning consent or actuation.
See [RELEASE_STATE.json](RELEASE_STATE.json), [RELEASE_RUNBOOK.md](RELEASE_RUNBOOK.md)
and [../CURRENT_STATE.md](../CURRENT_STATE.md) for operational detail.

## Capability ledger

| Capability | Implemented boundary | Acceptance / remaining work |
|---|---|---|
| App packaging and updates | Canonical Supervisor app; exact release/version/tree association and scoped operational backup routine | alpha.21 installed; independently attested Store checkout/image and recovery drill not claimed |
| Ingress and frontend | Peer-restricted app UI, navigation, zone guide and workbench | Synthetic Chromium passes; actual authenticated alpha.21 assets/API/interaction acceptance remains pending |
| HA snapshot and event stream | Read projection, reconnect/backoff, timestamp guards, bounded origin correlation | Runtime connected/fresh/ready; snapshots are not atomic transactions, no durable stream replay; soak pending |
| Readiness and quality | Stream, snapshot freshness, scope and capabilities reported separately | Does not certify physical sensor freshness; missing/conflicting data stays explicit |
| Habitus zones and entity roles | Stable logical zones, multiple areas/extras, explicit inclusion, plural role groups and main sensor selection | Real mapping review remains separate; no wholesale HA state mirror |
| Typed sensor references | Climate normalization, plural sources, spread, separate references, illuminance and unified presence-source semantics | Selection-dependent coverage; no invented sensor values |
| Suggestions and activity candidates | Deterministic climate heuristics and bounded consented activity evidence | Observation counts, confidence, risk and preference remain distinct; no causal habit or safe cellar-control claim |
| History and temporal views | Targeted transient history/statistics, graphs and explicit scoped history import through the existing evidence owner | Recorder coverage not presumed; raw history is not mirrored; new import consent was not enabled |
| Pattern workbench | Derived review briefs, evidence explanations and time-separated reobservation | Not a predictive holdout, action plan, semantic verdict or execution permission |
| Routine drafts / PlanStore | Explicit user-authored durable drafts with revision checks, declarative intent/targets, source refresh, export/delete | Schema 7; drafts survive learning reset. No raw automation config is copied into PlanStore |
| Existing automation reference review | Explicit bounded transient related-entity lookup using supported HA APIs | Entity reference is not equivalence, causality, enabled state or safety; no household-wide scan |
| Selected automation inspection | Fresh selected configuration read, whitelisted trigger/condition/action structure, open review checklist, fingerprint comparison and combined export | Config remains transient; live app automation/config capability not verified; no privilege escalation or template evaluation |
| Persisted review notes | **Next planned increment, not implemented** | User-authored notes bound to draft revision/config fingerprint; stale after change; never action authorization |
| Storage and migrations | Owned zones, roles, consent, evidence, feedback, provenance and routine drafts with migration safeguards | SQLite schema 7; audit and legacy dry-run records remain separate; not a Recorder clone |
| Action execution and runtime recovery engine | Dry-run boundary remains denied | Typed action catalog, real approval lifecycle, transactional apply/verify/rollback and fault-injection gates are future work; operational app backup is not that engine |
| Multi-user preferences | Planned | Preference/evidence separation and conflict handling required |
| Brain graph | Full interactive brain graph planned | Existing derived evidence views do not establish a second semantic owner |
| Optional native HA adapter / Assist / LLM / RAG | Planned or optional architecture | No mandatory LLM and no direct LLM action path; provider capabilities require verification |
| HomeKit, broad module/Dev/Wiki UI and presets | Deferred | Inventory-first and capability-specific review; no automatic exports or unrestricted actuation |
| Legacy cleanup | Not comprehensively verified | Removed Store repositories do not prove legacy HACS/config entries/entities were removed |

Feature contracts: [HABITUS_ZONES.md](HABITUS_ZONES.md),
[SENSOR_REFERENCES.md](SENSOR_REFERENCES.md), [OBSERVATION_LEARNING.md](OBSERVATION_LEARNING.md),
[HISTORY_AND_TRENDS.md](HISTORY_AND_TRENDS.md), [PATTERN_WORKBENCH.md](PATTERN_WORKBENCH.md),
[ROUTINE_DRAFTS.md](ROUTINE_DRAFTS.md), [AUTOMATION_REVIEW.md](AUTOMATION_REVIEW.md),
[AUTOMATION_INSPECTION.md](AUTOMATION_INSPECTION.md), and [../DECISIONS.md](../DECISIONS.md).

## Remaining acceptance gates

1. Actual authenticated alpha.21 Ingress assets, APIs, temporal/draft/review UI and
   existing app read capability. No fabricated browser pass or elevated permissions.
2. Golden Zone mappings and measured history coverage; reconnect/HA-restart soak
   without treating unavailable data as false, zero or absent behavior.
3. Already-consented real habit evidence with traceable proposal and durable
   feedback. A second unlike read-only zone before 1.0; no new consent by testing.
4. Only after separate explicit approval: one bounded reversible action with
   validated policy, backup, fault-injection, verification and recovery design.

Relative humidity alone never justifies a ventilation command. Current climate
thresholds are heuristics, not a validated cellar-control policy.

## Full historical ledger

The prior document is preserved byte-for-byte in
[IMPLEMENTATION_HISTORY_2026-09-23.md](IMPLEMENTATION_HISTORY_2026-09-23.md), original
blob `c7324a3d73365cc144caedf43fa3d2a6b9682287`. Historical installed versions and
acceptance instructions there are superseded by the current receipt above.
This consolidation changes documentation only, not application behavior.
