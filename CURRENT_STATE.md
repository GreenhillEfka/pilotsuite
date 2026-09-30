# Current state — Habitus setup implementation; Alpha.71 installed

## Active assignment, 30.09.2026 until 08:00 Europe/Berlin

The user explicitly authorized autonomous development through this new window.
Branch `feat/habitus-zone-setup` from `e3e5dc2`; preserve untracked AGENTS.md.
`docs/HABITUS_SETUP_PLAN.md` owns the ordered work and cutoff times. The existing
heartbeat is active on the current thread; earlier paused-loop statements below
are historical. No new agent or parallel checkout.

Implemented locally: device/entity label import in the existing zone editor;
atomic zone, stable membership, desired Habitus roles and relevance save in the
existing SQLite transaction; duplicate label ownership and identity/anchor guards.
Explicit batch HA label preview/apply/readback/restore reuses ontology/PlanStore;
foreign labels, names and locations survive. The form hides unrelated setup panels.
One concrete apply button replaces redundant browser confirmation dialogs.
Installed version remains Alpha.71; no household metadata or control changed.

Validation: first label/import slice passed all 661 Python, 78 JS tests and 66 API
contracts. Extended browser passed import, passive refresh, 390/768/1440 themes,
batch labels/readback/rollback with no actor calls. Skills updated and validated.
Autolabeling then added to the existing helper transaction: readable names,
role/zone labels, durable before/after receipts, lost-response readback and manual
conflict protection. Full own package binds its members to structure/scope in the
same transaction. Complete rerun: 665 Python tests pass; 78 JavaScript tests and
66 API contracts pass. Extended browser passes; mobile light screenshot inspected
with reduced motion to avoid capturing an unfinished theme transition. New helper
autolabel cases cover full member binding, lost metadata response and conflict on
manual edits. No HA household mutation, publication or installation performed.
Next local slice implemented: pending zone labels and member metadata share one
confirmed plan, native label receipt/readback and atomic canonical ID binding.
Area/extra candidates are selectable in the same form, with analysis off by default.
Fresh global anchors/device labels/shared roles and final metadata are checked;
manual conflicts do not get overwritten. Four regressions reproduced red before fix.
679 Python, 78 JS, 67 contracts and all eleven existing browsers pass locally;
selection browser required the existing dependency's NODE_PATH. Seven native HA
2026.9.3 protocol scenarios pass in a local disposable instance. New form screenshots
reviewed in light/dark. Metadata plan history now has correct labels, effects and
endpoints; its additional zone-browser regression and the organization browser pass.
Presence/connection UX is now implemented locally: visible zone setup steps lead
to the existing editors; verified stable zone members can prefill empty existing
presence bindings without saving or replacing drafts. Explicit save replaces the
redundant generic mapping confirmation. Publication has its concrete effect and
owned sensor target visible in the same form. Disabled anchors still block a
replacement package. 685 Python, 78 JS and 67 contracts pass; affected foundation,
workspace, organization and extended zone browsers pass. New mobile setup and
binding proposal screenshots inspected. Browser fixture uses one consistent clock
for status freshness and deterministic presence, without changing production guards.
The light comparison now uses the primary zone presence and existing light policy
in the same tick/operational store. Stable relevant target/source identities,
explicit outdoor-lux provenance, bounded brightness/temperature proposals and a
configurable hold after external light changes are visible in the zone editor.
No second presence session or light actuator path. Restart preserves proposal
cooldown; identity conflicts remain suspended until explicit reconfiguration.
701 Python / 78 JS / 68 API contracts pass. Extended zone browser passes the light
editor, unsaved/error retention and proposals without actuator calls. All eleven
browser suites pass; complete resource audit reports no ResourceWarnings. Seven
native HA protocol cases passed again. The component-browser launcher filename
was corrected before completing the remaining suites; no product failure hidden.
Active light control/automation takeover remains a separate unfinished capability,
not implied by comparison settings, relevance, tags or app installation.
Full exact-source release gates and actual household acceptance remain pending.
Alpha.72 markers/changelogs prepared locally. Fresh partial backup `63f11346`,
30 Sep 02:05:15 UTC, confirms only Alpha.71 PilotSuite, 54,528,000 bytes locally,
no HA/database/folders or failed components. However native backup/details reports
list failures for two unrelated Synology agents. The runbook's empty agent_errors
gate is not met. No publication/installation; do not weaken that gate implicitly.

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
