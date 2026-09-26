# PilotSuite current state

## 2026-09-26 — Alpha.32 candidate: Bestand & Ordnung

Baseline installed/offered Alpha31; canonical main
75c101b22da5e31ee12a1c7d211bfb09d1583825, no open PR. Candidate is not yet claimed
installed here. This is the requested inventory/order package, not another UX-only shell.

Implemented: automation-first reference inspection including template literals and timer
events; manual global function bindings by stable identity; alternative for/timer/external
mechanisms; retained bindings over renames and identity conflicts; source/status/parameter/
override/blocker distinctions. Existing for logic need not create a new PilotSuite timer.

The configuration workspace includes scoped analysis, candidate replacements, persisted
repair previews, current bindings, standard naming proposals, confirmed name application,
status history and separately confirmed undo. PlanStore persists before-images and
per-operation progress; restart/lost responses never blindly replay. Name cleanup uses
only native registry `name`, not entity IDs, labels, areas, values or generic actions.
ContextStore shares the zone revision and preserves existing roles/evidence/consent.
Savepoints include optional bindings; schema stays 8.

Not implemented: automation-repair execution, complete cross-component ID migration,
active presence takeover or adaptive comfort control. Older activation is fail-closed
until proper timer-event/ownership tests. Display names can affect name-based templates
and voice assistants; HA offers no conditional atomic registry update. Limits are explicit
in the UI and docs/ORGANIZATION_AND_MIGRATION.md.

Local compile, repository validation, 452 Python tests and 53 JavaScript tests passed.
Exact candidate/main CI, fresh app-only backup and installation receipt follow the
existing release runbook. No household
helper, automation, role, learning permission or actuator has been changed in this work.
