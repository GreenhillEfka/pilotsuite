# PilotSuite current state

## 2026-09-25 — Alpha.23 installed; Alpha.24 candidate in PR #54

Canonical repository and existing branch only. GitHub and HA-MCP read access work
in the same session again; a native GitHub write has also succeeded. This is not
a reason to reconnect apps, replace credentials or start another repository.

Fresh native app metadata: Alpha.23 installed/offered, started, no update pending,
auto_update=true unchanged. Fresh PilotSuite log window: ready, stream connected,
snapshot fresh and Golden Zone resolved; presence/light capabilities still partial.
No HA writes, new backup, Store refresh, update, restart or learning changes in this
integration. The original Alpha.23 delivery receipt remains in PR #54's initial
body and WORK_PACKAGE_DAILY_BRIEF.md. Real Ingress acceptance remains separate.

## Actual development

Cumulative R2 hardening is applied to the full Git checkout at
6b1e9cbb4b02c4da86ae751e9772b95b07c1b9bd. The source-checkout artifact 10823645624
from CI 36031998852 matched SHA256
cb1e88a8c12d3c10c9f3dba3445b57dd559a71eb7e9798509bbfc87e1cf1bd50.
Originals were backed up before local changes. No parallel evidence store or API.

The old CI failed on a synthetic inventory missing zone_id; reproduced and fixed
without weakening strict projection checks. The old five free daily-brief test
functions were not collected by unittest. R2 uses 41 actual unittest cases.
New real-store API tests cover GET/HEAD/export non-mutation, retained statistics,
source disconnect/unavailability, pause/revocation, preference and zone isolation.

The actual-app browser CI flow covers navigation, equal-response focus, unsaved
drafts, same-zone reload races, errors, preferences and responsive layout. Local
full-app navigation was blocked by the browser administrator policy; no bypass.
35 isolated component checks against the exact integrated functions passed; they
are not a full-app or live-household result. See docs/DAILY_BRIEF_HARDENING.md.

Alpha.24 VERSION/config/package/Dockerfile/DOCS markers and both changelogs match.
CI source comparison now uses the last published Alpha.23, not the older complete
Alpha.22 installation receipt; same-version changed app trees are rejected.

## Next action, without restarting discovery

Finish exact PR #54 CI, fixing concrete failures in this branch. Before publishing:
fresh native PilotSuite-only backup, completion/details verification, expected-head
merge and exact main CI under RELEASE_RUNBOOK.md. Then one matching native Store
update if Alpha.24 is not already installed. No speculative rebuild/restart.

Authenticated live UI, app automation/config read capability, independently checked
data/image and demonstrated real comfort benefit remain separate acceptance items.
No actuation, HA configuration, consent, credentials or scheduler changes.

Previous complete receipts remain in Git and RELEASE_STATE.json. Historical fields
are not fresh observations; current_observation is newer. Do not repeat Alpha.23.
