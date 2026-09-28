# Current state — Alpha.60 installed; household acceptance pending

## Active manual follow-up — Alpha.61 candidate

User chose existing-control integration, not takeover: existing HA automations keep
writing their Boolean/timer/public sensor. Branch `feat/zone-existing-presence`
extends the canonical organization profile with the public sensor, exposes the
observed chain/comparison in the zone view and reuses the structural automation
review for writers, consumers, mixed and unmatched selected logic. No household
mapping, automation, helper, metadata or publication change has been applied.

Red/green tests reproduced omitted status consumers, undifferentiated mixed writers,
self-evidence through later source configuration, refresh calls mislabeled as
Boolean control and changed public sensor semantics still appearing valid.
Local full suite: 612 Python / 75 JS, 62 contracts; expanded full-app zone and
organization browsers pass. Exact candidate/main CI remain publication gates.
Fresh scoped backup `16b918fa`, completed 08:26:52 UTC, was verified through native
list/details: exactly Alpha.60 PilotSuite app/data/options, 54,456,320 bytes,
no HA/database/folders/failures, local and unprotected. No restore drill performed.
Installed Alpha.60 was freshly confirmed at the start and before release preparation.
The prior three-hour run is closed and its heartbeat remains paused; this is a new
explicit manual implementation request, not an extension of that time window.

## Verified delivery

HA-MCP confirms Alpha.60 installed/offered/started. PR #129 merged as
`1ae32bcbf2da64c43ddc397bb182cf6043fa59fd`; exact candidate CI `36390129437`
and main CI `36390521039` passed all five jobs. Source, backup, installation and
runtime are separate evidence in [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).

Native PilotSuite-only backup `d72b1330` completed and was verified before publication:
exactly Alpha.59 app/data/options, 54,456,320 bytes, no HA/database/folders or failures.
One Store refresh and one targeted update installed Alpha.60. All four options
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
- Alpha.60 / #129: retain a dated last-publication receipt through unchanged ticks
  for less than 20 seconds; do not confuse it with current validity or renew it on GET.

## Current test and measurement evidence

596 Python tests, 74 JS tests, 62 API contracts, discovery and compilation pass.
The expanded local zone Chromium suite passes; exact candidate/main CI
also passed all 11 browser suites, amd64 container, reproducible checkout and the
disposable HA protocol. Synthetic browser success is not household acceptance.

Repeat measurement: `PYTHONPATH=pilotsuite python scripts/benchmark_zone_presence.py --cycles 60`.
Before/after Alpha.60, each occupied/vacant/unknown scenario retains 660 connections,
60 IMMEDIATE transactions, 60 checkpoints and zero history/HA output calls.
Median around 2.5 ms both times; no speed gain claimed. Exact medians/p95 are in
the receipt. Scheduler timing, valid-time results, evaluated_at and deadlines
remain unchanged. Do not remove durable timestamps to manufacture deduplication.

## Alpha.60 regression — dated publication evidence

Implemented, tested and installed, not household-accepted: reuse the existing in-memory publication
receipt for less than the unchanged 20-second heartbeat interval, only while current
decision, revision, mode, transport and validity still match. GET never advances its
timestamp or performs HA I/O. Failures clear the receipt; restart does not restore it.
The UI says "Zuletzt bestätigt" and shows the separate readback-check time.

Three genuine baseline failures reproduced lost confirmation after an unchanged tick
and a stale API marker after disconnect/clock rollback. Four new Python methods and
one JS test cover expiry at exactly 20 seconds, changed deadline/revision, unknown
sources, failure suspension, final-readback timing, restart and passive reads.
596 Python/74 JS tests and the expanded full-app zone Chromium suite pass. Three
unchanged synthetic publish ticks add zero HA reads/writes and preserve the proof date.
The 60-cycle compare workload still has 660 connections/60 transactions/60 checkpoints
per scenario and zero history/output calls; no speed claim. Desktop/mobile screenshots
were checked locally; this is not household acceptance. Exact CI/delivery are recorded above.

## Final bounded-run audit and next task

PRs #121/#123/#125/#127/#129 delivered the five packages above; their separate
receipts are #122/#124/#126/#128/#130. At 07:32 UTC the unchanged installed-source
suite passed again: 596 Python tests, with explicit ResourceWarning capture and
garbage collection reporting zero resource warnings, plus the full zone browser.

One low-severity UI defect is now reproduced, not fixed: open the presence editor,
attempt to navigate to Zonen (correctly blocked), then save successfully. Wait until
`selectionBusy` is false and `PilotSuiteZonePresence.dirty()` is false. The editor
has closed but `#ps-notice` still shows "Bearbeitung läuft". An isolated assertion
expecting it hidden failed with `true !== false` in the existing full-app browser
suite. The diagnostic assertion was then removed; the unchanged suite passes.
The workspace owns this announcement but editor completion does not clear it.
Next: retain this regression and clear only obsolete dirty-guard messages once all
drafts/requests finish; test save, cancel, failed save and unrelated errors. Do not
weaken the guard or blanket-clear announcements. No household write occurred.

No further functional release is planned in this run. Scheduler/checkpoint
consolidation and the authenticated household observation remain separate work.

The prior run ended with its heartbeat paused before 08:01:44 UTC on 28.09.2026.
Its 07:40 publication cutoff and end time remain historical, not a resumed job.

## Household acceptance remains separate

No authorized authenticated household browser is connected; no access bypass was
attempted. All four saved zones have not been independently read back after update.
Inspect Erdkellerbereich and one unlike saved zone read-only when access exists,
including all four zones and passive refreshes. No schema/configuration migration
was made. Own-output activation, automation takeover, technical entity-ID migration
and adaptive learning remain separate, unaccepted work.
