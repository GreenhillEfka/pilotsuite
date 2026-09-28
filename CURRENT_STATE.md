# Current state — Alpha.58 installed; household acceptance pending

## Verified delivery

HA-MCP confirms Alpha.58 installed/offered/started. PR #125 merged as
`66d155cb27e2e2a8ebd1e06feec0ed146ba7eacd`; exact candidate CI `36386546543`
and main CI `36386768279` passed all five jobs. See
[docs/RELEASE_STATE.json](docs/RELEASE_STATE.json) for separate source, backup and
runtime evidence. Alpha.56/PR #121 and Alpha.57/PR #123 remain integrated.

PilotSuite-only backup `012bff83` was completed and verified before publication:
exactly Alpha.57 app/data/options, 54,456,320 bytes, no HA/database/folders or failures.
One Store refresh and one targeted update installed Alpha.58. All four options
match the pre-update read. Mode remains `presence_adoption_review`; startup is ready,
connected, snapshot-fresh and zone-resolved. App log times are copied as emitted,
not independently clock-attested. No explicit restart/rebuild, other-app update,
household metadata write or device test occurred. AGENTS.md is unchanged/untracked.

## Presence corrections and evidence

Alpha.56 prevents complete loss of optional direct sources from proving vacancy.
It preserves positive evidence, bounded TV support and restart deadlines.

Alpha.57 fixes two reproduced asynchronous publication defects. Nine delayed-I/O
points and three stream-loss points could leave an outdated decision valid;
a separate conflict path overwrote newer checkpoint/deadline data with a pre-I/O
snapshot. Three regression methods failed in 13 baseline subcases before the fix.
The existing publisher now rechecks revision, generation, active zone, stream and
decision age after waits, and adds the failure marker to the newest checkpoint
under the projection lock. HA calls remain outside that lock. Existing invalidation,
durable suspension and lease expiry remain; no atomic HA/SQLite guarantee or
additional execution authority is claimed.

Locally: 583 Python tests, 73 JavaScript tests, 62 API contracts, discovery,
compilation and the existing synthetic full-app zone/review-compass browsers passed.
All 11 browser suites, amd64 container, reproducible checkout and disposable HA
protocol passed exact CI. Four-zone UI/configuration semantics remain unchanged.

## Alpha.58 — measured SQLite quality package

Implemented, tested and installed, not household-accepted: a durable read-first marker
check avoids reserving a write lock for already initialized zones. First bootstrap
still rechecks under its transaction. Before the fix, two regressions reproduced
an unnecessary IMMEDIATE transaction and a database-locked error beside a reserved
writer. All five new tests now pass, including simultaneous first readers,
rollback/retry, restored storage and an identical four-zone/selection SQL dump.

Repeat with installed test dependencies:
`PYTHONPATH=pilotsuite python scripts/benchmark_zone_presence.py --cycles 60`.
Same disposable one-zone fixture,
60 tick-plus-view cycles in each stable occupied/vacant/unknown scenario:

| Metric per scenario | Alpha.57 baseline | Alpha.58 |
|---|---:|---:|
| SQLite connections | 660 | 660 |
| IMMEDIATE transactions | 180 | 60 |
| Operational checkpoint writes | 60 | 60 |
| History requests / HA output calls | 0 / 0 | 0 / 0 |
| Median ms, occupied / vacant / unknown | 2.525 / 2.526 / 2.557 | 2.582 / 2.536 / 2.567 |
| p95 ms, occupied / vacant / unknown | 2.820 / 2.646 / 2.678 | 2.938 / 2.654 / 2.790 |

This proves 120 fewer write reservations, not a speed gain or household load result.
Every evaluated_at/checkpoint/deadline remains durable for clock-rollback protection.
The 43 bare SQLite test contexts and one browser fixture now explicitly close after
commit/rollback. The full 583-test run with ResourceWarning capture and final GC
passed with zero such warnings; no filters hide failures and no production leak is
inferred. Also passed: 73 JS tests, 62 API contracts, discovery, compilation,
synthetic zone and review-compass browsers. Exact candidate/main CI passed all five jobs.

Next: reproduce the future/invalid snapshot-time mismatch between readiness and
presence. Consolidate that existing freshness owner only with comparative tests;
valid-time behavior, scheduler timing and checkpoints must remain unchanged.
Measure before scheduler changes; do not remove evaluated_at or merge legacy
configurations speculatively.

Continue only within the bounded run; no new packages after 07:40 UTC, stop
development/release work by 08:01:44 UTC on 28.09.2026.

## Household acceptance remains separate

No authorized authenticated household browser is connected. No Ingress/auth/sandbox
bypass was attempted. All four saved household zones have not been independently
read back after update. Inspect Erdkellerbereich and an unlike saved zone read-only
when access exists, including all four zones and passive refreshes. Own-output
activation, automation takeover, entity-ID migration and adaptive learning remain
separate from this quality iteration.
