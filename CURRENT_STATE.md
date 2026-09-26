# Current state — Alpha.35 inventory overview candidate, Alpha.34 installed

## Active coherent package: cumulative inventory integrity

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
and absence of saves/control. RELEASE_STATE remains the actual Alpha.34 receipt.

Next: exact candidate CI, scoped backup and normal release gates; then authenticated
read-only acceptance beginning with the saved Erdkellerbereich zone.

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
