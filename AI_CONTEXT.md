# PilotSuite AI Context

Canonical repository receipts plus newer explicit user decisions take precedence
over older chat/status prose. Read CURRENT_STATE.md and docs/RELEASE_STATE.json first.

## Resume point — 2026-09-25: Alpha.24 delivered

PR #54 is merged. Alpha.24 is installed through the normal Home Assistant Store,
started and runtime-verified: hard_read_only, ready, connected, fresh, zone-resolved.
Presence/light remain partial, distinct from transport readiness. Do not repeat
backup/Store/update/rebuild/restart just to resume. GitHub reads AND writes and native
HA-MCP operations worked in the same conversation; no access reconfiguration needed.

Release 6f22100dcfbee87bdedc8288b1821971bad17d53; app tree
528396dc07e35b2df1e349322f6c0b49e9dee6cb. Exact candidate CI 36117146697 and main CI
36117395171 passed: 308 Python, 48 JavaScript, five browser steps and amd64 build.
Fresh PilotSuite-only Alpha.23 backup ad3c24bb was completed and natively verified
before publication. One native Store refresh, one PilotSuite update, unchanged
options/auto_update, no other app or household/consent/permission/scheduler changes.
Details and separate acceptance boundaries: RELEASE_STATE.json / PR #54.

R2 and the missing saved-candidate changes were reconciled, not reimplemented.
Bounded daily brief, consistent sources/evidence/preferences, stale-read prevention,
focus/unsaved-input preservation and unittest-discovery checks are delivered.
The stronger published_source / same-version app-tree release gate remains intact.
Local component evidence and synthetic full-app CI are not authenticated household
acceptance. No production proxy, peer, port or authentication workaround occurred.

Next: authenticated real Ingress acceptance of one useful or reasonably withheld
brief in the already consented Golden Zone and navigation to its existing workbench.
No automatic automation scan, new consent or actuation to obtain that evidence.
Do not create another review engine or release merely to restate completed delivery.

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
