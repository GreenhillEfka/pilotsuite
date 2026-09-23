# PilotSuite current state

## Store release candidate — 2026-09-24

Canonical repository `GreenhillEfka/pilotsuite`; app `0d79c5e8_pilotsuite`.
Resume **PR #50**, branch `feat/revision-bound-review-notes`.
**The existing review-note package is now versioned as 0.1.0-alpha.22 on that
branch. It is not published, merged or installed.** Do not restart its implementation
or assign another version merely because the installation has not happened.

The user explicitly requested the normal Store route. Release preparation changes
VERSION, app config version, Python package VERSION, Docker BUILD_VERSION, DOCS
release marker and both changelogs. App identity, options, permissions, runtime
code and read-only policy are unchanged from the tested feature candidate.
DOCS adds the user workflow for notes. Historical changelog entries remain intact.

CI now runs the existing read-only release_preflight.py against the exact candidate
SHA and the last published commit in docs/RELEASE_STATE.json whenever their versions
differ. The test job fetches full Git history for ancestry verification. Equal
versions explicitly skip only this new-release check; they do not authorize delivery.
No HA credentials, install calls, writes to main or permission escalation in CI.

## Evidence and remaining gates

The prior feature HEAD `47ae62ead032c48ecc8c2c56cb2eae124f0a0a54` passed CI
`35923067713`: 215 Python, 16 JavaScript, full-shell browser, note-editor browser
and amd64 container. Read the **new exact PR HEAD CI and source-preflight receipt
in PR #50** for this versioned candidate. An earlier green run is not its final gate.
No new local full-suite or container success is claimed; direct local Git download
was unavailable, so source reads and test execution use the authorized GitHub tools.

Current tool discovery offers no HA-MCP namespace or native ha_manage_app Store
action. Plugin search returned no matching usable Home Assistant connector.
This is not a fresh HA authentication failure. No new backup, Store refresh,
installation, restart or live household read/change occurred. Never repeat the
previously denied custom bridge or change permissions to compensate.

Before publishing, verify a fresh completed PilotSuite-only app/data/options backup
of the currently installed version. The last observed auto_update setting was true;
publication could make the candidate eligible for automatic installation. Do not
publish merely to try to get around the missing live verification. Do not disable
auto_update. Versioning on the existing unmerged branch is not Store publication.

## Last verified deployment — historical, not rechecked today

Alpha.21 was installed/started on 2026-09-23. Release commit
`1223f96f45053f7bf3d509bd7ad72c85b9f6cab1`, app tree
`3228fa2b5cae4d0db00dc7646aa6e39bb43b6b77`. Installation handoff PR #49 merged at
`c3e87fb81a24267b8584f2d68df25bd8f9539aba`; main still matched it before preparing
this candidate. Prior backup `ae7a3fba` contains alpha.18, not a fresh alpha.21
recovery point. Keep docs/RELEASE_STATE.json as the last actual deployment receipt.

## Next concrete step

Obtain fresh installed-version and completed scoped-backup evidence, then recheck
this candidate's exact source/CI, current main/open work and version uniqueness.
Only after those gates merge PR #50 without force and verify exact main CI.
Use the documented native Store refresh only when alpha.22 is not offered, reread
metadata and perform one normal update if not already installed. Verify runtime;
no speculative restart. Follow docs/RELEASE_RUNBOOK.md without reinventing the route.
If no authorized live access exists, report the exact pending step rather than
claiming either Store publication or installation.

Authenticated real Ingress UI and the app's existing automation/config read
capability remain separate pending acceptance. No new consent or household scan
for tests. After acceptance, the next concept is a compact derived review summary
with explicit missing requirements, not another store or execution gate.

## Contracts and retained history

ADR-030 and docs/REVIEW_NOTES.md define the already implemented notes. PlanStore is
the single owner, schema 8 backs up before adding its table, review revisions guard
competing writes/deletion, and all action application remains denied.
The complete previous candidate handoff is preserved in commit `47ae62e`.
Older ledgers remain unchanged in CURRENT_STATE_HISTORY_2026-09-23.md and
 docs/IMPLEMENTATION_HISTORY_2026-09-23.md. Older unversioned-candidate wording is
superseded by the alpha.22 preparation above, not by a claimed live deployment.
