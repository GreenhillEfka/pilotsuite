# PilotSuite AI context

Canonical GreenhillEfka/pilotsuite / app 0d79c5e8_pilotsuite / architecture v21.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first.

## Live-case naming — user clarification, 2026-09-26

The current user-confirmed case label is **Erdkellerbereich**. A display-name change
is not a new zone or permission to rewrite technical IDs, HA areas or the historical
bootstrap option. Resolve the saved Habitus zone by stable zone_id through the
canonical zone owner when authenticated Ingress is available; do not derive an ID
from the display name. HA metadata/read-only automation inspection does not certify
the app's saved zone membership or its own configuration-read rights.

## Active package: Alpha.34 trigger integrity candidate

Existing inventory and routine inspectors now share a bounded trigger-ID projection.
No new owner/store, HA writes, runtime mode, learning or Apply changes. All household
configurations stay private; regression fixtures are synthetic. User clarified that
development may read all HA entities/automations, beyond app learning permissions.
The acceptance scope contains four existing zones; Erdkellerbereich is the corrected
case name. Do not infer their saved IDs or create replacement zones.
Next: finish exact candidate CI and the native release gates, then read-only acceptance
of the new diagnostics with existing configurations. RELEASE_STATE remains Alpha.33
until an actual delivery receipt is recorded.

## Previous delivery: Alpha.33, 2026-09-26

PR 71 release 46ec340adf333f54efa760cde2d80f059b9c0ca2 is installed/offered/started.
Candidate CI 36260320758 and both exact release-main CI runs (36260420284,
36260423409) passed all four jobs and nine browser suites. Local 454 Python / 56 JS.
Fresh PilotSuite-only backup 1ea31dc2 was verified before publication. One native
Store refresh and one update; no explicit restart, rebuild or household operation.
All four options and auto_update=true unchanged. Startup, stream, fresh snapshot,
readiness and zone resolution verified. Runtime mode remains presence_adoption_review;
do not call it hard_read_only or change it during an update.

Organization plan responses now require matching zone/revision/invalidation generation.
Ambiguous saves retain visible choices and block replay; explicit recovery only reads.
Opened role groups/searches survive same-view refresh. Six new synthetic browser
regressions cover delayed/foreign replies, save interruption and stale previews.
Failed intermediate CI runs were corrected before publication, never treated as green.
Do not redeploy this installed version. Full source/backup/runtime evidence is in
RELEASE_STATE.json; household Ingress acceptance remains separate.

## Canonical implementation and boundaries

Existing PR 69 was retained; the offline candidate's compatible maintenance design
was integrated, not substituted for its ContextStore/PlanStore implementation.
Global manual function bindings include area-less helpers; analysis can start from
an automation without a prepared owner/timer. Nested references, event_data and
literal template dependencies are recognized; dynamic coverage remains explicit.
Global automation inspection uses explicit batches of at most eight configurations.
The save acknowledgement now survives the canonical post-save context refresh.

Display-name cleanup and separate guarded undo use PlanStore before-images, native
registry reads/writes and independent readback. This is not HA/SQLite atomicity or
native compare-and-swap. No household cleanup was performed during delivery.
Technical Entity-ID migration and automation repair execution remain unavailable;
repair previews do not write automations. Existing helper/presence control is
withheld pending separate transport, timer-event and authority acceptance.
Bindings do not grant learning or change observation roles. No new adaptive learner.

Maintenance now shares workspace themes/density/navigation and distinguishes local
savepoints from native HA backups. The app says native backup is not directly checked;
our native release backup verification is separate. Rescue remains read-only.

Next: authenticated read-only acceptance of inventory editing/recovery and existing
routine explanation in the already authorized Erdkellerbereich use case. No household edits,
new data collection, consent or execution activation. App-principal rights and
independent data preservation/image attestation remain unverified. No Ingress bypass.
Final documentation CI results belong in its PR, not another documentation loop.
