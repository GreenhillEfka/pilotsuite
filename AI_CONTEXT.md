# PilotSuite AI Context

Canonical long-term context for humans and AI contributors. The repository is
authoritative over chat history until an explicit architecture decision changes it.

## Identity and invariants

- Canonical repository: `GreenhillEfka/pilotsuite`; product PilotSuite, architecture v21.
- Primary platform: Home Assistant OS / Supervisor App `0d79c5e8_pilotsuite`.
- Semantic versioning from `0.1.0-alpha.1`; English code, German user-facing UI.
- HA owns devices, entities, areas, labels, live states and execution. No full shadow database.
- PilotSuite has one semantic/zone/evidence owner; LLM is optional and outside control.
- Deterministic policy and explicit bounded approval govern future execution.
- One mutation path: plan, backup, apply, verify, action-specific recovery.
- Read-only is the default; autonomy would require visible scope, expiry, revocation and audit.
- Never overwrite HA configuration; changes must be additive, backed up, validated and reversible.
- Never persist/log secrets or Supervisor tokens; no central cleartext secret file.
- Record material decisions in DECISIONS.md and implementation in CURRENT_STATE.md.
- Erdkeller is the first Golden Zone; validate a second unlike read-only zone before 1.0.

## Current verified delivery — 2026-09-24

**0.1.0-alpha.22 is published, offered by the normal Home Assistant Store,
installed and started. Runtime acceptance passed; authenticated live UI acceptance
remains pending. Do not implement, version or install this package again.**

PR #50 was merged without force at `7990f5a3225aec53548dd8cb5bc79e74707b9fd9`.
Its exact candidate was `ca6ba76f90c706cd3f7158aa07eec1605c81089a`.
The candidate, tested PR merge and published release have the same repository tree
`a73c3ada0695becd5823d1e0c386a06151cd5279` and application tree
`0d427053cdf246e63e044a11c15494f18dbeab08`.
Candidate CI `35928225010` and exact main CI `35929637405` passed all three jobs:
Python/JavaScript and repository/source contracts, both browser flows, amd64 build.
The candidate test log confirms 215 Python and 28 JavaScript tests. These browser
fixtures are synthetic, not a household UI acceptance receipt.

The first live call read the installed alpha.21 app. Before publication, fresh
PilotSuite-only backup `33908293` completed and native `backup/details` verified
alpha.21, 54005760 bytes, no HA configuration/database/folders, no failed components
and no encryption-key requirement. Health was verified after the backup.
After exact main CI, the native `ha_manage_app(action="check_updates")` without
slug/repository offered alpha.22. Metadata was reread, then exactly one matching
PilotSuite update completed. Installed/offered alpha.22, started, no update pending,
startup version, hard_read_only, readiness, connected stream, fresh snapshot and
resolved zone were verified. Options and auto_update=true remained unchanged.
No other app, HA configuration, actor, learning consent or permission was changed.
No separate restart, rebuild, custom bridge or restore drill was performed.

RELEASE_STATE.json is the actual deployment receipt. Source association is the
canonical repository, offered version and unchanged tested application tree; it is
not an independent installed-image or Supervisor-checkout attestation.
The older `ae7a3fba` backup contains alpha.18; `33908293` is the verified pre-alpha.22
alpha.21 recovery point. Older access blockers are historical, not current failures.

## Delivered review-note package

ADR-030 / docs/REVIEW_NOTES.md define the implemented PlanStore notes, schema 8,
revision/reference/config-fingerprint binding and conservative stale views.
Explicit save reinspects the selected automation, then atomically checks revisions
and bounded age. GET/restart never certifies current HA config. The editor preserves
text on conflicts, resets selection after a changed inspection basis and displays
saved text for comparison. Overview counts separate assessment from freshness;
selected recheck is explicit. See docs/REVIEW_NOTES_USABILITY.md.
Shared workspace notes are not verified individual identities. Notes, evidence,
preference, risk and execution authorization remain separate. Apply stays denied.
No implementation or release-number change was made during this delivery.

## Resume workflow and remaining acceptance

Read CURRENT_STATE.md, docs/IMPLEMENTATION_STATUS.md, DECISIONS.md and docs/VISION.md.
For delivery also read docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md (ADR-026).
First read current app metadata, main/open work and exact CI. If alpha.22 is still
installed, do not update, rebuild, restart or create another pre-update backup.
Proceed only with an explicitly authorized next slice or pending acceptance.
For a future release, retain the same backup-before-publication and native Store
routine; existing backup/update authorization need not be asked again.
Do not automatically re-enable a paused recurring development task.

Actual authenticated assets/API/temporal/draft/inspection/note UI, the app's existing
automation/config-read capability, independent live migration/data-preservation
inspection, Recorder coverage, reconnect soak, real multi-day habit evidence and a
second unlike read-only zone remain separate tasks. No rights escalation, additional
consent or household scan is implied by deployment. Historical alpha.16 user UI
acceptance does not certify alpha.22. After note acceptance, a compact derived
review-requirements summary may be a next development slice, never action permission;
it was not implemented in this delivery.

## Conceptual chain and retained boundaries

`world/sensors -> neurons -> moods -> synapses -> suggestions -> dialogue/approval -> policy -> transaction -> Home Assistant`

Neurons normalize relevant observations; moods are explainable deterministic scores.
Synapses link context to suggestions. Policies and transactions own action gates;
briefs, notes and graphs do not become execution plans or a second truth store.
The September 2026 vision is a target, not a claim of implemented capability.
Old repositories are pinned reference sources only. No second learning engine or
zone store. Climate rules remain heuristics. Counts, unknown confidence and
preference are distinct; correlation is not causality. Raw history stays transient
unless explicit scoped import uses the existing evidence owner. Missing history is
not absent behavior. Read-only PilotSuite emits no own-action evidence.
No unrestricted services, direct HA .storage edits, automatic automation creation,
full Recorder mirror, mandatory LLM stack or broad unconsented learning.

Prior candidate handoff is preserved at `ca6ba76`; older full ledgers remain in
CURRENT_STATE_HISTORY_2026-09-23.md and docs/IMPLEMENTATION_HISTORY_2026-09-23.md.
This documentation-only handoff does not change the deployed application tree.
