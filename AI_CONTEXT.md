# PilotSuite AI Context

Canonical long-term context for humans and AI contributors. Current repository
receipts plus newer explicit user decisions take precedence over older chat/status
prose. Read CURRENT_STATE.md and docs/RELEASE_STATE.json before acting.

## Resume point — 2026-09-24

**Alpha.23 Prüfkompass is implemented, merged through PR #52 and published.**
Release `dfecb464f9f67eb1dd3e393b8ecc99e9ca208814` passed exact main CI 35991187908;
candidate `cf445355868cbe1448f402be19207f66beae5898` passed CI 35990039222.
247 Python tests, 48 JavaScript tests, three synthetic browser flows and amd64 build
passed. Actual app tree: `38ef81068ff75f135bce6734a43e2caca3c09b8c`. The tree was checked
against Git and the source-only CI bundle; the different hash in the merge message
is a transcription error, not a second release. No image attestation is implied.

**Installation is unverified.** This continuation exposes GitHub but no HA-MCP.
No live HA check or update occurred here. Prior reads observed Alpha.22/started;
auto_update was true, so do not assume it is still Alpha.22. Prior Store readings
were inconsistent after a successful Alpha.23 offer. Native backup 5c40193c covered
Alpha.22 before publication: 54,118,400 bytes, 2026-09-24T11:02:07.031215+00:00,
PilotSuite only, no HA/database/folders/errors/key requirement. Recheck availability
and freshness; do not silently reuse an older Alpha.21 recovery point.

One next task: resume the existing native release routine with a fresh app read.
Installed Alpha.23 means skip backup/update/rebuild/restart; otherwise follow exact
source/CI/backup/offer gates for one matching update, then runtime verification.
Do not recreate the feature or release it under another version to finish delivery.
`docs/RELEASE_STATE.json` retains the completed Alpha.22 receipt; `pending_release`
records Alpha.23 publication/preparation only, not installation. No permission
weakening, new tokens, alternate bridge or unconsented household scan.

The user resumed hourly package development on 2026-09-24; see
[DEVELOPMENT_MANDATE.md](docs/DEVELOPMENT_MANDATE.md). This supersedes old paused-task
instructions, not household consent boundaries. No scheduler change was made in
this handoff. First finish delivery; then demonstrate real usefulness in the
already consented Golden Zone. No additional review administration for its own sake.

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

## Published review workflow and independent acceptance

ADR-027–031 and docs/ROUTINE_DRAFTS.md, REVIEW_NOTES.md,
REVIEW_NOTES_USABILITY.md and REVIEW_COMPASS.md describe the shared PlanStore path.
Five derived compass sections do not create another evidence owner or permission
gate. Note save reinspects and checks revisions/age atomically; GET cannot certify
current HA configuration. Authored text, preference, evidence, confidence, risk and
execution permission remain independent. No new schema in Alpha.23; Apply denied.

Read DECISIONS.md, docs/VISION.md, docs/ROADMAP.md and
 docs/IMPLEMENTATION_STATUS.md before the next code change. For deployment follow
 docs/RELEASE_RUNBOOK.md; never repeatedly ask for the already granted app-only scope.
Source CI, native installation/runtime, authenticated Ingress acceptance, app's
config-read capability, independent data preservation and installed-image checks
are separate. Missing tool access is not missing user authorization.

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

Earlier handoffs and their measurements remain in Git at `dfecb464f9f67eb1dd3e393b8ecc99e9ca208814`
and older commits. This handoff changes documentation only; no app or version change.
