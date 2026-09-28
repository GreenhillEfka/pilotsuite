# Current state — Alpha.62 installed; household acceptance pending

## Alpha.63 candidate — manual continuation

Branch `fix/presence-config-noop` fixes two reproduced failures: identical saves
lost the durable grace deadline and added an owned-output invalidation call.
Five added Python tests cover no-op retries/restart, output proof preservation,
stale/disconnected evidence, genuine changes/recovery and validation. Synthetic
full-app browser checks cover unchanged compare/publish forms and four preserved
zones. Installation is still Alpha.62; candidate/main CI and delivery are pending.
Local verification: 617 Python tests (repeat audit: zero ResourceWarnings), 75 JS
tests, 62 API contracts, discovery and compilation pass. Fresh scoped backup
`7e502760` at 14:02:19 UTC verified exactly Alpha.62 app/data/options, 54,466,560 bytes,
no HA/database/folders/failures, local and unprotected, before publication.
The later one-hour run also ended with its heartbeat paused; this is a subsequent
explicit manual continuation, not a reopened time window.

## Verified delivery

PR #134 merged as `3059b0ab1516cb8671897f4db79ec41a309e786b`.
Exact candidate CI `36417973638` and release-main CI `36418159721` passed
all five jobs: tests, 11 browser suites, amd64 container, reproducible checkout
and disposable Home Assistant protocol. App tree:
`96d25705ce7a9f3141dc1e0da73d1068468a9d8f`; local and connector trees matched.

Fresh PilotSuite-only backup `6828ab75` completed at 11:46:35 UTC, before
publication: exactly Alpha.61 app/data/options, 54,476,800 bytes, no HA/database/
folders/failures, local and unprotected. Native list and backup/details verified
metadata; no archive extraction or restore drill.

One native Store refresh and one targeted update installed Alpha.62.
HA-MCP confirms installed/offered/started, all four options unchanged. Startup
remains `presence_adoption_review`, ready, connected, snapshot-fresh and zone-resolved.
Raw log timestamps are copied without independent clock attestation.
Full evidence: [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).

## What Alpha.62 changes

The reproduced stale “Bearbeitung läuft” notice no longer remains after the presence
editor successfully saves/reloads or discards its draft. Guard ownership is explicit:
only a guard with no dirty/busy owner is cleared. Pending requests, failed saves,
other drafts and unrelated error/context notices are preserved. History close and
explicit read-only review completion also settle their guards. No automatic navigation,
new poller, store, presence-evaluation change or HA write authority.

The duplicate existing-control decision is now ADR-043; ADR-042 is unchanged.
No household binding, helper, metadata, automation, output activation or consent
was changed. AGENTS.md remains unchanged and untracked; Ingress/authentication intact.

## Test evidence

612 Python tests, 75 JS tests, 62 API contracts, discovery, syntax and compilation pass.
Repeat ResourceWarning audit: 612 tests, zero warnings. The original full-app test
failed before the fix and now passes; added deterministic save/reload gates, failed
save, discard, other draft, unrelated same-word error, history close and pending
read-only review checks also pass.

Local zone, workspace and Organization Chromium suites pass. Existing-control flow,
all four synthetic zones, saved roles/consents and other workflows are retained.
Post-save desktop and mobile screenshots inspected; all 11 browser suites passed exact
candidate and main CI. These are not household acceptance. No performance gain claimed.

## Next task and remaining boundaries

With an authorized authenticated household Ingress session, first read all four
saved zones, Erdkellerbereich and one unlike zone without changing anything.
Then explicitly choose intended existing Boolean/timer/public sensor bindings and
observe actual comparisons without test switching. No mappings were guessed/applied.

Alpha.61's existing-control path remains: **Vorhandenen Bestand verbinden** reuses the
canonical Organization editor. Existing HA automations remain controllers of their
Boolean/timer/public sensor; PilotSuite only reads and compares. Unknown never means
vacant. No public sensor was automatically generated for that existing chain.
Scheduler/checkpoint consolidation requires separate baseline measurements and
regressions. Automation takeover, technical ID migration and adaptive learning remain open.

## Closed bounded run and history

The three-hour run ended before 08:01:44 UTC with its heartbeat paused.
Alpha.61/62 are subsequent explicit manual requests, not an extended overnight job.
Alpha.61 receipt/history: `6e1cf864e20ec000c65b03e56eb6b9aa4dde1c3f:CURRENT_STATE.md`.
Alpha.56–60 detailed results/measurements:
`b3aa7966b9df146bc1bca61c0e844f279e6b7884:CURRENT_STATE.md`.
