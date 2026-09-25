# PilotSuite current state

## 2026-09-25 — Alpha.24 installed and runtime-verified

Canonical GreenhillEfka/pilotsuite, app 0d79c5e8_pilotsuite. PR #54 merged as
6f22100dcfbee87bdedc8288b1821971bad17d53, root a13f332d9e5cc58787e7481eaee6f5c035c467b9,
app tree 528396dc07e35b2df1e349322f6c0b49e9dee6cb. Exact PR CI 36117146697 and main CI
36117395171 passed all jobs: Python/JS, five browser steps, source and amd64 build.
The complete release source bundle was SHA256-verified and preflight passed against
published Alpha.23. Repository/version/app-tree association is not image attestation.

Backup ad3c24bb completed before publication: only Alpha.23 app/data/options under
the standard App backup contract, 54,138,880 bytes, 2026-09-25T09:13:57.670074+00:00.
Native snapshot/list and backup/details confirmed no HA/database/folders/failures
or key requirement. No archive download, live restore drill or independent DB check.

One native check_updates without slug/repository offered Alpha.24. One native update
installed it. Fresh metadata: Alpha.24 installed/offered, started, no pending update,
unchanged options and auto_update=true. Startup/readiness: hard_read_only, ready,
connected stream, fresh snapshot, resolved Golden Zone; presence/light remain partial.
No separate restart/rebuild, other app, host/Core/Supervisor, HA configuration,
automation, role, learning-consent, permission or scheduler change.

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

## One next task

Authenticated real Ingress acceptance: a useful or reasonably withheld daily brief
in the already consented Golden Zone, then existing workbench navigation without
writes. No new consent, automation scan or execution to obtain acceptance. UI,
config-read capability, data preservation and image attestation remain separately
open. Do not repeat the completed delivery or recreate connector setup.

RELEASE_STATE.json is the current receipt; its preceding file is preserved byte-for-
byte in RELEASE_HISTORY_2026-09-25_PRE_ALPHA24.json. Final documentation PR/main CI
receipts belong in the PR comments, not another documentation/version loop.
