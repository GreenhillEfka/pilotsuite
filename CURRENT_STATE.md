# Current state — Alpha.61 installed; household acceptance pending

## Verified delivery

PR #132 merged as `14f6cc659ccb5f5ddad7a77453d0038b5b29f8e2`.
Exact candidate CI `36397807655` and release-main CI `36398080000` passed
all five jobs: tests, 11 browser suites, amd64 container, reproducible checkout
and disposable Home Assistant protocol. The app tree is
`a1217ccb99f08c9bdddacd1d5e701c564e9a9bfa`; local and connector trees matched.

Native PilotSuite-only backup `16b918fa` completed at 08:26:52 UTC and was
verified before publication: exactly Alpha.60 app/data/options, 54,456,320 bytes,
no HA/database/folders/failures, local and unprotected. No extraction or restore drill.
One Store refresh and one targeted update installed Alpha.61. HA-MCP confirms
installed/offered/started, all four options unchanged. Startup remains
`presence_adoption_review`, ready, connected, snapshot-fresh and zone-resolved.
Raw log times are recorded without independent clock attestation.
Full evidence: [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).

## What Alpha.61 changes

The user chose existing-control integration, not takeover. Existing HA automations
remain the writers of their existing Boolean/timer/public presence sensor.

- Primary zone view → **Vorhandenen Bestand verbinden** → existing Organization
  editor; one canonical saved profile, now including the public occupancy/presence
  sensor. Missing chain parts remain explicit; no automatic helper creation.
- Zone view shows observed owner/timer/sensor, actual reported timer deadline,
  comparison against independent PilotSuite assessment and Boolean/public mismatch.
  Unknown, stale, changed identity or semantics never imply off. Idle is not vacancy.
- Explicit structural review finds status/timer writers, trigger/condition consumers,
  mixed logic and selected unmatched automations. Limited coverage, dated result,
  no automatic configuration polling, no rewriting or activation.
- Bidirectional save/runtime guards prevent outputs becoming their own evidence.
  PilotSuite timing never changes existing household timer/automation timing.

No household binding, helper, metadata, automation, output activation or consent
was changed. No new engine/store, automatic migration, test switching or weaker
Ingress/authentication. AGENTS.md remains unchanged and untracked.

## Test evidence

612 Python tests, 75 JS tests, 62 API contracts, discovery and compilation pass.
Sixteen new Python methods plus one JS test cover the new path and red/green defects:
omitted consumers, mixed writer, later source feedback, entity-refresh false writer,
and changed public-sensor semantics. Exact-source repeat with ResourceWarning capture
and garbage collection reports zero resource warnings.

Local full-app zone and Organization Chromium suites pass. The new chain-binding/
review segment makes zero HA helper/output/metadata calls; all four synthetic zones,
saved roles/consents and existing workflows remain intact. Screenshots were inspected
on desktop/mobile; all 11 suites passed exact candidate and main CI. These are not
household acceptance. No performance improvement or scheduler/checkpoint change claimed.

## Next task and remaining boundaries

When an authorized authenticated household Ingress session is available, first read
all four saved zones, Erdkellerbereich and one unlike zone without changing anything.
Then explicitly choose the intended existing Boolean/timer/public sensor bindings
and observe actual comparisons without test switching. This release did not guess
or apply household mappings. Existing automations stay in control; a public sensor
was not automatically generated for the existing chain.

The earlier stale “Bearbeitung läuft” notice after blocked navigation and successful
save remains reproduced but unfixed. Its focused regression/fix must preserve failed
drafts and unrelated errors; no blanket notice clearing. Scheduler/checkpoint
consolidation, automation takeover, technical ID migration and adaptive learning
remain separate work.

## Closed bounded run

The earlier three-hour run delivered Alpha.56–60 (PRs #121/#123/#125/#127/#129,
receipts #122/#124/#126/#128/#130, final audit #131). Detailed historical results and
measurements are retained at
`b3aa7966b9df146bc1bca61c0e844f279e6b7884:CURRENT_STATE.md`.
It ended before 08:01:44 UTC with its heartbeat paused. Alpha.61 is the subsequent
explicit manual implementation request, not a resumed or extended overnight job.
