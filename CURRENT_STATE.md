# Current state — Alpha.64 installed; household acceptance pending

## Verified delivery

PR #138 merged as `ee757af548194426d9f115cb29b3932379d5962e`.
Exact candidate CI `36441905253` and release-main CI `36442208985` passed
all five jobs: tests, 11 browser suites, amd64 container, reproducible checkout
and disposable Home Assistant protocol. App tree:
`352119664af2716660e0e48535571e2d643c69a8`; local and connector trees matched.

Fresh PilotSuite-only backup `14f1c9da` completed at 15:10:35 UTC before publication:
exactly Alpha.63 app/data/options, 54,476,800 bytes, no HA/database/folders/failures,
local and unprotected. Native list and backup/details verified metadata; no archive
extraction or restore drill. One native Store refresh and one targeted update
installed Alpha.64; no extra restart, rebuild or other-app update.

HA-MCP confirms installed/offered/started and all four options unchanged. Startup
remains `presence_adoption_review`, ready, connected, snapshot-fresh and zone-resolved.
Raw log timestamps are copied without independent clock attestation.
Full evidence: [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).

## What Alpha.64 changes

The existing operational checkpoint store reads zone/revision/exact value in one
SQLite snapshot before requesting a write reservation. Identical repetitions no
longer fail merely because another writer reserved the database. Changed records
still recheck revision/value under the existing transaction. No process cache,
removed timestamps, delayed durability, schema migration or scheduler change.

Measured with the same expanded synthetic benchmark, 60 single-zone cycles each:
suspended repetitions use 0 instead of 60 write reservations, with 0 actual writes
before/after. Occupied/vacant/unknown retain all 60 reservations/writes and add 60
SELECTs; connections stay 660 per case. All four complete decision-trace hashes
match and were reconfirmed on exact main. No overall speed or household-load gain
claimed; the additional read on changed writes is an explicit tradeoff.
Detailed counts/times are in the receipt and [ROADMAP.md](docs/ROADMAP.md).

No household binding, helper, metadata, automation, output activation or consent
was changed. AGENTS.md remains unchanged and untracked; Ingress/authentication intact.

## Test evidence

625 Python tests, 75 JS tests, 62 API contracts, discovery and compilation pass.
Repeat exact-candidate audit: 625 tests, zero ResourceWarnings; application tree
identical to release-main. Two original red tests reproduced the needless reservation
and lock failure. Eight added tests cover four-zone DB preservation, concurrency,
stale/boolean/missing revisions, clock durability/restart, rollback/retry and the
service's honest source-basis suspension beside a writer.

Local zone, workspace and Organization Chromium suites pass; no frontend assets or
browser-test logic changed. Desktop screenshot inspected; all 11 browser suites
passed exact candidate and main CI. Synthetic tests are not household acceptance.

## Next task and remaining boundaries

With an authorized authenticated household Ingress session, first read all four
saved zones, Erdkellerbereich and one unlike zone without changing anything.
Then explicitly choose intended existing Boolean/timer/public sensor bindings and
observe actual comparisons without test switching. No mappings were guessed/applied.

Alpha.61's **Vorhandenen Bestand verbinden** still uses the canonical Organization
editor. Existing HA automations remain controllers; PilotSuite reads and compares.
Unknown never means vacant. No public sensor was automatically generated for that
existing chain. Alpha.63 still preserves unchanged configuration sessions/deadlines.
Further write batching and scheduler consolidation require separate measurements
and regressions; current clock updates remain durable. Automation takeover,
technical ID migration and adaptive learning remain open.

## Closed bounded runs and history

The three-hour and subsequent one-hour windows remain closed; heartbeat stays paused.
This delivery follows the explicit manual continuation.
Alpha.63 receipt/history: `7a319a571e5d64f31856dd97e9c863af4e060b44:CURRENT_STATE.md`.
Alpha.62: `1719ee11dd92b2a73ca5149cd458fae7f9e56c29:CURRENT_STATE.md`.
Alpha.56–60 measurements: `b3aa7966b9df146bc1bca61c0e844f279e6b7884:CURRENT_STATE.md`.
