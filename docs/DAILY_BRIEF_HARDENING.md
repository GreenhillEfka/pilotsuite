# Daily brief — integrated hardening and reconciliation

2026-09-25; existing PR #54 / feat/zone-daily-brief. Canonical repository only.

## Retained implementation

R2 is integrated in the complete repository, not a replacement mock. The pure
bounded brief derives from existing inventory, ContextStore and review_brief.
Zone/revision/source checks, explicit learning/readiness, coverage, chronological
evidence partitions and preference precede candidate selection. Duplicate identities
and contradictory counts fail closed. Rejections/deferrals never change observations
or become promoted candidates. A split across one local calendar day remains valid.
Missing later evidence does not establish inactivity. No new store, collector or API.

The UI uses bounded text and Unicode code-point limits. It invalidates candidates on
same-zone reload, zone change, failed reads and unsaved selection. Only presentation
state can survive an in-flight reload: an equal verified response restores expansion
and focus unless the user moved focus elsewhere. New activation handlers bind to the
latest context. No stale navigation, automatic save, discarded input or actuation.
The link opens the existing workbench; this is no daily forecast or causal claim.

## Reconcile source evidence

Remote b994fc8b610df9a67669520795c0691950ef46ba already contained R2 and passed
CI 36110294548. Source artifact 10852638016 matched SHA256
f24c608c0e16b0d2de48c5bd198674c69de177618799eb40722bbc33b91b88a9.
The saved b9a520ce047610d611efea25be872f766b655375 candidate supplied the missing
focus/discovery/API/browser additions. Its older workflow is NOT copied over the
remote's stricter published-source check. Original local files were backed up first.

The existing published_source and --allow-unchanged gate still rejects changed app
trees reusing a published version. Only identical app trees permit documentation-only
same-version CI; that confers no deployment authority. Strict release_preflight still
requires a newer version. Four existing source-gate regressions stay unchanged.
All five release markers and both changelogs remain 0.1.0-alpha.24.

## Tests and limits

The earlier missing synthetic zone_id is corrected without weakening validation.
The five original free functions were not discovered by unittest; replacement R2
contains 41 collected projector cases. The new discovery guard rejects module-level
test functions, empty test modules and failed imports, with six regressions. It does
not execute test bodies; the regular unittest step still does so afterwards.

Ten actual HTTP/store cases use aiohttp and real World/Zone/Selection/Context/Plan
owners with synthetic data. GET/HEAD/export preserve every SQLite table digest and
do not read HA automations/configuration or collect extra evidence. Coverage loss,
preference, source unavailability, disconnect/recovery, pause/revocation, foreign
zones and denied Apply remain explicit. The fixture closes its direct DB reads.

The common canonical-owner fixture feeds ten isolated component checks and the
full-app browser flow in CI. They cover focus, keyboard navigation, equal-response
restoration, competing loads, errors, unsaved selection, preferences, connection,
zone isolation and responsive layout. Fixture controls use stdin, never an HTTP
backdoor. Production ingress peers/ports/credentials are unchanged.

This reconciliation passed 308 Python and 48 JavaScript cases locally. Ten actual-
owner component cases also passed with the already installed Playwright driver and
Chromium 144; a newer local npm install did not complete and was not substituted
for CI. Local Python/aiohttp differ from pinned CI versions. Existing SQLite
ResourceWarnings are not a warning-free claim. The previously blocked local HTTP
browser route was not bypassed.

Exact final candidate d875b5437ef0daf0bad912fbb13db2de062e3ed0 passed all jobs in
36117146697. Release 6f22100dcfbee87bdedc8288b1821971bad17d53 has the identical root
and app trees and passed exact main CI 36117395171, including all five browser
steps and amd64. CI diagnosis proved the 390px overflow came only from the synthetic
H1 heading (scroll width 411px); its wrapping/font size was corrected. No mobile
assertion, production style or access check was relaxed. Actual-app synthetic
screenshots at 390/1440 were downloaded, SHA256-verified and visually reviewed.

## Delivery completed, live UI acceptance separate

Fresh PilotSuite-only Alpha.23 backup ad3c24bb completed before publication;
native details verified no HA/database/folders/failures/key requirement. One native
Store refresh and one normal update installed Alpha.24. Startup and readiness logs
confirm hard_read_only, ready, stream, fresh snapshot and resolved Golden Zone;
metadata confirms unchanged options and no remaining update. No extra restart or
changes to another app, HA configuration, roles, consent, permissions or scheduler.

RELEASE_STATE.json records source/CI, backup and runtime separately from pending
authenticated live Ingress, config-read capability, independent data/image checks
and demonstrated household usefulness. No archived backup was downloaded/restored.
Earlier detailed integration evidence remains in Git at b994fc8b610df9a67669520795c0691950ef46ba.
