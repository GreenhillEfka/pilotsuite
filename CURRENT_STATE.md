# Current state — Alpha.33 delivered, 2026-09-26

## User package: recoverable inventory editing

PR 71 release commit 46ec340adf333f54efa760cde2d80f059b9c0ca2 adds matching
zone/revision/generation checks to all organization-plan responses. Late replies
cannot revive invalidated confirmation controls. Older-revision previews remain
readable without Apply. Lost save acknowledgements and failed post-save reloads
retain the visible selection and prevent write replay. Explicit recovery reads the
canonical configuration; open role groups and search terms remain visible.
Existing ContextStore/PlanStore, backend authority and household behavior are unchanged.

## Evidence

Candidate 1a81070963706428baac29c7a0ad32b5164f439b: CI 36260320758 green.
Exact release-main CI 36260420284 and 36260423409 green. All four jobs, nine browser
suites; organization suite now has 11 checks including 6 new regression scenarios.
454 Python and 56 JavaScript tests passed. Source preflight passed; repository tree
295fed803c3b0caeb4c3747759a97c39de4e33ab, app tree c059bc65fe76af09c560ca819b7051f81feecece.
Initial CI 36260055322 found a nonboolean dirty-state result, fixed; CI 36260188746
exposed collapsed role groups after recovery, fixed. Neither failed run was released.

## Actual installation

Before publication, backup 1ea31dc2 completed: only PilotSuite Alpha.32 and app data/
options, 54,323,200 bytes, local/unprotected, no failed parts, HA, database or folders.
Native snapshot list and backup/details verified. Recovery is a targeted partial
restore of that app only; it would discard PilotSuite changes since the backup.
No archive download or restore drill. Exact receipt: docs/RELEASE_STATE.json.

One native Store refresh and one update installed Alpha.33. Installed/offered/started,
no pending update. All four options and auto_update=true match before/after. Startup
and post-start readiness logs confirm connected stream, fresh snapshot and resolved
zone. Existing mode presence_adoption_review unchanged; hard_read_only is not claimed.
The general Apply gate remains READ_ONLY_RELEASE=True in the exact tested source;
existing denial tests pass. No real Apply request was made.
No explicit restart/rebuild, other-app update, names, automations, actors or learning
settings changed. A fresh transport projection does not certify physical sensor age.

## Remaining acceptance and next step

Synthetic CI is not authenticated household UX. The available browser had only an
empty tab, no logged-in HA session. App-principal configuration/registry rights,
independent installed-image attestation and comprehensive data preservation remain
separate, unverified checks. Options equality and successful startup are narrower
observations. No Ingress weakening or speculative alternate access was attempted.

Next: authenticated read-only acceptance of inventory editing/recovery and existing
routine explanation in the already authorized Erdkellerbereich use case. No extra imports,
learning consent or execution. Do not repeat Alpha.33 installation.

## Follow-up read-only acceptance — 2026-09-26

The user corrected the real case label to **Erdkellerbereich**. Preserve technical
identity; no HA area, entity, stored zone, option or automation was renamed.
Native HA reads confirm existing presence/timing/light logic, so an additional
PilotSuite helper set is not justified merely by the new display name. Household
configurations and readings remain outside this public repository.

A useful next inspection question is whether shutdown conditions respect still-active
presence. Treat an explicitly authored shutdown rule as behavior to review, not an
automatically repairable defect. This is a manual read-only assessment via HA-MCP,
not a completed app-generated proposal or browser acceptance. The app's canonical
zone endpoint continues to enforce Ingress (HTTP403); no alternate access attempted.
Installed/offered Alpha.33 remains started and ready. No update/restart/backup was
needed for this clarification. The next step above remains authenticated read-only
acceptance, with the corrected case label and this concrete inspection question.
