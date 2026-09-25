# PilotSuite AI Context

Canonical repository receipts plus newer explicit user decisions take precedence
over older chat/status prose. Read CURRENT_STATE.md and docs/RELEASE_STATE.json first.

## Resume point — 2026-09-25: Alpha.25 delivered

Alpha.25 is installed through the normal Home Assistant Store and started. Release
commit `a6d6e329eee15ee97c5e732dd963ca8a531444e3`; PR #57 candidate CI and main CI
#36128782821 passed all jobs including Python/JS, browser, source and amd64 build.
Fresh pre-publication PilotSuite-only backup `70e14c12` contains only Alpha.24,
54,179,840 bytes, no HA/database/folders/failures. One Store refresh and one
PilotSuite update installed Alpha.25; options and auto_update remained unchanged.
Runtime logs confirm hard_read_only, ready, connected stream, fresh snapshot and
resolved Golden Zone. Humidity/motion/presence/light remain partial capabilities.

Alpha.25 starts Issue #56 structurally: explicit logical input_boolean presence
helpers are valid only after role assignment; multi-source selection is explicit;
binary ambient-light indicators are separated from controllable light state; climate,
media and explicit atmosphere roles are available; a deterministic read-only
zone-foundation projection reports presence/light/media/climate readiness, bounded
cross-context correlations and stable helper recommendations. It does not create HA
helpers or actuate devices; execution remains denied.

During household hardening, four exactly identified stale
`binary_sensor.*_sound_syncronisation` references in existing music automations were
backed up and migrated to the already-existing corresponding
`input_boolean.*_sound_synchronisation` helpers. Post-search found zero old
references; automation enabled states were preserved. Do not guess replacements for
the still-stale Shutdown Wohnbereich scene: several missing targets lack a proven
one-to-one successor.

Next development continues Issue #56: governed helper provisioning/ownership,
presence timer foundation, systematic reuse/repair plan for existing HA logic,
daylight-relative lighting, then media/climate policies. Existing HA logic remains
owner until a revision-bound takeover is explicitly verified.

## Identity and invariants

- Canonical repository GreenhillEfka/pilotsuite; architecture v21; app 0d79c5e8_pilotsuite.
- Home Assistant OS / Supervisor; semantic versions; English code, German user UI.
- HA owns devices, entities, areas, labels, states and execution; no shadow database.
- One semantic/zone/evidence owner; optional LLM outside the critical control path.
- Future actions require deterministic policy and explicit bounded approval.
- One mutation path: plan, backup, apply, verify, action-specific recovery.
- Read-only is default; autonomy needs scope, expiry, revocation and audit.
- Never overwrite HA configuration; additive, backed-up, validated changes only.
- Never persist/log credentials or Supervisor tokens; no cleartext secrets file.
- Record material decisions in DECISIONS.md, implementation in CURRENT_STATE.md.
- Erdkeller is first Golden Zone; second unlike consented zone before broader action.

## Shared workflow and distinct acceptance

ADR-027–031 and ROUTINE_DRAFTS, REVIEW_NOTES, REVIEW_COMPASS and DAILY_BRIEF_HARDENING
retain the shared PlanStore/ContextStore ownership. Notes, briefs and graphs cannot
grant execution. Revision-bound authored assessments are independent of evidence,
preference, confidence and risk. GET cannot certify current HA automation config.
No new schema in Alpha.24; Apply remains denied.

Before code changes read DECISIONS.md, docs/VISION.md, docs/ROADMAP.md and
IMPLEMENTATION_STATUS.md. Deployment uses RELEASE_RUNBOOK.md, not a new routine.
Do not reask the already granted PilotSuite-only backup/update scope. Source CI,
installation/runtime, authenticated Ingress, app config-read capability, independent
data/image attestation and real comfort benefit remain distinct checks.

## Conceptual chain and boundaries

world/sensors -> neurons -> moods -> synapses -> suggestions -> dialogue/approval
-> policy -> transaction -> Home Assistant.

No second learner or zone store. Climate rules remain heuristics, missing data stays
unknown, and correlation is not causality. Raw history is transient except explicit
scoped imports. No Recorder mirror, unrestricted services, direct HA .storage edits,
automatic automation creation, mandatory LLM or unconsented learning. Read-only
PilotSuite cannot generate own-action learning evidence. The vision is a target,
not a claim of completed capability. Earlier handoffs remain in Git and the linked
release-history receipt. This delivery handoff changes documentation only.
