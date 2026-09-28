# Current state — Alpha.67 installed; household acceptance pending

## Safe UI handoff — PR #146 / Alpha.68 candidate, not installed

New one-hour user request: 28 September, 19:33:18–20:33:18 UTC; no new package
or publication after 20:13:18 UTC. Work stays on `fix/alpha68-setup-navigation`.
Four setup shortcuts reuse existing presence, source, entity and zone editors.
Hidden-role focus failure was reproduced first in the existing workspace browser;
the editor now focuses a visible field, and presence editing focuses the grace time.
The main-source link no longer leads to the learning workbench. Dirty drafts remain
protected; no household configuration, execution authority or persisted zone changed.

Local checks passed: 637 Python, 75 JS, 62 API contracts, discovery, repeated
zero-ResourceWarning audit, workspace and zone-instance browser suites. Synthetic
390/768/1440-pixel light/dark checks cover focus, navigation and no HA writes;
screenshots are not real Ingress acceptance.
Candidate `9b4dc353f0046825d19532d2dc638085183ab297` passed all five CI jobs in
run `36477800406`, including all 11 browser suites, container and HA protocol.
Final handoff adds two browser guard checks and receipt notes; its exact CI is
recorded on PR #146, not inferred from this earlier green run. Release-main CI
remains pending because no merge/update is performed in this bounded run.
Alpha.67 delivery evidence below remains the installed/published baseline.

PilotSuite-only backup `cd419ede` at 19:45:10 UTC: exactly Alpha.67 app/data/options,
54,497,280 bytes, no HA/database/folders/failures; native list/details verified,
local and unprotected, not extracted or restored. Fresh live read at 20:15 UTC
confirmed Alpha.67 installed/offered/started, all four options unchanged and
ready/connected/fresh/resolved logs. No Store refresh, update or explicit restart.
At the publication cutoff the tested package was secured as draft PR #146 rather
than starting a release under time pressure. Resume this branch/PR; first recheck
main, exact-head CI and fresh backup requirements, then the complete runbook.
No actual Ingress acceptance is available. The timeboxed heartbeat is paused at
handoff; the one-hour window is not extended.

## Verified delivery

PR #144 merged as `5ac673fa5d728b73a5a6ac612b43c6c8df65be05`.
Exact candidate CI `36469540355` and release-main CI
`36471554267` passed all five jobs: tests, all 11 browser suites,
amd64 container, reproducible checkout and disposable Home Assistant protocol.
Candidate/main repository tree: `953a208c1f14cd09f41743faa4ebfc1386f7bc2c`;
app tree: `9f26f2eb11a4c1be43788a1c5b3c3e0758a20be4`.
Local and connector trees matched; versioned source preflight passed.

Fresh PilotSuite-only backup `62b66f9e` completed at 19:00:10 UTC before version
publication: exactly Alpha.66 app/data/options, 54,476,800 bytes, no HA/database,
folders or failures. Native list and backup/details verified metadata; local and
unprotected, no extraction or restore drill. One Store refresh and one targeted
update installed Alpha.67; no extra restart/rebuild or other-app update.

Installed/offered Alpha.67 is started. All four app option values are unchanged.
Startup remains `presence_adoption_review`; ready, stream connected, snapshot
fresh and zone resolved. Log timestamps are copied as emitted, not clock-attested.
Full source/backup/runtime evidence: [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).

## Implemented and tested

Malformed binary observations remain invalid, not false/good. Explicit on/off and
missing-state semantics remain compatible. Invalid members block a negative role
summary, while valid positive evidence remains a positive partial result.
Lighting brief and synthetic preview share source validity: malformed binary/light
states, invalid lux and unsupported lux units are not counted as usable.

Red baseline: 64 normalization/summary subcase failures; eight lighting assertion
failures and two malformed-payload errors. After fixes: 637 Python / 75 JS /
62 API contracts, discovery/compilation, synthetic workspace browser and repeated
zero-ResourceWarning audit passed. All 11 browser suites passed candidate/main CI.
Own diff review complete; no second engine, store, configuration owner or migration.
No household binding/helper/metadata/automation/output/consent changed. AGENTS.md
remains unchanged and untracked; Ingress/authentication intact.

## Scope and remaining acceptance

The bounded two-hour run was safely stopped with PR #144 as an unversioned draft;
its unchanged-version release gate correctly failed. The heartbeat was paused.
The subsequent explicit user request "Kein Problem, mach die Arbeit fertig"
authorized completion of this existing package and its safe release. That completion
is now delivered; the scheduler remains paused and earlier windows are not reopened.

No authenticated HA browser session is available. Actual Ingress navigation and
four-zone household acceptance remain open; synthetic tests do not replace them.
When available, inspect Erdkellerbereich and one unlike zone read-only. Preserve
all four saved zones, entity cleanup and Habituszonen as the reference.

User permits adoption/reuse of existing automations, but concrete live-edit scope
is still unanswered. No household automation edit/enable/disable or control transfer.
An executable change path needs its own reviewed before/after plan and recovery.

Next separate bounded investigation: missing/derived versus explicit-empty lighting
roles in existing owners. This release unifies validity, not role derivation.
No additional feature package is implied by the completion request.

## History

Alpha.66 receipt: `2cbb3fe1a8496a01e7554874f62308d3bc37766b:docs/RELEASE_STATE.json`.
Alpha.64 measurements/tradeoff remain in ROADMAP.md and its historical receipt.
