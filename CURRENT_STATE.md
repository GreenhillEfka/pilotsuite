# Current State

## Atomic pattern feedback / alpha.18 candidate — 2026-09-23

A queued feedback request could validate a pattern, then save after a concurrent
reset/source change/threshold change or expiry. Validation and persistence now use
one BEGIN IMMEDIATE transaction and the existing canonical report projection.
No second detector, storage owner, schema, collection or consent change. Retained
valid patterns remain reviewable with learning disabled. Observation statistics,
rule strength, confidence, risk and preference remain separate.

Six synthetic regressions cover those four stale-write cases, competing SQLite
writers at the validation/save boundary, and valid durable feedback with learning
off. Four stale-write tests failed against the preceding code; all six pass with
the fix. Full local suite: 151 Python and nine JavaScript tests; repository contracts
and diff checks pass. Exact PR/main CI including Chromium/amd64 must precede delivery.

HA remains alpha.17 installed/offered/started. Fresh backup 92e7a465 completed
2026-09-23T15:15:58Z (53,923,840 bytes, unprotected); native backup/details verifies
only PilotSuite alpha.17, no failed components, HA/database/folders excluded.
Scoped rollback is hassio.restore_partial with slug 92e7a465, apps
[0d79c5e8_pilotsuite], homeassistant false, folders []; no restore drill performed.
Alpha.17 temporal-view/export browser acceptance remains open; only about:blank
is available. No real learning, feedback, roles or automation/actuator edits.

Next: exact alpha.18 candidate/main CI, then source/backup recheck and one normal
PilotSuite update when offered. Verify runtime and authenticated temporal view/export;
do not conflate synthetic regressions with live learning-quality acceptance.

## Alpha.17 installed; temporal UI acceptance pending — 2026-09-23

One normal PilotSuite-only update completed from alpha.16 to alpha.17. Supervisor
confirms alpha.17 installed/offered/started, update_available false. Startup logs
confirm alpha.17, hard_read_only, ready, connected stream, fresh snapshot and
resolved Golden Zone. Initial connection setup completed normally; no separate
restart or rollback was needed. Store already offered the target; no reload needed.

Published source 8a8393249ef43c9f85dbfc6ec759889827319de3 and pre-update main
723fea28004f55c95f6450efb5f8533ee1bc6268 share app tree
70879070888a7de8df6b15d1800bdb4bace5f598. Exact CI runs 35874744954 and
35875185276 are successful: 145 Python tests, nine JavaScript tests, Chromium and
amd64 container. Source preflight passed; no open PR or branch rule blocked this
receipt. Source association uses canonical repository/version and unchanged app
tree; Supervisor does not expose an independently verified checkout/image identity.

Fresh scoped backup fcbbc115 completed at 2026-09-23T15:09:02Z, 53,934,080 bytes,
unprotected. Native backup/details confirms exactly PilotSuite alpha.16, no failed
apps/agents/folders, no HA configuration/database and no folders. Standard app backup
includes app data/options; no archive extraction or live restore drill was performed.
Concrete rollback is hassio.restore_partial with slug fcbbc115, apps
[0d79c5e8_pilotsuite], homeassistant false and folders []; target alpha.16 and its
matching app data/options. The live service schema was checked before deployment.

Only about:blank is available in the browser; authenticated HA Ingress HTML/JS/CSS/API
and the new temporal review/export remain unverified. Alpha.16 user-reported UI
acceptance remains complete; it is not evidence for alpha.17's new view or real
learning quality. No roles, learning consent, configuration, automations or actuators
were changed. No household evidence was collected or exported for this work.

Next: read-only authenticated acceptance of alpha.17 temporal review and JSON export,
without reinstallation. Learning-quality and second-zone review remain distinct and
bounded to existing explicit consent. This receipt changes documentation only;
earlier pending-deployment sections below are historical and superseded.

## Alpha.17 published; Store offer pending — 2026-09-23

PR #37 merged temporal review at 8a8393249ef43c9f85dbfc6ec759889827319de3.
Exact PR CI 35874564312 and main CI 35874744954 passed 145 Python tests, nine JS
tests, Chromium (including temporal text/JSON export) and amd64 container. Source
preflight passed; app tree 70879070888a7de8df6b15d1800bdb4bace5f598 matches the candidate.

The user confirmed alpha.16 guide, zone navigation and workbench operate correctly.
That UI acceptance is complete as user-reported evidence, not independent network
capture or proof of learning quality. The new alpha.17 temporal view remains pending
installation and its own UI acceptance. Synthetic two-zone tests are not live
second-zone acceptance; no real learning was enabled or household evidence exported.

Pre-publication backup 94355ad1 completed 2026-09-23T14:28:37Z, 53,923,840 bytes,
unprotected. Native backup/details confirms only PilotSuite alpha.16, no failed
apps/agents/folders, HA configuration/database and folders excluded. Scoped recovery
is hassio.restore_partial with that slug, apps [0d79c5e8_pilotsuite], homeassistant
false, folders []; no restore drill. Post-backup logs confirm readiness, connected
stream, fresh snapshot and resolved zone.

