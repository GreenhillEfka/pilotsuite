# PilotSuite capability and acceptance ledger

## Alpha.42 candidate — current lighting decision check

| Capability | Verified source scope |
|---|---|
| Current basis | Canonical roles and current projected zone observations |
| HA relation | Fresh bounded related-automation lookup plus structural config reads |
| Integrity | Revision and effective roles rechecked after HA reads |
| Semantics | Indoor lux is no outdoor proof; transport is no physical freshness proof |
| Decision | Exactly one allowlisted internal next step; no duplicate/safety verdict |
| Boundary | Explicit POST, no persistence, configuration write, learning or execution |

Local repository/API validation, 522 Python and 59 JavaScript tests pass. Local
Chromium is unavailable; exact candidate CI remains required. Alpha.41 is installed
and unchanged. No Alpha.42 backup, publication, Store update or live Ingress
acceptance is claimed yet.

Next: verify exact candidate CI, then create and verify one fresh Alpha.41 app-only
backup before merge/publication and normal installation.

## Installed Alpha.41 — lighting-source integrity

| Capability | Verified source scope |
|---|---|
| Source meaning | Assigned/usable lights, indoor lux and binary brightness are separate |
| Provenance | Synthetic scenario lux never confirms a real outdoor daylight reference |
| Missing input | Unknown current brightness holds instead of reporting a capability defect |
| Temporal integrity | Inconsistent and future checkpoints are rejected |
| Boundary | No HA read/write, persistence, consent or execution added |

Fresh pre-publication backup `bc501582` contains only Alpha.40 app/data/options;
native details report no failed parts, no HA, database or folders. PR 90 release
`e0bfc77`; candidate CI 36289439619 and release-main CI 36289511093 passed all four
jobs. One Store refresh and one update installed Alpha.41; installed/offered/started,
options and auto_update unchanged. Logs report ready, connected stream, fresh snapshot
and resolved zone in unchanged presence_adoption_review mode.

Read-only HA inspection confirmed actual area `erdkeller` / `Erdkeller Innen`, the
user semantic label Erdkellerbereich, two indoor illuminance sources and existing
automation context. No HA configuration, automation, consent, state or device changed.
The authenticated browser session returned 502 connection closed before HA/PilotSuite
loaded, including one reload; this is not UI acceptance.

Next: run the Alpha.41 lighting preview in authenticated read-only Ingress for
Erdkellerbereich, verify that indoor lux is not presented as outdoor daylight proof,
then repeat with one unlike existing zone.

## Installed Alpha.40 — daylight and mood preview

| Capability | Verified source scope |
|---|---|
| Inputs | Presence, daylight lux, brightness, atmosphere and authority remain separate |
| Stability | Stable band, deadband, minimum interval and bounded brightness step |
| Fallbacks | Missing lux/unknown presence/manual override hold; no false-dark inference |
| Targets | Only fixed on/brightness/Kelvin settings; unsupported properties omitted |
| Preview | Six allowlisted scenarios, explicit POST only, no HA I/O/persistence/authority |
| UI integrity | Zone/revision/generation checks, safe text, selection retained, no GET side effects |
| Local validation | 50 API routes, 515 Python and 59 JavaScript tests pass |

PR 88 release f09dd27; candidate CI 36286331268 and release-main CI 36286428926
passed all four jobs, including Chromium, amd64 and reproducible source. Backup
ee6f2dfa contains only Alpha.39 app/data/options. One Store refresh and one update
installed Alpha.40; installed/offered/started with options and auto_update unchanged.
Ready, stream, fresh snapshot and the saved Erdkellerbereich are confirmed. No
household configuration, automation, actor, role, consent, productive data or
execution authority changed.

Next: explicit synthetic lighting preview in authenticated read-only Ingress for
Erdkellerbereich, then one unlike existing zone; runtime health is not UI acceptance.

## Installed Alpha.39 — deterministic presence kernel and explanation replay

