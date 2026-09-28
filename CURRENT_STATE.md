# Current state — Alpha.57 installed; household acceptance pending

## Verified delivery

HA-MCP confirms Alpha.57 installed/offered/started. PR #123 merged as
`87c62e1cd1eb4ee2b39aba869fe760aedb3b99e9`; exact candidate CI `36384548685`
and main CI `36384713053` passed all five jobs. See
[docs/RELEASE_STATE.json](docs/RELEASE_STATE.json) for separate source, backup and
runtime evidence. Alpha.56/PR #121 remains the optional-coverage correction.

PilotSuite-only backup `d6ab3997` was completed and verified before publication:
exactly Alpha.56 app/data/options, 54,456,320 bytes, no HA/database/folders or failures.
One Store refresh and one targeted update installed Alpha.57. All four options
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

Locally: 578 Python tests, 73 JavaScript tests, 62 API contracts, discovery,
compilation and the existing synthetic full-app zone Chromium suite passed.
All 11 browser suites, amd64 container, reproducible checkout and disposable HA
protocol passed exact CI. Four-zone UI/configuration semantics remain unchanged.

## Measured next package

On the Alpha.56 disposable one-zone fixture, 60 tick-plus-view cycles per stable
occupied/vacant/unknown scenario each opened 660 SQLite connections, reserved 180
IMMEDIATE transactions and wrote 60 checkpoints. Median cycle about 2.51 ms,
p95 2.65–2.75 ms on this host; zero history/output calls. These are synthetic
baseline counts, not household load or claimed gains. Preserve evaluated_at and
deadline durability: clock-rollback protection forbids naive timestamp deletion.

ZoneStore.bootstrap reserves a write lock even when its durable marker exists.
Next: test a read-first path with transaction recheck, concurrent bootstrap,
restart and preserved zones/selections, then compare identical measurements.
ResourceWarnings were separately traced to three bare sqlite3 connection contexts
in test_context_learning.py; source search finds 43 such test contexts and one
browser fixture. Close ownership properly, never suppress warnings or infer a
production leak from their delayed emission location.

Continue only within the bounded run; no new packages after 07:40 UTC, stop
development/release work by 08:01:44 UTC on 28.09.2026.

## Household acceptance remains separate

No authorized authenticated household browser is connected. No Ingress/auth/sandbox
bypass was attempted. All four saved household zones have not been independently
read back after update. Inspect Erdkellerbereich and an unlike saved zone read-only
when access exists, including all four zones and passive refreshes. Own-output
activation, automation takeover, entity-ID migration and adaptive learning remain
separate from this quality iteration.
