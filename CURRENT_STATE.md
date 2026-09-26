# Current state — Alpha.35 delivered; API contract integrity added, 2026-09-26

## Repository package: complete API inventory

The former API page documented only a historic subset of the live application and
named the legacy transaction parameter `{id}` although the registered path uses
`{plan_id}`. The repository now lists all 48 registered `/api/v1` method/path pairs,
grouped by owner and effect. It distinguishes inspection, preview, persistence,
restore and explicitly confirmed apply operations instead of treating an HTTP method
as an authority signal.

The dependency-free repository validator reads the explicit route registrations and
requires exact, unique set equality with docs/API.md. This is one owner plus one
checked human view, not a second API schema. The package changes no endpoint, payload,
application tree, version or installed app. Its scope and exclusions are recorded in
docs/WORK_PACKAGE_API_INTEGRITY.md.

## Delivered package: cumulative inventory integrity

The existing explicit global scan reads at most eight automation configurations per
request, but previously replaced the prior package's results. The candidate now keeps
a transient zone/revision-bound view across explicit batches. It shows deterministic
progress and separate filters for entity-reference findings, trigger-ID findings,
unreadable configurations and all readable reports. Selected replacement candidates
survive another batch and presentation-only filter changes.

The view is derived only in browser memory. A reload, zone/revision change or explicit
invalidation discards it; a late response cannot cross the existing request generation
boundary. There is no second queue/store, automatic full scan, configuration save,
repair execution or HA control. Each click still reads at most eight configurations.
Synthetic browser coverage uses ten automations over two packages including one
unreadable configuration, retained draft/replacement choices, filters, mobile layout
and absence of saves/control.

PR 76 release faf36118402e817d42c4ba1919995c40c53e0cf4 passed exact candidate
CI 36267009996 and release-main CI 36267117823 (all four jobs). Fresh backup
c194bc96 contains only PilotSuite Alpha.34 app/data/options, no HA/database/folders
or failed parts. One Store refresh and one update installed Alpha.35; options and
auto_update stayed unchanged. Startup, stream, fresh snapshot, readiness and zone
resolution are confirmed; mode remains presence_adoption_review. Full evidence is in
RELEASE_STATE.json.

The native Supervisor proxy is refused with the intended `403 Ingress access required`
and that protection remains unchanged. Authenticated Alpha.35 Ingress remains open:
the available browser contains only
about:blank. Earlier Safari GETs in logs predate this update and are not reused as
acceptance. Next: read-only cumulative scan in the saved Erdkellerbereich zone, then
the other three existing zones; no inferred replacement or household write.

## Previous delivery — Alpha.34, 2026-09-26

## User package: inventory and trigger integrity

Existing entity-reference reviews missed conditions referencing nonexistent trigger
IDs. PR 74 fixes that blind spot with one shared bounded projection for inventory and
routine details. It distinguishes missing/partial/matched/disabled/inactive/unknown,
respects inherited disabled status, supports implicit integer indices and shared IDs,
and withholds certainty for unresolved catalogues. Wait triggers and data payloads
are not automation trigger declarations; private authored IDs never leave the projection.
No ID condition is required; no explicit reference does not prove an unused trigger.

Both existing workspaces share safe text rendering, exact structural locations and a
manual next inspection step. Analysis keeps unsaved selections, never saves a config,
creates a repair plan or controls HA. Existing revision/fingerprint and response
isolation boundaries remain intact. No new module owner, database or learning path.

## Source and validation

Release 20adb0e6ddf61ab899366b8a24f66f67468df569, candidate 1866e17a2655b1a591c2730403fc3a9eeb764ce5.
Repository tree 1e7a3aff09a84d3212592df7ef2e5183366e8850; app tree b456df3d8f821c3679ad62da237d6f2cc07c3c3f.
Local 468 Python and 56 JavaScript tests passed, including 14 new Python regressions.
Exact candidate CI 36263679166 and release-main CI 36263809521 are fully green:
all four jobs, nine Chromium suites, amd64 build. Organization suite has 12 scenarios.
Local browser could not start without Chromium; CI browser evidence is separate.
Source preflight passed for the exact released commit.

## Actual installation

Fresh backup 09436e7c verified through native snapshot list and backup/details before
publication: Alpha.33 app/data/options only, 54,312,960 bytes, local/unprotected,
no HA/database/folders or failed parts. Targeted app-only partial restore would lose
PilotSuite changes since that backup; no archive extraction or test restore.
One native Store refresh and one update installed Alpha.34. Installed/offered/started,
no pending update; all four options and auto_update unchanged. Startup version,
connected stream, fresh snapshot, readiness and zone resolution confirmed in logs.
Existing presence_adoption_review mode retained; hard_read_only is not claimed.
General Apply remains READ_ONLY_RELEASE=True in exact tested code, no live Apply.
No extra restart/rebuild, other-app action, household config, role, consent or actor
change. Full deployment receipt is docs/RELEASE_STATE.json.

## Live inventory review and limits

User-authorized development reads cover HA-wide entities and automations, separately
from productive app learning consent. Native configuration validation, reference and
registry reads were performed; concrete household findings stay in a private report,
not this public repository. A syntactically valid HA config does not prove referential
or behavioral integrity. Missing references are not permission to guess replacements.
Four existing user-confirmed zones include Erdkellerbereich; their saved canonical
membership is not inferred from names. No new zones or helpers were created.

The fresh browser listing contains only about:blank, no authenticated HA session.
True Ingress UI, app-principal config rights, independent installed-image attestation
and comprehensive data preservation remain unverified. Options/startup confirm less.

Next: read-only acceptance of integrity findings against the four existing saved
zones, starting with Erdkellerbereich; no inferred replacement or household writes.
