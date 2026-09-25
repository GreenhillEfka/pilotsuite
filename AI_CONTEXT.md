# PilotSuite AI Context

Canonical: GreenhillEfka/pilotsuite / HA app 0d79c5e8_pilotsuite / architecture v21.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and RELEASE_RUNBOOK.md first.

## Resume: Alpha.26 closure (PR59)

Alpha.25 is currently installed/started; Alpha.26 remains a candidate until exact
CI, fresh prepublication PilotSuite-only backup, merge/main CI and native Store
installation are verified. Existing approvals cover this scoped release; do not
ask again or repeat completed delivery. Read the current receipt, not older chat.

Use native GitHub.fetch_workflow_job_logs for actual errors. Read full source and
run tests locally before pushing a pinned change set. Do not guess failures from
job names; the previous newline repair was an unchanged blob, not a repair.
Source and test compilation, unittest discovery, full unit/browser/container tests
remain mandatory. Preserve old changelog entries and published_source identity.

## Invariants and honest scope

HA owns device state/execution; PilotSuite owns zones/roles/bounded evidence and
review intent through existing ContextStore/PlanStore. No duplicate learner/store.
Alpha.26 remains hard_read_only. Helper plans, migration/diff/model primitives and
comfort examples do not constitute an executor, persisted journal or actual timer.
No implicitly granted learning, new collection, actor control or automatic adoption.
Registry hits do not establish helper ownership; registry absence does not prove
absence in helper collections. Existing automations remain HA-owned until an
explicit, backed-up, separately verified takeover exists. Avoid duplicate controllers.

Read-only views cannot claim operation, causal learning or physical sensor freshness.
Preserve unknown config fields; reject unsupported changes. Retain original entity
identity and manual overrides. No HA .storage edits, ingress/header/port bypass or
credentials in code/logs. Existing household mappings are not guessed from names.

## Next

Complete this frozen release, then implement ONE bounded helper executor via the
canonical mutation path (plan, scoped approval, backup, apply, verify, recovery),
with restart/timeout/concurrent-edit tests in disposable HA before real household
writes. Timers must reconcile after restart; no universal rollback for physical
effects and no claim that HA and local SQLite share an atomic transaction.
