# Current state — Alpha.59 installed; household acceptance pending

## Verified delivery

HA-MCP confirms Alpha.59 installed/offered/started. PR #127 merged as
`6c1e2e00f5e8027b731a6e68165febe666203a38`; exact candidate CI `36388245111`
and main CI `36388387311` passed all five jobs. Source, backup, installation and
runtime are separate evidence in [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).

Native PilotSuite-only backup `93299b98` completed and was verified before publication:
exactly Alpha.58 app/data/options, 54,466,560 bytes, no HA/database/folders or failures.
One Store refresh and one targeted update installed Alpha.59. All four options
match the pre-update read. Mode remains `presence_adoption_review`; startup is ready,
connected, snapshot-fresh and zone-resolved. Raw app log times are not independently
clock-attested. No explicit restart/rebuild, other-app update, household metadata
write or device test occurred. AGENTS.md remains unchanged/untracked.

## Delivered during this bounded quality run

- Alpha.56 / #121: total loss of direct optional coverage is unknown, never vacant.
  Valid positive evidence, bounded TV support and restart deadlines are preserved.
- Alpha.57 / #123: recheck publication freshness after awaited I/O and mark output
  failure on the newest checkpoint, without overwriting newer deadlines.
  HA and SQLite are not atomic; compensating invalidation and lease expiry remain.
- Alpha.58 / #125: read the durable bootstrap marker without a writer reservation;
  retain transactional recheck for concurrent first start. Synthetic 60-cycle
  scenarios reduced reservations 180 to 60; all 60 checkpoints remain. Explicitly
  close test-owned SQLite connections; no warning suppression or production-leak claim.
- Alpha.59 / #127: shared strict snapshot-age predicate for status, evidence and
  presence; zone time/freshness no longer depends on the shadow adapter. Old imports
  remain compatible. Future, naive and malformed snapshot time degrades safely.

## Current test and measurement evidence

592 Python tests, 73 JS tests, 62 API contracts, discovery and compilation pass.
Local zone, shadow and maintenance Chromium suites pass; exact candidate/main CI
also passed all 11 browser suites, amd64 container, reproducible checkout and the
disposable HA protocol. Synthetic browser success is not household acceptance.

Four Alpha.59 regression methods failed in 17 baseline subcases; an additional red
HTTP case exposed an invalid non-string timestamp in JSON. Nine added tests cover
HTTP/event recovery, age boundaries for four refresh intervals, timezone offsets,
transport separation, parser aliases and zone publication with the old shadow
method disabled. Normal evidence recording and publication still work.

Repeat measurement: `PYTHONPATH=pilotsuite python scripts/benchmark_zone_presence.py --cycles 60`.
Before/after Alpha.59, each occupied/vacant/unknown scenario retains 660 connections,
60 IMMEDIATE transactions, 60 checkpoints and zero history/HA output calls.
Median around 2.5 ms both times; no speed gain claimed. Exact medians/p95 are in
the receipt. Scheduler timing, valid-time results, evaluated_at and deadlines
remain unchanged. Do not remove durable timestamps to manufacture deduplication.

## One next task and deadline

Inspect publication-view consistency across normal throttling and concurrent
synthetic ticks; reproduce first. Distinguish last verification from current
presence. No speculative scheduler rewrite or legacy-configuration migration.

No new packages/publications after 07:40 UTC; stop development/release work by
08:01:44 UTC on 28.09.2026, report the secured state and pause the heartbeat.

## Household acceptance remains separate

No authorized authenticated household browser is connected; no access bypass was
attempted. All four saved zones have not been independently read back after update.
Inspect Erdkellerbereich and one unlike saved zone read-only when access exists,
including all four zones and passive refreshes. No schema/configuration migration
was made. Own-output activation, automation takeover, technical entity-ID migration
and adaptive learning remain separate, unaccepted work.
