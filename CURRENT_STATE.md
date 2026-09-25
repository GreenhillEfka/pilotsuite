# PilotSuite current state

## 2026-09-25 — Alpha.25 installed and runtime-verified

Canonical GreenhillEfka/pilotsuite, app 0d79c5e8_pilotsuite. PR #57 merged as
a6d6e329eee15ee97c5e732dd963ca8a531444e3. Candidate CI and main CI #36128782821
passed all jobs. Fresh backup 70e14c12 was completed before publication and verified:
only PilotSuite Alpha.24, 54,179,840 bytes, no HA/database/folders/failures. Exactly
one Store refresh and one PilotSuite update followed.

Fresh metadata: Alpha.25 installed/offered, started, auto_update=true, options
unchanged. Startup/readiness logs: hard_read_only, ready, stream connected, snapshot
fresh, Golden Zone resolved. Humidity/motion/presence/light remain partial.

Alpha.25 adds explicit logical presence-helper roles, clearer multi-source role
selection, ambient-light-vs-controllable-light separation, climate/media/atmosphere
roles and the deterministic read-only zone-foundation/correlation projection.
Execution is still denied; no helper provisioning or device actuation is claimed.

Separately, four exactly identified stale sound-synchronisation references in existing
music automations were backed up and repaired to corresponding existing input_boolean
helpers. Old references are now absent and automation enabled states were preserved.
The stale Shutdown Wohnbereich scene remains intentionally unresolved where successor
entities are ambiguous.

## What shipped

Reconciled existing R2 with saved candidate work, preserving concurrent stronger
release source gates. Current-source/evidence/preference checks, bounded derived
brief and safe rendering; stale candidates disappear on loading/errors/zone changes
and unsaved edits. Matching fresh replies restore presentation without stealing focus.
Ten real-store API checks, six discovery regressions, canonical component and full-app
browser tests complement the existing suite. The CI overflow was isolated to a
synthetic heading and corrected without relaxing the assertion or changing app CSS.
Local 308 Python, 48 JS and ten component checks passed; exact pinned remote CI passed.
Synthetic full-app screenshots at 390/1440 were visually reviewed.

## Next task

Authenticated real Ingress acceptance: a useful or reasonably withheld daily brief
in the already consented Golden Zone, then existing workbench navigation without
writes. No new consent, automation scan or execution to obtain acceptance. UI,
config-read capability, data preservation and image attestation remain separately
open. Do not repeat the completed delivery or recreate connector setup.

RELEASE_STATE.json is the current receipt; its preceding file is preserved byte-for-
byte in RELEASE_HISTORY_2026-09-25_PRE_ALPHA24.json. Final documentation PR/main CI
receipts belong in the PR comments, not another documentation/version loop.
