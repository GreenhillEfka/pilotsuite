# Current state — Alpha.63 installed; household acceptance pending

## Alpha.64 candidate — checkpoint contention

Branch `fix/presence-checkpoint-contention` fixes a reproduced SQLite lock error
for identical operational checkpoints. A single read joins zone/revision/value;
changed writes still recheck transactionally. Eight added tests and the full
625 Python / 75 JS suites pass; three local synthetic browser suites pass.
The extended existing benchmark preserves all four decision-trace hashes: suspended
repeats use 0 instead of 60 write reservations per 60 cycles; actual writes stay 0.
Occupied/vacant/unknown retain 60 writes/reservations and add 60 SELECTs. No overall
speed gain, timestamp removal or scheduler change. Exact CI/delivery pending;
installed Alpha.63 remains the separate receipt below.

## Verified delivery

PR #136 merged as `3779b630985bdedeb0402343dd153acda77974b0`.
Exact candidate CI `36433388018` and release-main CI `36433797302` passed
all five jobs: tests, 11 browser suites, amd64 container, reproducible checkout
and disposable Home Assistant protocol. App tree:
`ae8f1051f41ea7e4d7d11d76494fd25b9f055c45`; local and connector trees matched.

Fresh PilotSuite-only backup `7e502760` completed at 14:02:19 UTC before publication:
exactly Alpha.62 app/data/options, 54,466,560 bytes, no HA/database/folders/failures,
local and unprotected. Native list and backup/details verified metadata; no archive
extraction or restore drill. One native Store refresh and one targeted update
installed Alpha.63; no extra restart, rebuild or other-app update.

HA-MCP confirms installed/offered/started and all four options unchanged. Startup
remains `presence_adoption_review`, ready, connected, snapshot-fresh and zone-resolved.
Raw log timestamps are copied without independent clock attestation.
Full evidence: [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).

## What Alpha.63 changes

Identical presence-configuration saves preserve the session, revision and durable
grace deadline. They no longer write the configuration, run an extra all-zone
evaluation or unnecessarily invalidate owned outputs. Dated publication evidence
keeps its original time and still becomes unavailable on stale/disconnected inputs.
Revision/source/relevance/feedback checks precede the no-op. Actual timing, mode or
source changes and explicit recovery from suspension retain the full save path.

No new store, scheduler, schema migration, HA authority or broad speed-gain claim.
No household binding, helper, metadata, automation, output activation or consent
was changed. AGENTS.md remains unchanged and untracked; Ingress/authentication intact.

## Test evidence

617 Python tests, 75 JS tests, 62 API contracts, discovery, syntax and compilation pass.
Repeat audit on exact release-main source: 617 tests, zero ResourceWarnings.
Two original red regressions reproduced a lost deadline and one extra mocked output
call. Five added Python methods cover repeated saves, restart/deadline expiry,
publisher proof, stale/disconnected evidence, real changes/recovery and validation.

Local zone, workspace and Organization Chromium suites pass. Expanded compare/publish
form tests retain the grace deadline, revision and proof date without extra HA writes;
four synthetic zones, roles/consents and organization bindings remain unchanged.
Desktop/mobile screenshots inspected; all 11 browser suites passed exact candidate
and main CI. Synthetic tests are not household acceptance.

## Next task and remaining boundaries

With an authorized authenticated household Ingress session, first read all four
saved zones, Erdkellerbereich and one unlike zone without changing anything.
Then explicitly choose intended existing Boolean/timer/public sensor bindings and
observe actual comparisons without test switching. No mappings were guessed/applied.

Alpha.61's existing-control path remains: **Vorhandenen Bestand verbinden** reuses the
canonical Organization editor. Existing HA automations remain controllers of their
Boolean/timer/public sensor; PilotSuite only reads and compares. Unknown never means
vacant. No public sensor was automatically generated for that existing chain.
Periodic checkpoint/scheduler consolidation requires separate baseline measurements
and regressions. Automation takeover, technical ID migration and adaptive learning
remain open.

## Closed bounded runs and history

The three-hour run and subsequent one-hour run ended with the heartbeat paused.
This fix follows the explicit manual continuation; neither window was reopened.
Alpha.62 receipt/history: `1719ee11dd92b2a73ca5149cd458fae7f9e56c29:CURRENT_STATE.md`.
Alpha.61: `6e1cf864e20ec000c65b03e56eb6b9aa4dde1c3f:CURRENT_STATE.md`.
Alpha.56–60 measurements: `b3aa7966b9df146bc1bca61c0e844f279e6b7884:CURRENT_STATE.md`.
