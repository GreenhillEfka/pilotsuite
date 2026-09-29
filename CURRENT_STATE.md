# Current state — Alpha.70 installed; Alpha.71 candidate

## Active work: finish PR #151

The user explicitly continued this package after the timed runs ended.
The existing heartbeat remains paused; no new timed loop or background job.
Branch `feat/zone-missing-helper`, PR #151. Alpha.70 was freshly verified
installed/offered/started on 29 September at 07:49 UTC; options retained privately.

Alpha.71 adds one missing Boolean/timer through the existing package endpoint,
PlanStore and creation/readback/recovery transaction. Existing or unresolved role
bindings, owned packages and registry collisions block replacement. Timer duration
is explicit and bounded. No automatic binding, automation connection, publication,
control transfer or interpretation of initial off/idle as vacancy.

The original three feature regressions and two new fault regressions failed first.
Additional coverage includes lost response, failed readback/restart, wrong identity,
disabled identity, expired/stale plan, exact confirmation and unlike-zone operation.
Local 651 Python / 78 JS / 62 contracts, discovery and compilation pass.
Repeated resource audit: zero warnings. Workspace, organization and extended zone
browsers pass. Unlike-zone 390/768/1440 light/dark screenshots inspected.
Synthetic tests do not establish household acceptance.

Fresh prepublication backup `e5df45f0`, 29 Sep 07:58:30.470906 UTC: native list and
backup/details confirm only Alpha.70 PilotSuite app/data/options, 54,497,280 bytes,
no HA/database/folders/failures, local unprotected agent. No extraction/restore drill.
Before release require versioned source preflight, own diff review, all five exact
candidate and main CI jobs (including extended disposable HA protocol acceptance).
Do not confuse a candidate or successful backup with installation.

## Delivered baseline

PR #148 delivered Alpha.69: zone-owned Automationen, explicit presence/light/other
topics, shared-use hints, deduplicated inspections and preserved drafts/focus.
PR #149 delivered Alpha.70: connected public HA sensor first, independent comparison,
no unknown fallback to Boolean/calculation, strict validity and separated timing.
Role-specific links reuse the helper editor; complete owned output remains five
components. ADR-043 and UX_WORKSPACE.md document the research and concept.

Alpha.70 release-main `bf1846166738d90be71757f7d6d3c14075acc04f`; source and
delivery evidence in RELEASE_STATE.json and PR #149. PR #150 closed its documentation
at main `001811bd01cc1202245b6a6ef47994d4f2ac7d64`, unchanged app tree.
Do not repeat the Alpha.70 installation.

## Boundaries and actual gaps

Preserve all four saved zones, entity cleanup and untracked AGENTS.md. No schema or
configuration migration, auth/Ingress/sandbox change or learning grant. General
Apply remains closed; bounded executors are not universal hard_read_only.
Current mode remains presence_adoption_review; existing HA automations own control.

Concrete household-write scope remains unanswered. No household helper creation,
rename, automation edit/enable/disable, output activation or control transfer.
Reuse/adoption is an authorized direction, not permanently forbidden. New individual
helper creation still requires an exact user-confirmed plan; app installation alone
creates no helper. Active HA-parameter editing and automation wiring/execution remain
unimplemented. Do not reopen the legacy provisioner.

No authenticated HA browser is connected. Real Ingress/four-zone acceptance remains
open. Prior read-only states/history contained no transition and do not prove vacancy,
timer expiry, quiet occupancy, saved bindings or safe takeover.

## Next step after release

Read-only authenticated Ingress acceptance of Erdkellerbereich: verify the existing
Boolean/timer/public sensor/responsible automation bindings and actual HA timing,
then contrast an unlike saved zone. No test switching. Identify genuinely missing
helpers before any separately authorized household creation or wiring.

## History

Alpha.69 receipt: `bf1846166738d90be71757f7d6d3c14075acc04f:docs/RELEASE_STATE.json`.
Earlier timed runs are closed; Alpha.64 measurements remain in ROADMAP.md.
