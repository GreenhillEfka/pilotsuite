# Current state — Alpha.71 installed; household acceptance pending

## Completed package: PR #151

The user explicitly continued the existing package after the timed runs ended.
The heartbeat remains paused; no new timed loop, chat or background job.
PR #151 is merged. Closing delivery evidence uses the same feature branch;
do not create another PR merely to record the receipt PR's own CI.

Alpha.71 adds one missing Boolean/timer through the existing package endpoint,
PlanStore and creation/readback/recovery transaction. Existing or unresolved role
bindings, owned packages and registry collisions block replacement. Timer duration
is explicit and bounded. No automatic binding, automation connection, publication,
control transfer or interpretation of initial off/idle as vacancy.
UI separates individual creation from a full owned output package and name edits;
drafts survive errors. Confirmed creation is explicitly not a working presence chain.

## Verified release and installation

PR #151 candidate `c96fda7ddb4225fb383bd7b206005a10190911f9`;
release-main `7e6bb5ee9348df9999106cd283d448cb7e3b8ad3`.
Both passed all five CI jobs: runs `36540248104` / `36540501031`.
Root tree `3958527cdd2d4c4fbe0aaffbb3ba9a738f949a4c`;
app tree `4d7baccf4b09c637fd8179336cc830853d8c991e`.
Source preflight and own diff review passed; all 11 browser suites and six real
isolated HA 2026.9.3 protocol scenarios passed. No household protocol testing.

Local 651 Python / 78 JS / 62 contracts, discovery and compilation pass.
Repeated exact-release-main resource audit: zero warnings. Three affected browsers
pass; unlike-zone 390/768/1440 light/dark screenshots inspected. Initial feature
regressions and stale-revision/disabled-identity failures were reproduced before fixes.
Additional cases cover lost response, readback failure/restart, wrong identity,
expiry, exact confirmation/zone and missing comparison configuration.

Fresh prepublication backup `e5df45f0`, 29 Sep 07:58:30.470906 UTC: native list and
backup/details confirm only Alpha.70 PilotSuite app/data/options, 54,497,280 bytes,
no HA/database/folders/failures, local unprotected agent. Scope rechecked immediately
before installation. No extraction or restore drill.

At 08:12:48 UTC: Alpha.71 installed/offered/started; all four options unchanged.
One Store refresh and one targeted update; no extra restart/rebuild/other-app update.
Startup remains presence_adoption_review, ready, connected, fresh and zone-resolved.
Log times copied as emitted, not clock-attested. RELEASE_STATE.json owns the receipt.
Do not repeat the Alpha.71 installation.

## Boundaries and actual gaps

Preserve all four saved zones, entity cleanup and untracked AGENTS.md. No schema or
configuration migration, auth/Ingress/sandbox change or learning grant. General
Apply remains closed; bounded executors are not universal hard_read_only.
Existing HA automations remain in control.

Concrete household-write scope remains unanswered. No household helper creation,
rename, automation edit/enable/disable, output activation or control transfer.
Reuse/adoption is an authorized direction, not permanently forbidden. New individual
helper creation requires an exact user-confirmed plan; app installation alone creates
no helper. Active HA-parameter editing and automation wiring/execution remain
unimplemented. Do not reopen the legacy provisioner.

No authenticated HA browser is connected. Real Ingress/four-zone acceptance remains
open. Prior read-only states/history contained no transition and do not prove vacancy,
timer expiry, quiet occupancy, saved bindings or safe takeover.

## Next step

Read-only authenticated Ingress acceptance of Erdkellerbereich: verify existing
Boolean/timer/public sensor/responsible automation bindings and actual HA timing,
then contrast an unlike saved zone. No test switching. Identify genuinely missing
helpers before separately authorizing household creation or wiring.

## History

PR #148: Alpha.69 thematic zone Automationen; PR #149: Alpha.70 public HA status
first and honest validity/timing; PR #150: its delivery receipt. ADR-043 and
UX_WORKSPACE.md retain concept/research. Alpha.70 receipt is retained at
`7e6bb5ee9348df9999106cd283d448cb7e3b8ad3:docs/RELEASE_STATE.json`.
Earlier timed runs stay closed; Alpha.64 measurements remain in ROADMAP.md.
