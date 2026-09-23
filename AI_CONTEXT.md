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

## Current candidate — Store preparation on 2026-09-24

Resume **PR #50**, branch `feat/revision-bound-review-notes`, now versioned as
**0.1.0-alpha.22** across all release markers and both changelogs. This is a
versioned development candidate, **not published, merged or installed**.
Do not implement the notes again or reuse alpha.21 for their changed application tree.
The user requests the normal Store update, not a custom deployment path.

ADR-030 / docs/REVIEW_NOTES.md define the implemented PlanStore notes, schema 8,
revision/reference/config-fingerprint binding and conservative stale views.
Explicit save reinspects the selected automation, then atomically checks revisions
and bounded age. GET/restart never certifies current HA config. The editor preserves
text on conflicts. Shared workspace notes are not verified individual identities.
Notes, evidence, preference, risk and execution authorization remain separate.
Apply stays denied. No additional feature behavior was changed for versioning.

Prior feature HEAD `47ae62ead032c48ecc8c2c56cb2eae124f0a0a54` passed CI
`35923067713` (215 Python, 16 JavaScript, both browser flows, amd64).
The exact new candidate CI is recorded in PR #50. CI also invokes the existing
read-only source preflight when the candidate version differs from the last
published version in RELEASE_STATE.json; this cannot authorize deployment.
All fixtures are synthetic; no household configuration was requested.

## Delivery boundary and last actual deployment

On this turn tool discovery provided no HA-MCP namespace/native Store action and
plugin search found no matching usable connector. No fresh live HA state, backup,
Store refresh or installation was performed. Do not turn this into a fabricated
HA authentication rejection, retry the old denied custom bridge or change rights.

Last verified deployment is alpha.21 on 2026-09-23, release
`1223f96f45053f7bf3d509bd7ad72c85b9f6cab1`, app tree
`3228fa2b5cae4d0db00dc7646aa6e39bb43b6b77`, CI `35914643847` passed.
PR #49's handoff/main is `c3e87fb81a24267b8584f2d68df25bd8f9539aba`.
Backup `ae7a3fba` predates that update and contains alpha.18; it is not the required
fresh backup of the current installation for alpha.22. RELEASE_STATE.json remains
the last deployment receipt, never a candidate or unverified current-state claim.

The previously observed auto_update setting is true. Before publishing on main,
obtain and verify fresh PilotSuite-only app/data/options backup evidence and live
version information; do not waive this gate or change auto_update. Candidate
versioning is completed, source/CI must be rechecked on its exact SHA before merge.
Publication, Store offering, installation and authenticated UI acceptance are four
different steps. A GitHub change alone is not proof of a Store offer or installation.

## Resume workflow

Read CURRENT_STATE.md, docs/IMPLEMENTATION_STATUS.md, DECISIONS.md and docs/VISION.md.
For delivery also read docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md (ADR-026).
First inspect PR #50/CI and main; preserve work rather than duplicating the project.
With verified fresh backup/current source, merge without force, verify exact main CI,
then the native `ha_manage_app(action="check_updates")` without slug/repository only
if the target is not offered. Reread metadata, update the matching PilotSuite app
once unless already installed, and verify runtime. No speculative restart, new
credential or access bypass. Already granted update/backup scope need not be asked
again. Do not automatically re-enable a paused recurring development task.

The September 2026 vision is a target, not a claim of implemented capability.
Old repositories are pinned reference sources only. No second learning engine or
zone store. Climate rules remain heuristics. Counts, unknown confidence and
preference are distinct; correlation is not causality. Raw history stays transient
unless explicit scoped import uses the existing evidence owner. Missing history is
not absent behavior. Read-only PilotSuite emits no own-action evidence.

## Conceptual chain and acceptance

`world/sensors -> neurons -> moods -> synapses -> suggestions -> dialogue/approval -> policy -> transaction -> Home Assistant`

Neurons normalize relevant observations; moods are explainable deterministic scores.
Synapses link context to suggestions. Policies and transactions own action gates;
briefs, notes and graphs do not become execution plans or a second truth store.

Historical alpha.16 user UI acceptance and diagram rendering remain separate from
alpha.21/alpha.22 live acceptance. Actual authenticated UI, existing automation/config
read capability, Recorder coverage, reconnect soak and real multi-day habit evidence
remain separate tasks. No consent or household scan added by testing.
After note acceptance, the next slice is a compact derived review summary with
explicit missing requirements, never action permission.

## Deferred and retained history

No unrestricted services, direct HA .storage edits, automatic automation creation,
full Recorder mirror, mandatory LLM stack or broad unconsented learning. Discover
entity IDs from HA and preserve existing configurations. Old full ledgers stay in
CURRENT_STATE_HISTORY_2026-09-23.md and docs/IMPLEMENTATION_HISTORY_2026-09-23.md.
The previous candidate handoff is preserved at `47ae62e`; old unversioned wording
is superseded by alpha.22 preparation, not by a claimed installation.
