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

## Current development versus deployed release

Resume **draft PR #50**, branch `feat/revision-bound-review-notes`.
The review-note increment (ADR-030, docs/REVIEW_NOTES.md) is implemented on this
**unversioned development branch, not merged/published/installed**. It extends the
canonical PlanStore with bounded user-authored assessments and schema 8. Notes bind
to draft revision, zone/reference basis and a freshly read selected automation
fingerprint. Edits/reset/expiry make the basis stale; GET/restart never certifies
current HA configuration. Explicit save reinspects via the existing HA client and
atomically checks revisions and bounded age before writing. Notes, evidence,
preference, risk and execution authorization remain separate. Apply stays denied.
The editor preserves text on conflicts; draft deletion guards the notes revision.
Shared workspace notes are not verified personal identities.

Local focused tests and syntax/compile checks pass. Full backend/browser/container
CI must be read on the exact PR head; the final receipt belongs in PR #50.
The local synthetic browser navigation was environment-blocked, not a test pass.
All new fixtures are synthetic; no household configuration/evidence was requested.

Last verified deployment remains alpha.21 from the previous continuation, release
`1223f96f45053f7bf3d509bd7ad72c85b9f6cab1`, app tree
`3228fa2b5cae4d0db00dc7646aa6e39bb43b6b77`, release CI `35914643847` passed.
The installation handoff was merged in PR #49 at
`c3e87fb81a24267b8584f2d68df25bd8f9539aba`, this increment's baseline.
The native `ha_manage_app(action="check_updates")` works without slug/repository;
never retry the previously denied custom /store/reload bridge. Backup `ae7a3fba`
preceded the alpha.18-to-alpha.21 update. It is **not** a fresh alpha.21 backup.

HA-MCP was unavailable in tool discovery during review-note development. No fresh
live state or HA change is claimed. Do not interpret this as a general permissions
failure or ask for already granted update/backup authority. Because the last
verified app setting has auto_update enabled, do not merge/release this candidate
before fresh scoped backup verification. Version markers intentionally remain at
the published baseline on this unmerged branch; a new unused version is required
before delivery. Do not install changed behavior as alpha.21.

## Resume workflow

Read CURRENT_STATE.md, docs/IMPLEMENTATION_STATUS.md, DECISIONS.md and docs/VISION.md.
For delivery also read docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md (ADR-026).
First inspect PR #50/CI and current main; preserve work rather than starting another
repository, another PR for the same increment or duplicating this implementation.
Recheck live state when the native HA tools are available, complete scoped backup,
version/validate, exact PR CI, merge without force, exact main CI, one Store update
and runtime checks. Authenticated UI/config-read acceptance is a separate gate;
never spoof Ingress or escalate privileges. No automatic re-enabling of a paused
recurring development task.

The September 2026 vision is a target, not a claim of implemented capability.
Older repositories are pinned reference sources only. Do not reintroduce two learning
engines or independently owned zones. Climate rules remain heuristics. Activity
patterns, counts, unknown confidence and preference are distinct; correlation is
not causality. Raw history stays transient unless an explicit scoped historical
import uses the existing evidence owner. Missing history is not absent behavior.
Read-only PilotSuite emits no own-action evidence.

## Conceptual chain

`world/sensors -> neurons -> moods -> synapses -> suggestions -> dialogue/approval -> policy -> transaction -> Home Assistant`

Neurons normalize relevant observations; moods are explainable deterministic
context scores, not anthropomorphic truth. Synapses connect context to suggestions.
A suggestion needs evidence, scope and independently stated confidence/risk.
Policies remain final gates, transactions the only mutation owner. Derived briefs,
review notes and graphs are neither execution plans nor a second truth store.

## Acceptance still pending

Keep historical alpha.16 user guide/navigation/workbench acceptance and reported
history diagram rendering separate from alpha.21/new-candidate acceptance.
Actual authenticated temporal/draft/inspection/note UI and the app's existing
`automation/config` capability remain unverified here. Recorder coverage,
reconnect soak and multi-day real learning remain separate; no extra consent by
acceptance testing. After note delivery, the next conceptual slice is a compact
derived review summary with explicit missing requirements, never an action gate.

## Deferred and history

No unrestricted services, direct HA `.storage` edits, automatic automation creation,
full Recorder mirror, mandatory Ollama/Open WebUI/LLM or broad unconsented learning.
Entity IDs are discovered from HA, not invented. Preserve existing configurations.
Full former receipts remain unchanged in CURRENT_STATE_HISTORY_2026-09-23.md and
docs/IMPLEMENTATION_HISTORY_2026-09-23.md. Old blockers there are not present state.
