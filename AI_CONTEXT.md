# PilotSuite AI Context

Canonical: GreenhillEfka/pilotsuite / HA app 0d79c5e8_pilotsuite / architecture v21.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and RELEASE_RUNBOOK.md first.

## Resume — Alpha.26 delivered, 2026-09-25

PR59 merged as ede80bd4d7024aaa146c8d5bff53031905da9165. Exact candidate CI
36147092132 and main CI 36148039084 passed all jobs. Fresh PilotSuite-only backup
45805440 completed and was verified BEFORE publication. One native check_updates,
one PilotSuite update. Alpha.26 is installed/offered/started; startup and readiness
logs confirm hard_read_only, ready, connected stream, fresh snapshot, resolved zone.
Options and auto_update=true unchanged; no other app, household config or learning
permission was changed. Partial capabilities are NOT transport failure.
Do not repeat backup/update/rebuild/restart or reconfigure connectors just to resume.
All identities, scope and distinct acceptance boundaries are in RELEASE_STATE.json.

## Honest implementation boundary

Alpha.26 delivers a German planning view, current-source validation, non-authoritative
helper inventory hints and guarded explicit transient automation reads. It does NOT
run presence timers, provision helpers, control light/music/heating, persist an
adoption journal or automatically take over existing automations. Preparatory policy,
state-list, diff and mapping functions are not those complete capabilities. Issue56
remains open. See docs/ALPHA26_RELEASE_REVIEW.md and IMPLEMENTATION_STATUS.md.

## Invariants

HA owns device state/execution. PilotSuite owns zones/roles/bounded evidence and
review intent through existing ContextStore/PlanStore; no second learner/store.
No implicit learning, unscoped writes, guessed entity replacements or ownership.
Registry ID/name matches cannot establish helper configuration/ownership; registry
absence cannot prove helper-collection absence. Preserve manual overrides, unknown
original config fields, existing entity identity and the user's house logic.
No HA .storage edits, ingress/peer/header/port bypass, or credentials in code/logs.

## Active Alpha.27 maintenance slice (not installed yet)

The latest explicit request adds existing-helper inspection, last-three versions,
update/native install entry, local savepoints and rescue recovery. Implemented in
the candidate through existing PlanStore/service/UI; see
docs/MAINTENANCE_AND_RECOVERY.md. No HA helper executor or runtime actuation.
First-start Golden Zone option is relabelled, not changed in the household.
Close this scoped package through exact CI and the existing release routine.

## Following implementation, not another concept loop

Implement ONE actual bounded helper executor in the canonical PlanStore mutation
path: scoped plan/approval, backup, apply, independent read-back, action-specific
recovery. Test timeout, lost response, restart and concurrent edits in disposable HA
before real household writes. HA and SQLite are not one atomic transaction. Never
blindly replay a write with unknown outcome or delete pre-existing/foreign helpers.
Implement and test the full UI-to-application path before claiming provisioned zones.
Then presence timing, followed by controlled existing-automation adoption.
Improve mobile foundation-card word wrapping within that new version, not Alpha.26.

Use native GitHub job logs and a complete checkout for diagnosis; the earlier
newline fix was an unchanged blob. Compile application AND test sources, run full
local tests before a single pinned change set, then exact remote CI. Keep the
published-source/app-tree release gate and existing runbook. Documentation-only changes alone do not justify another release. Final docs CI receipts belong in PR comments.
