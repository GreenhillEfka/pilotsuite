# Current state — Alpha.56 installed; household acceptance pending

## Active Alpha.57 candidate

The next presence-first package reproduces delayed-I/O publication faults: nine
delay points and three disconnection points could retain validity after the
15-second decision-age boundary or loss of the stream. A separate conflict test
proved the error handler could overwrite a newer checkpoint with its pre-I/O copy.
Three test methods failed in 13 subcases before the fix. The publisher now rechecks
the same decision/revision/stream after awaits and merges its failure marker into
the newest checkpoint under the existing projection lock. HA calls remain outside
that lock. Existing invalidation, suspension and bounded lease remain unchanged;
no atomic HA/SQLite guarantee or new write authority is claimed.

Alpha.57 is a candidate, not yet an installed release. RELEASE_STATE.json retains
the verified Alpha.56 receipt until all new delivery gates have passed.

## Verified delivery

Fresh HA-MCP reads confirm Alpha.56 installed/offered and started. PR #121 merged
as `fde808afa65ec4c52a85ccf05ee8c8cea74152a9`; exact candidate CI `36383403520`
and main CI `36383567794` passed all five jobs. Source, backup and runtime evidence
are in [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).

Native PilotSuite-only backup `15da86c3` was completed and verified before publication:
exactly Alpha.55 app/data/options, 54,446,080 bytes, no HA/database/folders or failures.
One Store refresh and one targeted update installed Alpha.56. All four options match
the pre-update read. Startup remains `presence_adoption_review`, ready, connected,
fresh and zone-resolved. Log timestamps are copied as emitted, not clock-attested.
No explicit restart, rebuild, other-app update, household metadata edit or test
switching occurred. AGENTS.md remains unchanged and untracked.

## Presence correction and proof

When all direct sources were optional and unavailable, aggregation could wrongly
declare or retain vacancy. Two new regression methods failed in nine baseline
subcases before the minimal fix. Missing all direct observation now produces unknown;
positive evidence and individually optional gaps beside valid coverage retain their
existing meaning. No source settings, schema, zone identities or deadlines migrated.

Local checks: 574 Python tests, 73 JavaScript tests, 62 API contracts, test discovery,
Python compilation and the existing synthetic zone Chromium suite passed. All
11 browser suites, amd64 container, reproducible checkout and disposable HA protocol
passed exact remote CI. Further tests cover held motion expiry, bounded TV support,
SQLite reload, HTTP projection and invalidation without owner.off. SQLite
ResourceWarnings remain; no leak-free claim. Synthetic tests are not household proof.

Alpha.55's existing three-entry workspace and primary presence card remain intact.

## Measured baseline and next bounded package

On Alpha.56's disposable one-zone fixture, 60 tick-plus-view cycles per stable
occupied/vacant/unknown scenario each opened 660 SQLite connections, started 180
IMMEDIATE transactions and wrote 60 operational checkpoints; median cycle about
2.51 ms, p95 2.65–2.75 ms on this host. No history or HA output calls occurred.
These are synthetic baseline counts, not household load or optimization gains.
Checkpoint evaluated_at participates in clock-rollback protection: do not merely
drop time fields to force deduplication. ZoneStore.bootstrap obtains a write lock
even when its durable marker already exists; a read-first, transaction-rechecked
fast path is a possible small measured improvement.

First test publication freshness across awaited I/O; source review identified an
initial freshness check followed by asynchronous reads, not yet a reproduced defect.
Then pursue measured lock reduction with concurrency/restart tests. Keep one active
implementation package and observe the bounded run's 08:01:44 UTC stop.

## Still not household-accepted

No authorized authenticated household browser is connected. Ingress/authentication/
sandbox were not bypassed. All four saved household zones have not been independently
read back after update. Inspect Erdkellerbereich and one unlike saved zone read-only
when authorized browser access exists, including passive refresh and all four zones.
Output activation, automation takeover, entity-ID migration and adaptive learning
remain separate, not granted by this quality iteration.