| Capability | Verified source scope |
|---|---|
| State model | Pure occupied/grace/vacant/unknown transition kernel; pulse and continuous evidence separated |
| Restart | Existing generation/deadline persists in ContextStore and is not silently extended |
| Conservative absence | Unknown source/dependency, cold start and manual cancel never assert vacancy |
| Invalidation | Presence source change/reset clears checkpoint; savepoints omit operational state |
| Replay | Five allowlisted synthetic scenarios, explicit POST only, no HA I/O/persistence/authority |
| Runtime gate | Dormant reconciler uses the kernel; public enable and general Apply remain denied |
| Local validation | 49 API routes, 506 Python and 59 JavaScript tests pass |

PR 86 release 892cbab; candidate CI 36283655159 and release-main CI 36283761672
passed all four jobs, including Chromium, amd64 and reproducible source. Backup
618bc607 contains only Alpha.38 app/data/options. One Store refresh and one update
installed Alpha.39; installed/offered/started with options and auto_update unchanged.
Ready, stream, snapshot and zone resolution are confirmed in unchanged
presence_adoption_review mode. No explicit restart, rebuild, other app or household
change. Public presence activation and general Apply remain closed.

Authenticated Ingress remains open because the cloud browser returned 502 connection
closed before HA loaded, including one reload after installation. Next: explicit
synthetic replay and read-only role/evidence acceptance in saved Erdkellerbereich.

## Installed Alpha.38 — evidence integrity and coherent sources

| Capability | Verified scope |
|---|---|
| Event admission | Only WorldModel-accepted frames can become new learning events |
| Context time | Delayed activity retained; light/lux withheld on missing or later source timestamps |
| Role integrity | Effective roles consistent; unrelated saves do not promote derived defaults |
| Temperature | Optional independent comparison, separate from median; strict unit/completeness guard |
| Boundaries | No new action, consent, collector, migration or household change |
| Validation | 494 Python, 59 JavaScript; exact candidate/main Chromium and amd64 CI green |

PR 84 release fcdebae; candidate CI 36280638136 and main CI 36280792938 passed
all four jobs. Backup d4f477c9 contains only Alpha.37 app/data/options. Alpha.38 was
already offered; one update installed it, with no Store refresh or explicit restart.
Installed/offered/started; options and auto_update unchanged. Ready, stream, snapshot
and zone resolution confirmed in unchanged presence_adoption_review mode. General
Apply remains closed. Authenticated real Ingress remains open because the cloud
session returned 502 connection closed before HA loaded, including one reload.

Historical Alpha.38 acceptance remained open for the saved Erdkellerbereich and one
unlike existing zone.

## Installed Alpha.37 — presence lifecycle questions

| Capability | Verified scope |
|---|---|
| Boundary close | Flags a literal close-trigger branch that clears a plausible bidirectionally set room status |
| Activity timeout | Flags a literal activity-start branch that directly starts the presence timer |
| Semantics | Device-class based; findings are review questions, not defect/runtime/safety verdicts |
| Integrity | Stale, disabled, dynamic, ambiguous and indirect paths cannot become findings |
| Privacy | No authored trigger IDs, aliases, raw configuration or payload values in the projection |
| Mutation | None: transient analysis, no save/repair/learning/control |
| Validation | 484 Python, 56 JavaScript; exact candidate/main Chromium and amd64 CI green |

PR 82 release 93e6df7; candidate CI 36277330306 and main CI 36277424359 passed all
four jobs. Backup 0baa717d contains only Alpha.36 app/data/options. One Store refresh
and one update installed Alpha.37; started, ready, connected, fresh and zone-resolved
in unchanged presence_adoption_review mode. Options/auto_update unchanged. Real
Ingress remains open because the authenticated cloud endpoint returned 502 before the
UI loaded. Historical lifecycle acceptance remained open for Erdkellerbereich and one unlike zone.

## Installed Alpha.36 — consistent inventory snapshots

| Capability | Verified scope |
|---|---|
| Reconnect | Old snapshot never promoted solely by a later successful connection |
| Batch failure | Lost readiness, including unread configurations, invalidates all batch findings |
| Catalog integrity | Identity, metadata and availability changes conflict; normal values can change |
| Repair preview | Fresh/unchanged inputs required before saving; no execution |
| Regression | Seven synthetic tests, HTTP 409, no plan/context/HA writes on conflict |
| Validation | 475 Python, 56 JavaScript, nine CI Chromium suites, amd64 build |
| Delivery | PR 80; b8ebc1b; candidate CI 36272344492 and main CI 36272461571 green |

