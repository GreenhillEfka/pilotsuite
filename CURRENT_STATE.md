# PilotSuite current state

## 2026-09-25 — Alpha.26 release closure, Alpha.25 still installed

Canonical repository GreenhillEfka/pilotsuite; app 0d79c5e8_pilotsuite.
Active PR #59, feat/zone-foundation-provisioning. No new repository or setup loop.
Alpha.25 metadata was freshly confirmed installed/offered/started with original
options and auto_update=true. Alpha.26 is not published by this development commit.

The complete PR source was obtained from CI run 36138938438 artifact 10866005818;
ZIP SHA256 3876c9496da70751f1fb8cdc9cdca9bb3f49c81520dc2d75e43a83a75b7704d0
and the bundle checksum verified. Exact candidate c363220137260f6fc03d51cc783183348d1607f6
was checked out. The full native test-job log identified the still-broken literal
newline in test_automation_import.py. A local full-suite run after that syntax fix
identified the separate diff bug: alias was mislabeled as an unknown field.
The previous timer-namespace/zone-fixture diagnoses were not proof of these failures.

Release closure fixes those errors plus stale/false setup readiness, registry-only
helper assumptions, detached and bounded imports, numeric guards and missing
identity verification. No new executor, state store or learning consent was added.

## Delivered vs prepared

Alpha.25: roles and initial foundation projection; runtime read-only observation.
Alpha.26 candidate: German visual planning surface, guarded explicit transient
existing-automation API read, helper inventory hints and isolated policy/diff/model
primitives. A list of presence states is NOT an operating presence state machine;
module overlap is NOT proven execution ownership; a transition record is NOT a
persisted migration journal. The broad takeover/comfort vision remains incomplete.
See docs/ALPHA26_RELEASE_REVIEW.md and IMPLEMENTATION_STATUS.md for exact boundaries.

## Next action

Freeze PR59; finish exact remote tests and release using RELEASE_RUNBOOK.md.
A fresh app-only backup must complete before publication because auto_update is on.
Do not change other apps, house configuration, role assignments or learning consent.
After delivery, implement and fault-test one bounded helper executor in the existing
PlanStore path. Do not add another contract-only module or claim HA/SQLite atomicity.
