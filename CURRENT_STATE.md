# Current state — Alpha.42 installed, 2026-09-27

Alpha.42 adds an explicit current lighting decision check in the existing workspace.
It combines canonical source roles and current observations with freshly read related
automation structures without persistence. Configured/usable sources, transport and
physical freshness, indoor lux and outdoor provenance remain separate. A related
automation is neither a duplicate verdict nor a safety proof. Changed revisions or
roles invalidate the answer, and the brief exposes exactly one fixed internal next
step with execution still denied.

Local repository/API validation, 522 Python and 59 JavaScript tests pass. PR 92
release `be537ce`; candidate CI 36292600442 and release-main CI 36292681509 passed
test/source contracts, Chromium, amd64 and reproducible source. Fresh backup
`a90ec2d3` contains only Alpha.41 app/data/options with no failed parts.

One Store refresh and one normal update installed Alpha.42. It is installed, offered
and started with options and auto_update unchanged. Logs report version Alpha.42,
ready, connected stream, fresh snapshot and resolved saved zone. No HA configuration,
automation, actor, role, consent, productive learning or household state changed.

Next: perform the explicit Alpha.42 current-light check in authenticated read-only
Ingress for Erdkellerbereich; UI acceptance remains separate from runtime health.

## Previous delivery — Alpha.41 installed

Alpha.41 is the installed lighting-source integrity follow-up. It separates
assigned/currently usable lights, indoor lux and binary brightness in the existing
synthetic preview, explicitly withholds outdoor-daylight confirmation, holds on a
missing current brightness value and rejects incoherent/future checkpoints. Local
validation passes 515 Python and 59 JavaScript tests. Fresh scoped backup `bc501582`
contains only the previous Alpha.40 app/data/options and has no failed components.
PR 90 release `e0bfc77`; candidate CI 36289439619 and release-main CI 36289511093
passed all four jobs. One Store refresh and one update installed Alpha.41. Only
authenticated Ingress acceptance remains a separate gate.

## Daylight and mood preview delivered

The existing pure lighting policy now models stable daylight bands, a five-point
deadband, sixty-second minimum interval and at most fifteen percentage points per
brightness proposal. Presence, lux, brightness, selected atmosphere, manual override,
target capabilities and execution authority stay separate. Missing lux is not
darkness; unknown presence and manual operation hold. A confirmed vacant night
scenario can preview off, but no setting is executed.

The existing lighting workspace offers six fixed synthetic scenarios only after an
explicit click. The response is zone/revision/generation bound and stores nothing.
It accepts no household payload, target, service or URL and can emit only fixed
setting keys for explanation. Reload and ordinary GETs do not run the preview.

Repository/API validation and 515 Python plus 59 JavaScript tests pass. PR 88 release
f09dd27; exact candidate CI 36286331268 and release-main CI 36286428926 passed all
four jobs: tests/source contracts, Chromium, amd64 and reproducible source.

## Installed evidence

Fresh backup `bc501582` contains only Alpha.40 app/data/options, no HA, database,
folders or failed parts. One Store refresh and one normal update installed Alpha.41.
It is installed/offered/started with unchanged options and auto_update. Runtime is
ready, stream connected, snapshot fresh and the saved zone is resolved in unchanged
presence_adoption_review mode. Public presence activation and general Apply remain
closed. Read-only HA inspection confirmed actual area `erdkeller` / `Erdkeller Innen`,
the user semantic label Erdkellerbereich, two indoor illuminance sources and existing
automation context. No HA configuration, automation, actor, role, consent, productive
learning or household state changed.

Next: verify the explicit Alpha.41 lighting preview in authenticated read-only Ingress
for Erdkellerbereich, including that the two indoor lux sources are not shown as
outdoor daylight proof, then repeat with one unlike existing zone. Do not change HA
configuration, consent, devices or execution rights.

## Previous delivery — Alpha.39, 2026-09-27

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
