# Current state — Alpha.39 installed, 2026-09-27

## Deterministic presence kernel and synthetic explanation

The source candidate replaces timer-state inference in the dormant presence runtime
with one deterministic checkpoint: occupied, grace, vacant or unknown plus generation,
deadline, last activity and reason. Motion pulses renew grace without claiming
continuous occupancy. Restart preserves an existing deadline; expiry requires all
required sources to be valid and clear. Unknown sources/dependencies, cold all-clear
startup and manual cancel do not become false vacancy.

The checkpoint is stored in existing zone context without a schema migration or
second owner. Source changes and reset remove it; configuration savepoints omit it.
The existing workspace can explicitly replay five fixed synthetic scenarios. Replay
performs no HA read/write or persistence, accepts no data-supplied action/URL and
cannot change execution authority. Late zone/revision responses are discarded.
Public presence activation and general Apply remain closed.

Repository/API validation and 506 Python plus 59 JavaScript tests pass locally.
PR 86 release 892cbab; exact candidate CI 36283655159 and release-main CI
36283761672 passed all four jobs: tests/source contracts, Chromium, amd64 container
and reproducible source.

## Installed evidence

Fresh scoped backup 618bc607 contains only Alpha.38 app/data/options, no HA,
database, folders or failed parts. One native Store refresh and one normal update
installed Alpha.39. It is installed/offered/started; options and auto_update are
unchanged. Startup/readiness logs confirm presence_adoption_review, ready, connected
stream, fresh snapshot and resolved zone. No explicit restart, rebuild or other app
update occurred. Public presence activation and general Apply remain closed.

Authenticated real Ingress acceptance remains unavailable: the cloud browser returned
502 Bad Gateway / connection closed before HA or PilotSuite loaded, including one
reload after installation. Runtime health is not UI acceptance. No HA configuration,
automation, actor, role, learning consent or household data changed.

Next: run the explicit synthetic Alpha.39 presence replay and read-only role/evidence
acceptance in the saved Erdkellerbereich zone in authenticated Ingress, without HA
configuration, automation, learning or device changes.

## Previous delivery — Alpha.37, 2026-09-27

## Presence lifecycle review package

The existing explicit inventory analysis now derives two bounded questions from
literal current automation structure and current device-class metadata. It can show
that a boundary-close branch clears a plausible bidirectionally set room-status helper,
or that an activity edge is the only recognized start/refresh of a presence timer.
Closing a door does not prove absence; continuous active motion supplies no new state
edge. These remain intent questions, not automatic defect or safety claims.

Stale snapshots, disabled/dynamic paths, ambiguous selectors and indirect targets do
not become findings. Trigger IDs, raw config and private payloads are withheld. The
existing inventory view adds one deterministic filter and a direct next review step.
Nothing is stored or repaired; no learning or execution authority changes.

Local repository validation passes with 484 Python and 56 JavaScript tests. The new
full-app browser scenario covers both findings, private-ID removal, filtering and no
ContextStore/PlanStore/HA/control mutation. PR 82 release
93e6df76d23a3171edcecfa9130330f192aa5d5f; exact candidate CI 36277330306 and
release-main CI 36277424359 passed all four jobs, including Chromium and amd64.

Fresh scoped backup 0baa717d contains only Alpha.36 app/data/options, no HA/database/
folders or failed components. One Store refresh and one update installed Alpha.37.
Installed/offered/started, options and auto_update unchanged. Startup/readiness logs
confirm presence_adoption_review, connected stream, fresh snapshot and resolved zone.
No extra restart, other app, household configuration, learning or device action.

The authenticated cloud browser reached only a 502 connection-closed response before
the HA/PilotSuite UI loaded, including one reload. Actual Ingress lifecycle review is
therefore still open; runtime health and synthetic Chromium do not substitute for it.

Historical Alpha.37 acceptance remained open for the saved Erdkellerbereich zone and
one unlike existing zone.

## Previous delivery — Alpha.36, 2026-09-26

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

Historical Alpha.36 acceptance remained open for the saved Erdkellerbereich and the
other three existing zones without household configuration or learning changes.