Fresh Store metadata still reports alpha.16 installed/offered/started, no update
available. No same-version installation, explicit restart or denied Store-route
retry was performed. Backup access is working, not a blocker.

Next: once Store offers alpha.17, recheck source association/CI and backup freshness,
update once and verify startup/read-only/connection/zone; then accept the temporal
view. Repository development is complete for this slice. Do not add artificial
features to fill Store waiting time. Real learning-quality review stays bounded to
already explicitly consented evidence; actuation remains disabled.

## Temporal pattern review candidate / alpha.17 — 2026-09-23

The user confirmed alpha.16 guide/navigation/workbench works. Record this as
user-reported UI acceptance, not independent network capture or proof of real
learning quality. Current HA metadata remains alpha.16 installed/offered/started.

The next bounded slice reuses retrospective() for retained activity evidence.
Earlier 70% of the fixed rolling 14-day retention window must qualify independently;
later 30% is checked only for repeat observation in the same local bucket/day group.
An overall qualifying recent pattern may still lack earlier qualifying evidence.
No later events train the earlier partition; out-of-period events are excluded.
Counts/status/period enter the existing review and JSON export. No probability,
causality or action permission is inferred. No new collection, schema or owner.

Seven synthetic regressions cover partition bounds, missing early/later evidence,
local day/window separation, two distinct zone profiles, durable feedback isolation,
revoked consent and detached reports. Local tests/CI receipts are recorded in the PR.
Browser regression checks temporal text and exported counts. No real learning or
configuration change has been performed. Alpha.17 is not installed by this commit.

Next: exact candidate CI, fresh verified PilotSuite-only backup, release and scoped
update, then runtime checks. Live quality review of already-consented evidence in
Golden Zone and a second unlike zone remains distinct from synthetic tests and UI
acceptance. Do not create or activate automations from this review.

## Alpha.16 installed; native backup verification — 2026-09-23

The user requested the regular Store/app-backup workflow. Native Core WebSocket
`backup/details` succeeds with the existing connection; the earlier denial of the
Supervisor gateway did not establish a general lack of backup-read permission.
Do not repeat that conclusion or request broader credentials for this working path.

Fresh backup 95bb73d4 completed at 2026-09-23T10:49:56Z, 53,893,120 bytes,
unprotected. Details confirm exactly PilotSuite alpha.13, no failed apps/agents/
folders, no HA configuration/database and no extra folders. Standard app backup
includes app data/options; this is metadata verification, not an archive extraction
or restore drill. Concrete rollback: hassio.restore_partial, slug 95bb73d4,
apps [0d79c5e8_pilotsuite], homeassistant false, folders []. No restore performed.

Store offered alpha.16. Release source is 208b5d31532c5f4ad38a6227b51028aeacacc9fd,
CI 35838497565 green; current main 33d5676 CI 35842713561 also green. Both have app
tree 811de10be4d11acab5ee98a41eb5dc3a93b56f46. Source association uses canonical
repository/version and unchanged published app tree, not an independently observed
Supervisor checkout SHA or cryptographic installed-image attestation.

One normal scoped update succeeded. Supervisor now confirms alpha.16 installed,
offered and started, update_available false. Startup logs confirm alpha.16,
hard_read_only, ready, connected stream, fresh snapshot and resolved Golden Zone.
No separate restart, role/consent edits, history import or actuator call. No Store
reload was needed. Only an about:blank cloud browser tab is available; no logged-in
HA session. Actual Ingress HTML/JS/CSS/API and guide/workbench acceptance remain open.

Next: authenticated, read-only guide/workbench/navigation acceptance; do not reinstall
alpha.16. No runtime code or version change in this documentation receipt.
Earlier deployment-gate sections below are historical, superseded by this receipt.

## Deployment gate review — 2026-09-23

Alpha.16 is now offered by the canonical HA Store; alpha.13 is still installed
and started, update_available true. No Store reload is needed. No open PR existed
at this check. Published source 208b5d31532c5f4ad38a6227b51028aeacacc9fd passed
exact main CI 35838497565 (138 Python, nine JS, Chromium and amd64). Read-only
release preflight passed; app tree 811de10be4d11acab5ee98a41eb5dc3a93b56f46.
Store metadata exposes the offered version/repository, not a checkout commit;
the exact Store checkout-to-source mapping is not independently verified.

Backup d454e834 remains listed as completed (2026-09-23T08:35:11Z,
53,882,880 bytes, unprotected, HA/database excluded). Its content details were
requested via hassio/api GET /backups/d454e834/info and denied Unauthorized.
The listing alone cannot confirm the saved app version and data/options. The
required verified recovery gate is therefore still closed. No alternate access
route was attempted, no redundant backup created, no update/restart performed.

