# Current state — Alpha.73 installed

## Delivered structural foundation, 30.09.2026

PilotSuite now exposes only the Habitus zone overview, structure editor and zone
documentation. Old routes/preferences return to this flow. Deferred comparison,
presence/light setup, helpers, learning and automation views are hidden, with their
background UI queries removed. Existing stores, runtime and analysis choices are
preserved; hiding UI does not disable existing backend behavior.

PR #155 release main: `a620dafbeb472868d56d3cf5475dc3ec45b72ed1`.
Exact candidate/main CI: 36698531500 / 36703236135, all five jobs successful.
App tree: `7cda002218b58062265520abb6dfe18ad1c04661`; source preflight passed.
729 Python tests, 77 JS tests, 68 API contracts, five current Chromium suites,
seven native scenarios against disposable HA 2026.9.3 and amd64 build passed.
Actual fixture screenshots were inspected at 390/820/1440 in light/dark. The current
browser contract replaces seven historical full-product navigation suites; backend,
model and selected isolated-component coverage remains. Full scope and regressions:
[HABITUS_FOUNDATION_RESET.md](docs/HABITUS_FOUNDATION_RESET.md).

Fresh backup `b510f891`, 30 September 10:33:30 UTC: only installed Alpha.72 app/data,
54,558,720 bytes local, unprotected, no HA/database/folders or failed components.
Two additional Synology agents report only “Failed to list backups”. The user
answered “ja immer” to this concrete exception: it is now a standing narrow
permission, documented in the runbook and quality skill. Verify all local conditions
on every release; do not ask repeatedly. NAS settings are unchanged; no archive
extraction, restore drill or off-device resilience is claimed.

One Store refresh and one targeted update installed Alpha.73. At 10:36:55 UTC,
native metadata reports started; all four option values match the baseline.
Startup and readiness logs confirm presence_adoption_review unchanged, connected
stream, fresh snapshot and resolved zone. General Apply stays closed in source;
existing bounded metadata/helper paths retain their prior scope. No extra restart,
rebuild, other-app update, household import/apply, label edit or control action.
Source evidence is repository/version/app-tree association, not image attestation.
Already-open clients must reload to obtain the reduced frontend; old Safari-client
requests were still visible after update, so household UI acceptance is not claimed.

## Current target and remaining access

The user explicitly commissions **real structural zone adoption**: synchronize
actual HA/PilotSuite members and manual Habitus roles through concrete existing
metadata plans, then independently verify fresh registries. Newly imported members
receive no new analysis or control authority. Presence, helpers, active light,
climate, multimedia and learning remain later work.

The available HA browser still shows the login form (fresh DOM check after update).
The earlier direct app proxy returned 403 Ingress required; that route remains
stopped. User login/opening PilotSuite was requested and is still pending. This is
the remaining access prerequisite; the backup exception is no longer a blocker.

Read-only HA inspection confirms the existing Erdkellerbereich dashboard and its
configuration/diagnostic/documentation views. Its shared template inherits zone
and role tags from devices; no current role tag is device-assigned. Alpha.73's
import/readback and conflict guards cover that inheritance, with red/green tests.
This does not establish actual saved PilotSuite bindings or household acceptance.
Private input stays in ignored pilot_data/reviews; release proof is in
[RELEASE_STATE.json](docs/RELEASE_STATE.json).

Next: once authenticated, inspect all four saved zones and compare Erdkellerbereich
and one unlike zone against HA areas/tags, stable members and roles. Reconcile only
confirmed structural differences through the existing preview/apply/readback path;
retain foreign labels, physical locations and saved runtime decisions. Record real
readback before claiming synchronization. No guessed binding or auth workaround.

The overnight heartbeat remains PAUSED; no new agents, tasks or timed run.
Historical Alpha.72 delivery is preserved in Git and the implementation ledger.