Fresh scoped backup 67fa033b contains only Alpha.35 app/data/options. One native Store
refresh/update; Alpha.36 installed/offered/started with unchanged options/auto_update.
Ready, stream, snapshot and zone resolution confirmed; presence_adoption_review retained.
RELEASE_STATE.json owns current evidence. Actual Ingress remains open because the
browser runtime is offline; app-principal rights and independent data/image checks
are not inferred. No household configuration, learning or device action changed.

Historical inventory acceptance remained open for Erdkellerbereich and the other
three existing zones without household configuration or learning changes.

## Repository contract integrity after Alpha.35

| Capability | Delivered scope |
|---|---|
| API inventory | All 48 registered `/api/v1` method/path pairs grouped by semantic owner |
| Effect clarity | Inspection, preview, persistence, restore and apply described separately |
| Drift guard | Dependency-free exact set check of explicit routes against `docs/API.md` |
| Runtime impact | None: no endpoint, payload, app tree, version, option or installation change |
| Local regression | Validator plus 468 Python and 56 JavaScript tests pass |

The historical API-only package did not change the installed Alpha.35 app.

## Previous delivery: Alpha.35 — cumulative inventory integrity

| Capability | Delivered scope |
|---|---|
| Package continuity | Same-zone/revision results accumulate across explicit batches of at most eight |
| Completeness view | Exact requested/total progress plus readable and unreadable counts |
| Integrity filters | References, trigger IDs, unreadable and all-readable; deterministic order |
| Draft continuity | Unsaved role choices and explicit replacement selections remain intact |
| Conservative invalidation | Reload, zone/revision change or invalidation discards transient results |
| Persistence/control | None added; no queue, automatic scan, repair execution or HA write |
| Regression | Ten synthetic automations, two batches, one unreadable config, no mutations |

PR 76 release faf3611; candidate CI 36267009996 and main CI 36267117823 passed all
four jobs. Backup c194bc96 contains only Alpha.34 app/data/options. Alpha.35 is
installed/offered/started with unchanged options/auto_update and healthy readiness.
Authenticated Alpha.35 Ingress remains open; see RELEASE_STATE.json.

## Previous delivery: Alpha.34 — 2026-09-26

PR 74, release 20adb0e; exact source/CI/backup/runtime receipt: RELEASE_STATE.json.

| Capability | Actual scope |
|---|---|
| Trigger integrity | Shared bounded projection in inventory and routine details; paths/counts only |
| ID cases | Missing/partial/matched/disabled/inactive/unknown; implicit indices and shared IDs |
| Honest limits | No flow/safety proof; unreferenced is not unused; dynamic/blueprint cases remain open |
| Review UI | Shared safe text, keyboard/mobile, unsaved selections retained, explicit reads only |
| Inventory recovery | Alpha.33 response isolation/read-only reconciliation preserved |
| Canonical persistence | ContextStore/PlanStore unchanged; no new store, schema or learner |
| Repair execution | Unavailable; review creates no HA write or approval |
| Existing naming executor | Unchanged and not invoked; technical-ID migration still blocked |
| Tests | 468 Python / 56 JS; 14 new Python regressions; nine CI browser suites |
| CI | Exact candidate and release-main all four jobs passed, amd64 included |
| Installation | Alpha.34 installed/offered/started; options/auto_update unchanged |
| Runtime | Ready, stream connected, snapshot fresh, zone resolved; mode unchanged |
| Household acceptance | Authenticated Ingress, app-principal rights, independent image/data checks remain open |

Backup 09436e7c verified before publication: Alpha.33 app/data/options only, no HA/DB/
folders or failed parts. One Store refresh/update, no extra restart or household edits.
HA-wide development reads are authorized independently of productive learning consent.
Four existing zones are user-confirmed; saved identities cannot be inferred from labels.

Historical acceptance of integrity findings remained open across the four saved zones,
starting with Erdkellerbereich.
