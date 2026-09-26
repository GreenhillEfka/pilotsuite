# PilotSuite AI context

Canonical GreenhillEfka/pilotsuite / app 0d79c5e8_pilotsuite. Read CURRENT_STATE,
docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first. Do not start a new repo.

## Alpha.32 candidate — 2026-09-26

User asked to finish inventory recognition, manual semantic assignment, cleanup and
controlled migration after the interrupted prior turn. Live Alpha31 and main
75c101b22da5e31ee12a1c7d211bfb09d1583825 were verified; no open PR or unfinished
remote implementation existed. Full source bundle artifact10892532197 was checksum-
verified and cloned, with a local before-archive. No household mutation was performed.

The candidate is a complete configuration-workspace path: global helper/catalog choice,
automation-first bounded references/repair suggestions, persistent manual bindings,
existing for/timer planning, and confirmed helper display-name cleanup with readback,
durable status and guarded undo. Existing ContextStore and PlanStore remain canonical;
no second learner/database or schema migration. Role/evidence/consent data survive.
Bindings are semantic organization, not new learning or control grants.

Repair plans are stored but cannot execute automation writes. Technical-ID migration
shows proposals/collisions and stays blocked because selected automation review cannot
prove complete consumer coverage. Do not claim all migration/repair execution is done.
Older presence activation is now fail-closed pending separate timer/authority acceptance;
this package must not be described as a tested replacement presence controller.

Implementation, UX, safety boundaries and follow-up: docs/ORGANIZATION_AND_MIGRATION.md.
Use native HA APIs only, no .storage edits or Ingress bypass. Registry name updates are
not HA/SQLite atomic and not a native compare-and-swap; never blindly replay unknown
outcomes or claim an unknown-response result authorizes rollback. Shared bindings and
identity/name changes block unilateral cleanup.

Before delivery: full local Python/JS/compile and exact remote CI incl new actual-app
browser flow; then fresh completed PilotSuite-only native backup BEFORE publication
(auto_update=true). One normal Store update; source/main CI and runtime rechecked.
Household names, automations, sources and learning grants remain unchanged by release.
Record final delivery separately; do not repeatedly redeploy to write documentation.
