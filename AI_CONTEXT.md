# PilotSuite AI Context

Canonical long-term context for humans and AI contributors. Current repository
receipts plus newer explicit user decisions take precedence over older chat/status
prose. Read CURRENT_STATE.md and docs/RELEASE_STATE.json before acting.

## Resume point — 2026-09-25

Alpha.23 is already installed and started. Fresh native app metadata and readiness
logs confirm ready/connected/fresh/zone-resolved; presence and light remain partial.
Do not repeat its backup, Store refresh, update or restart. GitHub and HA-MCP reads
work together again; native GitHub writes also work. Do not recreate access setup.

Continue **PR #54 / feat/zone-daily-brief**, originally at
`6b1e9cbb4b02c4da86ae751e9772b95b07c1b9bd`. Cumulative R2 hardening is integrated in
the complete SHA256-verified CI source checkout, not another engine or local-only
mock. Alpha.24 markers are prepared, not published or installed. Real-store API
checks complement 41 projector tests; the former five free test functions were
not collected by unittest. The old PR CI failed, and its fixture defect is fixed.

See docs/DAILY_BRIEF_HARDENING.md for exact scope and test limitations. Local full-app
browser navigation was administrator-blocked; that route was not bypassed. The
regular CI now includes the full actual-app daily-brief flow. Local component
browser checks do not substitute for that CI or authenticated household acceptance.

Next: complete exact PR CI, then follow the existing RELEASE_RUNBOOK.md. With
Auto-Update enabled, a fresh completed PilotSuite-only backup is required BEFORE
publishing Alpha.24. Never use an old Alpha.22 archive as that recovery point.
RELEASE_STATE.json separates published_source, current_observation and development
from historical receipts. No new scheduler, consent, rights or actuation changes.

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
and older commits. The current change continues the existing daily-brief package and prepares Alpha.24.