Further feature work is deferred to the requested live acceptance priority.
Autonomous continuation is paused at the permission gate, not marked complete.
Next: restore authorized read access to the backup details, verify PilotSuite
alpha.13 plus matching data/options and the offered alpha.16 source mapping;
then refresh the scoped backup if needed, update once and check runtime plus
authenticated Ingress. Do not enable learning, change roles or weaken access guards.
This is a documentation-only status increment; no new regression tests or release.

## Zone guide / alpha.16 candidate — 2026-09-23

User requested the next coherent package after the release procedure was fixed.
Based on published alpha.15 (PR #32) and its receipt (PR #33), the zone guide derives
setup and optional-learning readiness from existing canonical projections. It shows
one next step, missing relevant sources, paused evaluation, connection readiness,
presence validity and retained patterns. Nearest-window evidence remains separate;
no pooling, completion forecast, confidence/preference change or action permission.
No new persistence, migration, consent or collection. Contract: docs/ZONE_GUIDE.md.

Validation: 138 Python and nine JavaScript tests passed locally, including eight new
synthetic guide regressions. Browser regression covers navigation without writes and
clearing guidance on failed zone loads. Functional candidate 78f0206258a6bbac0b47fd2e5264a40595857d05 passed CI
35838202517 (138 Python, nine JS, Chromium and amd64 container). PR #34 records
the final documentation-head and resulting main CI receipts separately.

Installation is separate: alpha.13 still installed/offered/started; no update available.
Scoped PilotSuite backup d454e834 completed 2026-09-23T08:35:11Z, 53,882,880 bytes,
unprotected, HA/database excluded. Request selected only PilotSuite and no folders.
Archive internals not inspected; do not claim verified restore readiness. Concrete
recovery target is alpha.13 and matching app data/options via restore_partial for
this app only, after contents verification. No update, restart, learning enablement
or Store permission retry. Real authenticated guide/workbench acceptance remains open.

Next: pass exact candidate/main CI, then offered-source and backup-content gates;
install once when available and validate the guide in authenticated HA Ingress.
The sections below are historical receipts, not new pending work.

## Published alpha.15; repeatable release procedure — 2026-09-23

Baseline main f0989ea17a819a0718f5b980c6f62d0e64804bab, CI 35831435324
fully green; no open PR at the initial check. Alpha.15 packages the already merged
UI revision, release-marker correction and context-ordering fix under a new version.
No new runtime behavior, schema, consent or configuration change in this increment.

ADR-026 and docs/RELEASE_RUNBOOK.md preserve the scoped backup/rollback procedure,
known Store permission boundary, exact-source CI and separate Ingress acceptance.
scripts/release_preflight.py emits committed source identities and rejects reused
versions, marker/changelog drift and unrelated history; it never authorizes deployment.
Seven synthetic Git regressions pass. Local total: 130 Python and nine JavaScript
tests, repository contracts and diff checks passed. Functional candidate
d9f7ab7e824a7e6cf998c1e9377a8fb78206e4b4 passed CI 35837285851, including
Chromium and amd64 container. PR #32 merged at
7fc0abc6c62bc15446c39b6d6da03990519fc919; final head CI 35837490073 and exact
main CI 35837585440 both passed all three jobs. Release app tree is
e789111f0f672a026b1f4e8813edee075c32a208. Source preflight passed for exact main.

Fresh HA metadata: alpha.13 installed/offered/started, no update available,
auto-update enabled. Scoped backup 6db4ba91 completed 2026-09-23T08:23:00Z,
53,882,880 bytes, unprotected, HA/database excluded. The verified service request
selected only PilotSuite and no folders. Archive internals and restore drill were
not inspected/performed. Recovery target: alpha.13 app and matching data/options
using hassio.restore_partial, apps [0d79c5e8_pilotsuite], homeassistant false,
folders []. Confirm backup contents and source mapping before an actual update.
No update or explicit restart command, Store retry, role/consent edits or Ingress
bypass in this increment. The scoped backup produced a fresh alpha.13 startup log;
afterward logs confirm hard_read_only, ready, connected stream, fresh snapshot and
resolved zone. Backup-related app lifecycle is not a release installation.

Next: once alpha.15 is offered, verify source mapping and
backup recovery gate, update once and accept navigation/workbench in authenticated
Ingress. Existing Store authorization and live UI acceptance remain open; do not
silently substitute the older published alpha.14 source or invent new feature work.

The sections below are historical receipts; their then-pending CI/merge steps do not
override this current release handoff.

## Development: context response ordering — 2026-09-23

Based on main 0359878; no open PR existed at the initial check and its CI
35827610130 was green. UI context reads previously guarded only the zone ID:
overlapping reads of the same zone, or leaving and returning to a zone, could
replace a newer display with an older response. Feedback saves could likewise
be visually undone by an already pending read (persisted feedback was unaffected).

A monotonically increasing read generation now rejects stale successes and stale
errors. Selection reloads and context mutations invalidate pending reads. Current
errors still propagate; an obsolete prerequisite read cannot continue a history
request. No schema, algorithm, evidence, consent or actuator change.

Five deterministic Node regressions exercise the actual UI function. Four failed
before the fix and all five pass after it. Local totals: 123 backend tests, nine
JavaScript tests, syntax and repository contracts passed. Browser regression now
freezes an old GET while saving feedback. PR #31 functional candidate 2823517
passed CI 35831207187: backend/JS, expanded Chromium and amd64 container. The
following documentation-only commit records that verified result.

Fresh HA metadata still reports alpha.13 installed/offered/started, with no update
available. Readiness logs report connected stream, fresh snapshot and resolved zone.
No HA write, installation, restart, data collection or bypass of Ingress occurred.
Known Store/interactive UI acceptance constraints remain separate from this fix.
Next: exact candidate CI and merge; then a separately verified release and scoped
backup before deployment, only when the Store offers the correct source/version.
Authenticated workbench/navigation acceptance and real learning remain open.

## Usability revision candidate — 2026-09-23

Based on main 1644c9b (alpha.14). A dedicated revision improves navigation,
German labels, shared form styles, responsive layout and feedback. Zone changes
clear stale learning content; delayed context responses cannot overwrite a different
zone. Periodic refresh pauses during editing and focused interactive review.
History import explains its disabled state; custom intervals are validated before
requesting HA history. No schema, role, consent or algorithm change.

Local verification after merging main 53a17f3: 123 backend tests, four JS tests, syntax and repository contracts
pass. Final functional candidate 4d3c8d3 passed CI 35827201950: backend, JS,
Chromium and amd64 container. Expanded browser tests cover navigation, editing state,
failed-zone isolation, history validation and widths 390/768/1440. Synthetic mobile
and desktop screenshots were visually reviewed; dense learning details were folded
and cancelled-edit feedback corrected. Local Chromium download remained unavailable.
No HA update or live usability acceptance performed. Latest prior deployment report
was alpha.13; alpha.14 store refresh was unauthorized. Do not infer installation
from repository version. See docs/USABILITY_REVIEW.md.


## Development: release marker contract

The alpha.14 tree still embedded alpha.13 in the browser footer and first-start
documentation. The footer is now release-neutral, while a regression requires the
documented release marker to equal the canonical VERSION/config/Docker markers and
rejects semantic-version literals in the static web shell. 123 backend tests, four
JavaScript tests and repository validation pass locally. Browser/container CI remains
required before merge. This changes no runtime behavior, storage, consent or access.

Live remains alpha.13: the current Supervisor Store still offers alpha.13. Scoped
backup fe09f165 remains the prepared rollback point; no update or restart occurred.
Next: merge only after CI, then obtain an authorized Store refresh, verify offered
alpha.14 and its exact source, deploy once and perform authenticated workbench checks.

## Published alpha.14; live update pending (2026-09-23)

PR #23 delivers the pattern workbench; PR #24 publishes 0.1.0-alpha.14 at
1644c9b170c861e83582ef9503775a8e913818f0. Release candidate CI 35824319061
and exact main CI 35824395251 passed: 122 backend tests, four JavaScript tests,
Chromium workbench/filter/export regression and amd64 container build.

Live verification still reports alpha.13 installed/offered and started. Recent app
logs confirm readiness, connected stream, fresh snapshot and resolved zone. No update
or restart was performed. Store reload through the documented Supervisor WebSocket
API was denied Unauthorized; this access boundary was respected. Backup fe09f165
and scoped rollback are recorded below. Recheck backup freshness before deployment.

Next: wait for authorized Store refresh, verify offered alpha.14 and exact source,
then perform scoped update and startup checks. User confirmed the previous history
diagram renders; the new workbench, JSON download and real Recorder coverage still
require separate live UI acceptance. No learning consent, roles or actuators changed.

### Earlier preparation record

## Release candidate: 0.1.0-alpha.14

Packages PR #23 (76f7665) with the already merged metadata and timeout corrections.
Main CI 35824185318 passed 122 backend tests, four JS tests, expanded Chromium
workbench/filter/export regression and amd64 build. This release candidate still
requires its own CI before publication. User reported the prior diagram renders.

Fresh scoped backup fe09f165 completed at 2026-09-23T05:52:04Z, 53,862,400 bytes,
HA configuration and database excluded. Requested only PilotSuite app and data;
archive internals were not inspected and no restore drill was performed. Recovery:
hassio.restore_partial with slug fe09f165, apps [0d79c5e8_pilotsuite],
homeassistant false and folders [], returning only PilotSuite to alpha.13.
Fresh app metadata: alpha.13 installed/offered/started, auto-update enabled.
Next: exact release CI, store version/commit verification, scoped update, startup
checks and separate user acceptance of the workbench. No consent or role changes.

## Development: pattern workbench

The user confirmed on 2026-09-23 that the existing history diagram renders.
This is user-reported UI acceptance, not independent Recorder coverage verification.
The next package adds preference filters, derived evidence chains, matching local
light-context summaries, coverage warnings and JSON review briefs to the existing
pattern cards. It reuses canonical candidates and durable feedback; no new evidence
store, collection consent, migration or actuation path. See docs/PATTERN_WORKBENCH.md.
122 synthetic backend tests, four JavaScript tests and repository validation pass
locally. Extended Chromium regression and amd64 CI must pass before merge.
No version bump or installation yet; last verified live version remains alpha.13.
Next: candidate CI, then release packaging with a fresh scoped App-and-data backup
and exact-version CI; after installation, review the workbench with the user.

## Merged: bounded history request timeouts

The next reliability increment maps both the explicit 90-second history budget and
lower-level WebSocket receive/connect timeouts to the existing typed Home Assistant
history error. A stalled Recorder request therefore fails in a controlled way instead
of escaping as a generic HTTP 500. Cancellation remains untouched, and successful
history/statistics responses, storage schema 6, roles, consent and learning do not
change.

One synthetic regression covers the timeout boundary. PR #21 merged the increment as
main commit `e77b80c573a1429173aaaa0f5d50a92b9102fc6a`. Final main CI 35822148371
passed 117 backend tests, four JavaScript tests, Chromium browser regression and the
amd64 container. Home Assistant remains unchanged on installed alpha.13.

Next: the separate live acceptance item remains a short read-only history request and
graph check in an authenticated local HA Ingress session. Do not enable learning or
import history for that test. Package the merged correction in a later release
candidate only after an exact-version CI gate and fresh scoped backup.

## Merged: bounded statistics metadata validation

The next reliability increment validates Home Assistant Recorder metadata before
building the transient statistics projection. A non-list response or an entry
without a non-empty string `statistic_id` now becomes the existing typed HA history
error instead of leaking `TypeError` or `KeyError` through a generic HTTP 500.
Metadata outside the explicitly requested source set is ignored. Successful
statistics, raw history, SQLite schema 6, roles, consent and learning are unchanged.

Synthetic regression covers five malformed response shapes. PR #19 merged the
increment as main commit `af41ee3883bf0b05975933b8d15884cd4df6e274`.
Final main CI 35818141260 passed 116 backend tests, four JavaScript tests, Chromium
browser regression and the amd64 container. Home Assistant remains unchanged on
alpha.13, started and hard read-only.

The next task remains a short read-only history request through an authenticated
local HA Ingress session to verify Recorder coverage and graph rendering. No
learning or historical import is required for that acceptance.

## Released and running: 0.1.0-alpha.13

PR #16 merged the reliability increment as main commit
`734a1e5c272433d37405470918ea93b983e1fdf9`. It converts `aiohttp`
connection failures during a history/statistics WebSocket request into the existing
bounded history error instead of leaking a generic HTTP 500. Malformed text frames
now become the same typed Home Assistant protocol error used for other invalid
frames. This changes no successful response, storage schema, consent, roles or
actuation boundary.

Synthetic regression covers both failure paths. PR #17 released the fix as main
commit `d7068e5b08827a9ddf61df60cf2271b6a1b7aa88`. Candidate CI 35814179314 and
final main CI 35814266844 each passed 115 backend tests, four JavaScript tests,
Chromium browser regression and the amd64 container.

Before publication, scoped PilotSuite App-and-data backup `9bf5a8a1` completed at
2026-09-23T03:27:24Z. The completed listing reports 53,841,920 bytes and excludes
Home Assistant configuration and database. Recovery is a targeted partial restore
of PilotSuite and its data from this backup to alpha.12; archive contents were not
independently inspected and no restore drill was performed.

Supervisor Store metadata links offered `0.1.0-alpha.13` to the exact main commit
above. The update completed, and metadata confirms alpha.13 installed, offered and
started. Startup at 2026-09-23T05:28:40Z reports `hard_read_only`; at 05:28:41Z it
reports `ready=True`, connected event stream, fresh snapshot and resolved Golden
Zone. No error or history request appeared after startup. No role, learning consent,
history import, automation or actuator state was changed.

Authenticated Ingress loading of a short read-only history interval remains the
next live acceptance item. The available remote browser had no authenticated HA
session and could not access the private HA address, so root/assets/APIs, Recorder
coverage and graph rendering are not claimed. Do not enable learning or import
history merely for this acceptance.

## Released and running: 0.1.0-alpha.12

PR #13 is merged as `13e1b03791d93d2bedb3e022b08743a1d61649b9`.
PR #14 released it on main as `52bc972b834aa533575db3e874970f5312c2d513`.
Final main CI 35805983743 passed 113 backend tests, four JavaScript tests,
extended Chromium browser flows and the amd64 container. The release combines
consent-gated coarse event-origin hints with targeted Home Assistant
history/statistics views and separately consented retrospective activity imports.
It remains hard read-only; no learning consent or import is enabled by the update.
SQLite schema 6 backs up schema 5 before migration.

Before publication, scoped App-and-data backup `f803e957` completed at
2026-09-23T01:21:28Z. Its listing reports 53,811,200 bytes and excludes Home
Assistant configuration and database. Recovery is a partial restore of PilotSuite
and its data from that backup; archive contents were not inspected and no restore
drill was performed.

Supervisor Store refresh identified alpha.12 and the update completed. Metadata
confirms alpha.12 installed, offered and started. Startup at 2026-09-23T03:25:47Z
reports `hard_read_only`; at 03:25:48Z it reports `ready=True`, connected event
stream, fresh snapshot and resolved Golden Zone. The protected direct proxy
correctly returns HTTP 403 `Ingress access required`; it was not weakened for
testing. No authenticated HA browser tab was available, so real Ingress root,
asset, API and chart interaction remain unverified for this release. Actual role
choices and Recorder coverage also remain separate live acceptance items. No role,
learning-consent, history-import, automation or actuator state was changed.

Next: in an authenticated HA Ingress session, verify root/JS/CSS/API loading and
load a short read-only history interval to confirm Recorder coverage and graph
rendering. Do not enable learning or import history merely for acceptance.

## Merged implementation: targeted history and zone trends

Branch feat/history-and-trends incorporates main 155fb07 including consent-gated
event attribution. Implements
scoped raw/statistics reads, source/reference graphs, presence/light timelines,
weekly activity raster and chronological reobservation checks. One-time explicit
consent imports only presence activations into the existing bounded activity-v1
store, deduplicated against live/imported evidence. Schema 6 migration backs up
schema 5 and preserves settings. Contract: docs/HISTORY_AND_TRENDS.md / ADR-024.
CI 35802932782 for candidate 31f04a68577a5afbfa9df4d9dfa150659900953c passed
113 backend tests, four JS tests, extended Chromium browser flows and amd64
container. Local repository validation also passed. Implementation is in PR #13.
The following documentation-only commit records that verified candidate.
HA read-only metadata confirms alpha.11 started. No role/consent change or live
historical import was performed. Actual Recorder coverage and Ingress acceptance
remain open.


## Merged, not released: consent-gated coarse event attribution

PR #11 merged as `203fb512dcad1d652aa38eb37e07092855a6edb7`; its tree exactly
matches tested candidate `00773dc3c23ad9274c29608ce1f535689b3afa58`.
Main CI [35802574356](https://github.com/GreenhillEfka/pilotsuite/actions/runs/35802574356)
passed 93 backend tests, four JS tests, Chromium browser regression and amd64
container. Based on installed `0.1.0-alpha.11`, the event stream now
subscribes separately to `state_changed` and `call_service`. When at least one zone
has active learning consent and an eligible source, a bounded in-memory correlator
keeps opaque HA context links for at most 120 seconds / 2,048 entries. Disconnect,
loss of all eligible learning sources or process restart clears them. No service
payload, user ID or context ID is written to SQLite, exports, logs or the UI.

Persisted activity evidence can distinguish direct user context, correlated
parented service context, correlated unparented service context, uncorrelated
derived context and unknown. These are hints, not proof of manual operation or a
specific automation/script. The candidate UI makes that limitation explicit.
PilotSuite remains read-only and therefore produces no own-action evidence.

Synthetic regression covers dual subscriptions, interleaved dispatch, consent
gating, expiry/limit/disconnect clearing, identifier non-disclosure and independent
origin persistence. This increment is merged but not versioned, released or
installed. HA remains unchanged on alpha.11; no production consent was changed.

Next: prepare a separately versioned release candidate without enabling learning,
then require final exact-commit CI, a fresh App-and-data backup and an explicit
recovery target to alpha.11 before deployment. Live attribution acceptance requires
already-consented real learning; do not enable it merely for a test.

## Released and running: 0.1.0-alpha.11

PR #9 merged as a1bb95f7a6c045ece234ad70e8e9ee3c855129d0. The merge tree
c2a47079e11c89885fd418cec21afdb1505d651c exactly matches candidate 258a116.
Final CI 35800786084 passed 85 backend tests, four JS tests, extended mobile
browser flows and amd64 container including IANA timezone availability.

Fresh App-only backup 1b74df9a was created before publication because auto-updates
are enabled, and confirmed in the completed listing: 53,739,520 bytes, unprotected,
HA configuration/database excluded. Requested scope was PilotSuite and its data;
archive contents were not inspected and no restore drill was performed. Recovery
is a partial App-and-data restore of this backup, not schema-4 code over schema 5.

Supervisor update completed; metadata confirms alpha.11 started with unchanged
options. Startup at log timestamp 2026-09-23T02:10:59Z reports hard_read_only;
02:11:00Z reports ready=True, stream=True, snapshot_fresh=True, zone_resolved=True.
Startup necessarily completed database initialization; migration copies were not
independently inspected on the host. Migration preservation is covered by tests.
Real iPhone Ingress requests after startup (02:11:10–16Z) returned HTTP 200 for
context, selections, zones and status; root/assets also returned 200. This is not
proof of interactive acceptance of every control or the user's exact live roles.

This release includes configured activity thresholds, local time/day groups,
source/progress/module views, sampled observability and separately consented
light/lux context. No production role, timezone or consent was changed by this
release operation; new context consent defaults off. HA actuation stays blocked.
Next: actual zone UI acceptance, explicit learning choices and real multi-day
observations. Physical sensor coverage is not guaranteed; presence/light were
partial at startup. Temporal switching sequences and HA draft execution remain
future work. Contracts: docs/RHYTHMS_AND_CONTEXT.md and LEARNING_AND_ACTIONS.md.

## Historical development notes

## Next package: local rhythms and activation context (development)

PR #9 now includes persisted IANA timezone and weekday/weekend grouping, DST-safe
local-day counts, bounded sampled observability and separately consented light/lux
context at accepted activity events. Explicit source groups only; unknown values
stay unknown. Context cards make read-only review suggestions, not HA commands.
Schema 5 backs up before adding two tables; existing context consent defaults off.
85 backend tests and repository validation pass locally. Browser test now covers
new settings and context/coverage rendering; expanded CI remains a required gate.
The previous df5a77b head passed all CI 35799028200 before this package.
Verified at package start: PR #9 open, main d48e719, HA alpha.9 started. No production
consent, role edit, update or HA automation was performed by this increment.
Contract and recovery: docs/RHYTHMS_AND_CONTEXT.md / ADR-022. Release requires an
App-and-data backup because schema-4 code cannot open schema 5. Remaining: actual
HA Ingress acceptance and real multi-day data; temporal light sequences, shadow
execution and native HA drafts are explicitly deferred.


## Development: zone overview and evidence progress

PR #9 now also provides per-zone activity-v1 minimum events (5–100) and days
(3–14), revision-safe persistence, bounded validation, parameter-specific pattern
identity and a module status overview. Evidence is retained on parameter edits;
consent does not change. docs/LEARNING_AND_ACTIONS.md separates implemented learning
from planned script/automation drafts and governed execution. 70 backend tests,
four JS tests and validation pass locally. The previous PR head d76b40a passed CI
35798093744 (backend/browser/container); the expanded head needs its own CI gate.
Main advanced to alpha.10 via PR #10 during this work. Its structured assessment
contract is merged and rule-strength ratios use the configured per-zone thresholds.
No installation or new learning/actuation consent performed in this increment.


Extends alpha.9 with expandable source details in reference cards; persisted
presence-group names; collection-state explanations; consent and first/last retained
evidence timestamps; per-UTC-window counts and missing candidate requirements.
No statistical confidence percentage or uninterrupted coverage is implied.
No schema migration, role rewrite, consent change or HA update in this increment.
Previous increment: 66 backend tests and four JS tests passed locally; repository validation passed.
Browser regression extended, but local Chromium is unavailable: CI must verify it.
Live read-only check confirms alpha.9 started, ready and real Ingress API HTTP 200.
The user's exact live selection remains uninspected through the protected APIs.
Next: CI browser/container gate, then release preparation and scoped backup before
any production update. Real multi-day habits and live interactive acceptance remain open.


## Release candidate: 0.1.0-alpha.10 structured activity evidence

The next bounded change gives `activity-v1` candidates independent observation
statistics, deterministic threshold ratios, nullable statistical confidence,
read-only risk and durable user preference fields. Deprecated flat alpha fields
remain compatibility aliases; feedback still changes no evidence. Synthetic tests
cover the contract and persistence. PR #10 candidate CI 35798185711 passed 64
backend tests, four JS tests, browser regression and amd64 container before the
release metadata commit. App-only backup 522eda91 was then created from running
alpha.9; the completed listing excludes HA configuration/database. The partial
restore target is PilotSuite and its data only; archive internals and a restore
drill were not performed. alpha.9 remains installed until the final release-metadata
CI passes. Production learning consent remains unchanged.

## Released and running: 0.1.0-alpha.9

PR #8 merged as 04db3fb103850dd1c6f495d035f646d488a27b3d. Its tree
cbe0f8e1140a0f0d57b444041f8213ce7a8ba529 exactly matches candidate b1553a2.
Final CI 35797007069 passed 63 backend tests, four JS tests, extended mobile
browser regression and amd64 container. A mismatched Docker version marker was
caught by the release test and fixed before this final CI and deployment.

ADR-018 and docs/SENSOR_REFERENCES.md define the revised contract: automatic
virtual references for temperature, humidity, illuminance, presence and light;
persisted empty groups; consistent presence display/learning sources; visible
legacy defaults and explicit external comparison-temperature labeling.

App-only backup 19bfccc7 was created and confirmed before merge (automatic app
updates were already enabled). Listing reports unprotected, HA/database excluded.
Only PilotSuite and its data were requested; archive contents were not inspected.
Recovery is an App-and-data partial restore of that backup, not a full HA restore;
no restore drill was performed. No database migration or role rewrite was added.

Supervisor confirms alpha.9 started with unchanged options. Runtime logs at
2026-09-23T01:23:08Z report hard_read_only, ready=True, stream=True,
snapshot_fresh=True, zone_resolved=True. Existing source availability remains
partial for presence/light; readiness is not a physical sensor completeness claim.
Actual user selection and UI behavior in the live Ingress session remain to be
accepted. Do not infer that the user's exact presence-saving issue was reproduced:
code inspection found an inconsistent fallback and explicit-empty-group loss;
API persistence and browser reopen tests cover the corrections. Learning consent
was not changed by this deployment. New sensor classes require typed semantics;
no generic energy/alarm aggregation and no native HA reference entities yet.

## Historical alpha.8 deployment

Last updated: 2026-09-23 (runtime log UTC)

## Released and running: 0.1.0-alpha.8

PR #7 merged as 3aec18fce0b9d1e36abed1f81b38a034d36dcdcb with the exact
CI-tested tree f7ec8d4395f52b7b501424591dc4936031a183b8. CI 35793755621
passed 59 backend tests, four JavaScript tests, browser workflow tests and the
amd64 container build. A new subprocess regression executes the real module
entrypoint and checks HTTP health and database creation.

PilotSuite-only alpha.6 backup 89e963d5 was created and confirmed before updating;
HA configuration/database and unrelated Apps were excluded. alpha.7 initially
failed before startup callbacks/schema migration because main ran before newly
added route handlers were defined. alpha.8 moves the entrypoint after all handlers.
After installing alpha.8, an explicit start recovered the previously failed App.
Supervisor reports version 0.1.0-alpha.8 and state started. Runtime logs at
2026-09-23T00:45:49Z confirm hard_read_only, ready=True, stream=True,
snapshot_fresh=True and zone_resolved=True. Temperature/humidity/motion/illuminance
are available; presence/light are partial. Readiness does not mean every source
is complete or physically fresh.

## Implemented

Contract: docs/OBSERVATION_LEARNING.md and ADR-017. Only explicitly relevant
entities feed zone evaluation; unreviewed and ignored entities are excluded.
Zone tabs, mutable names, multiple HA-area sources, extra entity candidates and
direct start/pause remain available. The user confirmed Badbereich activation in
alpha.6; do not recreate it or infer that its new role groups were reviewed.

Compact zone cards summarize temperature, humidity, presence and light; entity
selection and raw neurons are expandable. Plural sensor roles support climate
median with source range/quality, separate reference temperatures and presence
from any active group member. A multi-room median is a zone summary, not an
individual room temperature. Missing or conflicting data remains visible.

Learning defaults off per zone. Explicit consent allows bounded live presence
activity evidence (14-day retention, 5,000 global records, five-minute zone-wide
cooldown). Candidates require at least five activations on three distinct UTC
dates in a two-hour UTC window. They carry unknown confidence, not causal or
person-specific claims. Feedback is independently persisted; export/reset and
consent revocation are implemented. No production consent was enabled and no
synthetic evidence was seeded during deployment. Climate suggestions remain
deterministic heuristics, separate from these activity candidates.

SQLite schema 4 stores zone definitions/selections, role groups, consent, evidence
and feedback, with migration backups and shared revision conflict checks. The
actual archive file was not inspected on the HA host. The successful startup
completed initialization; migration/backup details are covered by tests.

The reconnect correction from PR #4 (CI 35792464489, merge aac362a) remains:
short streams retain bounded 1/2/4/8/16/30-second backoff, reset only after a
60-second stable subscribed stream. Authentication failures do not report connected.
Ingress peer restrictions and hard-disabled HA actuation remain in force.

## Acceptance limits and next work

Startup/transport readiness is live-verified for alpha.8. Role selection, consent,
revision conflicts, feedback and reset passed browser/API tests, but these are not
proof of interactive acceptance in the user's actual HA Ingress session. The MCP
proxy cannot inspect protected APIs through the peer guard; do not bypass it.
No real multi-day learned routine is claimed. Live disconnect/load soak is pending.

Next: review relevant sources and plural roles in the actual zone UI; optionally
grant learning consent, then evaluate real evidence and durable feedback. Validate
a second unlike zone before 1.0. No autonomous HA action engine, native adapter,
voice integration, LLM dependency or causal habit model is implemented.

For downgrade recovery restore the scoped App-and-data backup 89e963d5; never
feed schema 4 to older code. No restore drill was performed. Historical alpha.5
and alpha.6 release evidence remains in git history and merged PRs #1/#3/#5.
The canonical repository remains GreenhillEfka/pilotsuite.
