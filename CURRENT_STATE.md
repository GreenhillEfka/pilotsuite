# PilotSuite current state

## 2026-09-25 — Alpha.26 installed and runtime-verified

Canonical GreenhillEfka/pilotsuite; app 0d79c5e8_pilotsuite. PR59 release commit
ede80bd4d7024aaa146c8d5bff53031905da9165; root tree
80ff429ec9fc26139a8a8121f3287516aa707cea; app tree
e9506c40047db1f8bfd4e4f6e08b643d0b03fb70. Exact candidate eb7c7f4deea8f5e2a2a8d885c93f2e5939fb87a8
CI36147092132 and main CI36148039084 passed all jobs: tests, six browser steps,
reproducible source and amd64 build. Local full suite: 355 Python and 48 JavaScript.

Before publication, native snapshot/list and backup/details verified backup45805440:
only PilotSuite Alpha.25, 54,210,560 bytes, no HA/database/folders or reported failures.
No live restore drill. Exactly one native Store refresh and one PilotSuite update
followed. Fresh metadata confirms installed/offered Alpha.26, started, no pending
update, auto_update=true and original options. Runtime startup/readiness confirms
hard_read_only, ready, stream connected, fresh snapshot and resolved zone.
Humidity/motion/presence/light remain partial; temperature/illuminance available.
No other app, household configuration, roles or learning consent changed this turn.

## What is actually connected

German Zonenbasis planning cards; strict source/relevance checks; stale-view
invalidation on errors/zone changes/unsaved edits; global cached registry hints
without inferred creation or ownership; bounded transient automation-read API with
original fingerprint, static-reference limits and concurrency/revision checks.
No automatic scan or additional learning collection. Original changelog history
and the published-source baseline were repaired.

## What is NOT completed

Presence contracts, comfort-policy examples, mapping/diff/transform and migration
primitives remain preparations. No running presence timer, helper executor,
autonomous lighting/music/climate controller, persisted adoption journal or actual
HA automation takeover. Details: docs/ALPHA26_RELEASE_REVIEW.md.

Remote browser screenshots at390/1440 were checksum-verified and visually reviewed.
They exercise the actual application with synthetic data, NOT authenticated household
Ingress. Narrow German card word wrapping needs refinement; no overflow observed.
Local full-shell Chromium was blocked by administrator policy and not bypassed.
Source/version association is not independent image or database attestation.

## Active Alpha.27 candidate — maintenance and existing helpers

Integrated last-three bundled versions, cached exact-identity HA update state and
native install handoff. PlanStore owns private checksummed zone-configuration
savepoints and preview/hash-bound paused restore, with prior point, stale guard,
idempotent completion and SQLite rollback. Existing evidence/text are not restored.
Newer extra zones survive; restored learning consents are revoked. Detected database
bootstrap failure serves guarded rescue UI without overwriting the original file.
Explicit existing-helper storage inspection handles renamed IDs and timer restore
settings, without adopting/creating helpers. Bootstrap Golden Zone label clarified.
Full details and acceptance boundaries: docs/MAINTENANCE_AND_RECOVERY.md.
Local full suite: 386 Python and 48 JS passed. Full browser navigation is blocked by
local administrator policy; exact remote CI includes a mandatory new actual-app
maintenance/recovery browser step. No live restore has occurred.

## Next bounded deliverable after maintenance

Issue56: implement one real helper executor through existing PlanStore, including
complete UI/application integration and disposable-HA timeout/restart/conflict tests.
Then verify one real zonal basis without guessing mappings or expanding learning.
Keep existing HA automations responsible until a separate backed-up takeover is
reviewed and verified. No additional contract-only modules. Do not replay this release.

RELEASE_STATE.json retains the completed Alpha.26 receipt until Alpha.27 is
actually delivered. This maintenance candidate changes the app and needs its own
exact source/CI and scoped deployment gates. Final documentation CI status belongs
in the PR discussion, not another status-only release loop.
