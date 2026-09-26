# Current state — Alpha.36 delivered, 2026-09-26

## Fixed: inconsistent inventory snapshots

The existing inventory reader could promote an old catalog after reconnect, retain
earlier fresh findings after losing the connection partway through a batch, and
recommend replacements despite changes to availability or registry metadata.
Repair previews could persist those outdated choices.

Alpha.36 retains conservative freshness across the entire explicit read batch,
including failed configuration reads. Relevant catalog changes return HTTP 409.
Ordinary available measurement changes remain allowed; snapshot values are not
presented as proof of current physical measurements. Repair previews require fresh
transport and unchanged catalog inputs before persistence; they remain non-executable.

## Code and tests

PR 80, release b8ebc1ba2a32450ceb35e71269399d2f62cabe54.
Seven new synthetic integration regressions; 475 Python and 56 JavaScript tests pass.
Exact candidate CI 36272344492 and release-main CI 36272461571 passed all four jobs:
tests/release-source contracts, nine Chromium suites, amd64 container and source bundle.
The local runtime disconnected after tests; the anchored patch was reconstructed via
native GitHub tools from the verified base. Exact remote diff and CI were checked.
The 48-route API contract inventory and prior cumulative/trigger integrity features
remain covered. Historical delivery details remain in IMPLEMENTATION_STATUS and Git.

## Actual installation

Backup 67fa033b was completed and verified before publication through native snapshot
list and backup/details: only Alpha.35 app/data/options, 54,353,920 bytes, unprotected,
no failed components, HA, database or folders. Targeted app-only rollback would
overwrite PilotSuite data since that backup. No archive extraction or restore drill.

One native Store refresh and one update installed Alpha.36. Installed/offered/started,
options and auto_update unchanged; no extra restart/rebuild. Startup/readiness logs
confirm presence_adoption_review, connected stream, fresh snapshot and resolved zone.
General Apply remains READ_ONLY_RELEASE=True in exact tested source; no live Apply.
No other app, household configuration, device action, role or learning change.

## Acceptance and next step

RELEASE_STATE.json separates source, backup, installation and runtime evidence.
The browser runtime returned environment_offline; actual Alpha.36 Ingress remains
unverified. No failed proxy retry or weakened access. App-principal configuration
rights, independent data preservation and installed-image attestation remain separate.
The user-confirmed label is Erdkellerbereich and three other zones already exist;
canonical saved IDs and membership must be read, never inferred or recreated.

Next: Authenticated read-only inventory acceptance in the saved Erdkellerbereich zone, then the other three existing zones; verify snapshot-conflict feedback without changing household configuration or learning.
