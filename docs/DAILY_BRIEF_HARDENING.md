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

This reconciliation passed 308 Python and 48 JavaScript cases locally with
Python 3.13.5 / aiohttp 3.13.3 / Node 22.16.0, not pinned CI Python 3.14 / aiohttp
3.13.5 / Playwright 1.62.1. Existing SQLite ResourceWarnings are not a warning-free
claim. Playwright is absent in this local environment, so no fresh local browser
run is claimed. Earlier isolated browser receipts are historical; local HTTP browser
navigation had been administrator-blocked and was not bypassed. Exact new-head CI
is required; earlier b994fc8 CI cannot certify these additions.

## Delivery

Fresh completed PilotSuite-only backup before publication because auto_update=true;
expected-head merge, exact main CI and existing native Store update routine follow.
No HA option, consent, actuation, scheduler, other app or host change belongs here.
Authenticated live Ingress, app configuration-read capability, data/image attestation
and demonstrated household usefulness stay separate from synthetic CI evidence.
The preceding detailed integration record remains in Git at b994fc8b610df9a67669520795c0691950ef46ba.
