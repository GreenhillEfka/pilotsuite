# Current State

## Candidate: bounded history request timeouts

The next reliability increment maps both the explicit 90-second history budget and
lower-level WebSocket receive/connect timeouts to the existing typed Home Assistant
history error. A stalled Recorder request therefore fails in a controlled way instead
of escaping as a generic HTTP 500. Cancellation remains untouched, and successful
history/statistics responses, storage schema 6, roles, consent and learning do not
change.

One synthetic regression covers the timeout boundary. Local repository validation,
117 backend tests and four JavaScript tests pass. CI browser and amd64-container gates
remain required before merge. Home Assistant remains unchanged on installed alpha.13.

Next: merge only after exact-candidate CI is green. The separate live acceptance item
remains a short read-only history request and graph check in an authenticated local HA
Ingress session; do not enable learning or import history for that test.

## Merged: bounded statistics metadata validation

The next reliability increment validates Home Assistant Recorder metadata before
building the transient statistics projection. A non-list response or an entry
without a non-empty string `statistic_id` now becomes the existing typed HA history
error instead of leaking `TypeError` or `KeyError` through a generic HTTP 500.
Metadata outside the explicitly requested source set is ignored. Successful
statistics, raw history, SQLite schema 6, roles, consent and learning are unchanged.

Synthetic regression covers five malformed response shapes. PR #19 merged the
increment as main commit `af41ee3883bf0b05975933b8d15884cd4df6e274`.
Final main CI 35818141260 passed 116 backend tests, four JavaScript tests, Chromium
browser regression and the amd64 container. Home Assistant remains unchanged on
alpha.13, started and hard read-only.

The next task remains a short read-only history request through an authenticated
local HA Ingress session to verify Recorder coverage and graph rendering. No
learning or historical import is required for that acceptance.

## Released and running: 0.1.0-alpha.13

PR #16 merged the reliability increment as main commit
`734a1e5c272433d37405470918ea93b983e1fdf9`. It converts `aiohttp`
connection failures during a history/statistics WebSocket request into the existing
bounded history error instead of leaking a generic HTTP 500. Malformed text frames
now become the same typed Home Assistant protocol error used for other invalid
frames. This changes no successful response, storage schema, consent, roles or
actuation boundary.

Synthetic regression covers both failure paths. PR #17 released the fix as main
commit `d7068e5b08827a9ddf61df60cf2271b6a1b7aa88`. Candidate CI 35814179314 and
final main CI 35814266844 each passed 115 backend tests, four JavaScript tests,
Chromium browser regression and the amd64 container.

Before publication, scoped PilotSuite App-and-data backup `9bf5a8a1` completed at
2026-09-23T03:27:24Z. The completed listing reports 53,841,920 bytes and excludes
Home Assistant configuration and database. Recovery is a targeted partial restore
of PilotSuite and its data from this backup to alpha.12; archive contents were not
independently inspected and no restore drill was performed.

Supervisor Store metadata links offered `0.1.0-alpha.13` to the exact main commit
above. The update completed, and metadata confirms alpha.13 installed, offered and
started. Startup at 2026-09-23T05:28:40Z reports `hard_read_only`; at 05:28:41Z it
reports `ready=True`, connected event stream, fresh snapshot and resolved Golden
Zone. No error or history request appeared after startup. No role, learning consent,
history import, automation or actuator state was changed.

Authenticated Ingress loading of a short read-only history interval remains the
next live acceptance item. The available remote browser had no authenticated HA
session and could not access the private HA address, so root/assets/APIs, Recorder
coverage and graph rendering are not claimed. Do not enable learning or import
history merely for this acceptance.

## Released and running: 0.1.0-alpha.12

PR #13 is merged as `13e1b03791d93d2bedb3e022b08743a1d61649b9`.
PR #14 released it on main as `52bc972b834aa533575db3e874970f5312c2d513`.
Final main CI 35805983743 passed 113 backend tests, four JavaScript tests,
extended Chromium browser flows and the amd64 container. The release combines
consent-gated coarse event-origin hints with targeted Home Assistant
history/statistics views and separately consented retrospective activity imports.
It remains hard read-only; no learning consent or import is enabled by the update.
SQLite schema 6 backs up schema 5 before migration.

Before publication, scoped App-and-data backup `f803e957` completed at
2026-09-23T01:21:28Z. Its listing reports 53,811,200 bytes and excludes Home
Assistant configuration and database. Recovery is a partial restore of PilotSuite
and its data from that backup; archive contents were not inspected and no restore
drill was performed.

Supervisor Store refresh identified alpha.12 and the update completed. Metadata
confirms alpha.12 installed, offered and started. Startup at 2026-09-23T03:25:47Z
reports `hard_read_only`; at 03:25:48Z it reports `ready=True`, connected event
stream, fresh snapshot and resolved Golden Zone. The protected direct proxy
correctly returns HTTP 403 `Ingress access required`; it was not weakened for
testing. No authenticated HA browser tab was available, so real Ingress root,
asset, API and chart interaction remain unverified for this release. Actual role
choices and Recorder coverage also remain separate live acceptance items. No role,
learning-consent, history-import, automation or actuator state was changed.

Next: in an authenticated HA Ingress session, verify root/JS/CSS/API loading and
load a short read-only history interval to confirm Recorder coverage and graph
rendering. Do not enable learning or import history merely for acceptance.

## Merged implementation: targeted history and zone trends

Branch feat/history-and-trends incorporates main 155fb07 including consent-gated
event attribution. Implements
scoped raw/statistics reads, source/reference graphs, presence/light timelines,
weekly activity raster and chronological reobservation checks. One-time explicit
consent imports only presence activations into the existing bounded activity-v1
store, deduplicated against live/imported evidence. Schema 6 migration backs up
schema 5 and preserves settings. Contract: docs/HISTORY_AND_TRENDS.md / ADR-024.
CI 35802932782 for candidate 31f04a68577a5afbfa9df4d9dfa150659900953c passed
113 backend tests, four JS tests, extended Chromium browser flows and amd64
container. Local repository validation also passed. Implementation is in PR #13.
The following documentation-only commit records that verified candidate.
HA read-only metadata confirms alpha.11 started. No role/consent change or live
historical import was performed. Actual Recorder coverage and Ingress acceptance
remain open.


## Merged, not released: consent-gated coarse event attribution

PR #11 merged as `203fb512dcad1d652aa38eb37e07092855a6edb7`; its tree exactly
matches tested candidate `00773dc3c23ad9274c29608ce1f535689b3afa58`.
Main CI [35802574356](https://github.com/GreenhillEfka/pilotsuite/actions/runs/35802574356)
passed 93 backend tests, four JS tests, Chromium browser regression and amd64
container. Based on installed `0.1.0-alpha.11`, the event stream now
subscribes separately to `state_changed` and `call_service`. When at least one zone
has active learning consent and an eligible source, a bounded in-memory correlator
keeps opaque HA context links for at most 120 seconds / 2,048 entries. Disconnect,
loss of all eligible learning sources or process restart clears them. No service
payload, user ID or context ID is written to SQLite, exports, logs or the UI.

Persisted activity evidence can distinguish direct user context, correlated
parented service context, correlated unparented service context, uncorrelated
derived context and unknown. These are hints, not proof of manual operation or a
specific automation/script. The candidate UI makes that limitation explicit.
PilotSuite remains read-only and therefore produces no own-action evidence.

Synthetic regression covers dual subscriptions, interleaved dispatch, consent
gating, expiry/limit/disconnect clearing, identifier non-disclosure and independent
origin persistence. This increment is merged but not versioned, released or
installed. HA remains unchanged on alpha.11; no production consent was changed.

Next: prepare a separately versioned release candidate without enabling learning,
then require final exact-commit CI, a fresh App-and-data backup and an explicit
recovery target to alpha.11 before deployment. Live attribution acceptance requires
already-consented real learning; do not enable it merely for a test.

## Released and running: 0.1.0-alpha.11

PR #9 merged as a1bb95f7a6c045ece234ad70e8e9ee3c855129d0. The merge tree
c2a47079e11c89885fd418cec21afdb1505d651c exactly matches candidate 258a116.
Final CI 35800786084 passed 85 backend tests, four JS tests, extended mobile
browser flows and amd64 container including IANA timezone availability.

Fresh App-only backup 1b74df9a was created before publication because auto-updates
are enabled, and confirmed in the completed listing: 53,739,520 bytes, unprotected,
HA configuration/database excluded. Requested scope was PilotSuite and its data;
archive contents were not inspected and no restore drill was performed. Recovery
is a partial App-and-data restore of this backup, not schema-4 code over schema 5.

Supervisor update completed; metadata confirms alpha.11 started with unchanged
options. Startup at log timestamp 2026-09-23T02:10:59Z reports hard_read_only;
02:11:00Z reports ready=True, stream=True, snapshot_fresh=True, zone_resolved=True.
Startup necessarily completed database initialization; migration copies were not
independently inspected on the host. Migration preservation is covered by tests.
Real iPhone Ingress requests after startup (02:11:10–16Z) returned HTTP 200 for
context, selections, zones and status; root/assets also returned 200. This is not
proof of interactive acceptance of every control or the user's exact live roles.

This release includes configured activity thresholds, local time/day groups,
source/progress/module views, sampled observability and separately consented
light/lux context. No production role, timezone or consent was changed by this
release operation; new context consent defaults off. HA actuation stays blocked.
Next: actual zone UI acceptance, explicit learning choices and real multi-day
observations. Physical sensor coverage is not guaranteed; presence/light were
partial at startup. Temporal switching sequences and HA draft execution remain
future work. Contracts: docs/RHYTHMS_AND_CONTEXT.md and LEARNING_AND_ACTIONS.md.

## Historical development notes

## Next package: local rhythms and activation context (development)

PR #9 now includes persisted IANA timezone and weekday/weekend grouping, DST-safe
local-day counts, bounded sampled observability and separately consented light/lux
context at accepted activity events. Explicit source groups only; unknown values
stay unknown. Context cards make read-only review suggestions, not HA commands.
Schema 5 backs up before adding two tables; existing context consent defaults off.
85 backend tests and repository validation pass locally. Browser test now covers
new settings and context/coverage rendering; expanded CI remains a required gate.
The previous df5a77b head passed all CI 35799028200 before this package.
Verified at package start: PR #9 open, main d48e719, HA alpha.9 started. No production
consent, role edit, update or HA automation was performed by this increment.
Contract and recovery: docs/RHYTHMS_AND_CONTEXT.md / ADR-022. Release requires an
App-and-data backup because schema-4 code cannot open schema 5. Remaining: actual
HA Ingress acceptance and real multi-day data; temporal light sequences, shadow
execution and native HA drafts are explicitly deferred.


## Development: zone overview and evidence progress

PR #9 now also provides per-zone activity-v1 minimum events (5–100) and days
(3–14), revision-safe persistence, bounded validation, parameter-specific pattern
identity and a module status overview. Evidence is retained on parameter edits;
consent does not change. docs/LEARNING_AND_ACTIONS.md separates implemented learning
from planned script/automation drafts and governed execution. 70 backend tests,
four JS tests and validation pass locally. The previous PR head d76b40a passed CI
35798093744 (backend/browser/container); the expanded head needs its own CI gate.
Main advanced to alpha.10 via PR #10 during this work. Its structured assessment
contract is merged and rule-strength ratios use the configured per-zone thresholds.
No installation or new learning/actuation consent performed in this increment.


Extends alpha.9 with expandable source details in reference cards; persisted
presence-group names; collection-state explanations; consent and first/last retained
evidence timestamps; per-UTC-window counts and missing candidate requirements.
No statistical confidence percentage or uninterrupted coverage is implied.
No schema migration, role rewrite, consent change or HA update in this increment.
Previous increment: 66 backend tests and four JS tests passed locally; repository validation passed.
Browser regression extended, but local Chromium is unavailable: CI must verify it.
Live read-only check confirms alpha.9 started, ready and real Ingress API HTTP 200.
The user's exact live selection remains uninspected through the protected APIs.
Next: CI browser/container gate, then release preparation and scoped backup before
any production update. Real multi-day habits and live interactive acceptance remain open.


## Release candidate: 0.1.0-alpha.10 structured activity evidence

The next bounded change gives `activity-v1` candidates independent observation
statistics, deterministic threshold ratios, nullable statistical confidence,
read-only risk and durable user preference fields. Deprecated flat alpha fields
remain compatibility aliases; feedback still changes no evidence. Synthetic tests
cover the contract and persistence. PR #10 candidate CI 35798185711 passed 64
backend tests, four JS tests, browser regression and amd64 container before the
release metadata commit. App-only backup 522eda91 was then created from running
alpha.9; the completed listing excludes HA configuration/database. The partial
restore target is PilotSuite and its data only; archive internals and a restore
drill were not performed. alpha.9 remains installed until the final release-metadata
CI passes. Production learning consent remains unchanged.

## Released and running: 0.1.0-alpha.9

PR #8 merged as 04db3fb103850dd1c6f495d035f646d488a27b3d. Its tree
cbe0f8e1140a0f0d57b444041f8213ce7a8ba529 exactly matches candidate b1553a2.
Final CI 35797007069 passed 63 backend tests, four JS tests, extended mobile
browser regression and amd64 container. A mismatched Docker version marker was
caught by the release test and fixed before this final CI and deployment.

ADR-018 and docs/SENSOR_REFERENCES.md define the revised contract: automatic
virtual references for temperature, humidity, illuminance, presence and light;
persisted empty groups; consistent presence display/learning sources; visible
legacy defaults and explicit external comparison-temperature labeling.

App-only backup 19bfccc7 was created and confirmed before merge (automatic app
updates were already enabled). Listing reports unprotected, HA/database excluded.
Only PilotSuite and its data were requested; archive contents were not inspected.
Recovery is an App-and-data partial restore of that backup, not a full HA restore;
no restore drill was performed. No database migration or role rewrite was added.

Supervisor confirms alpha.9 started with unchanged options. Runtime logs at
2026-09-23T01:23:08Z report hard_read_only, ready=True, stream=True,
snapshot_fresh=True, zone_resolved=True. Existing source availability remains
partial for presence/light; readiness is not a physical sensor completeness claim.
Actual user selection and UI behavior in the live Ingress session remain to be
accepted. Do not infer that the user's exact presence-saving issue was reproduced:
code inspection found an inconsistent fallback and explicit-empty-group loss;
API persistence and browser reopen tests cover the corrections. Learning consent
was not changed by this deployment. New sensor classes require typed semantics;
no generic energy/alarm aggregation and no native HA reference entities yet.

## Historical alpha.8 deployment

Last updated: 2026-09-23 (runtime log UTC)

## Released and running: 0.1.0-alpha.8

PR #7 merged as 3aec18fce0b9d1e36abed1f81b38a034d36dcdcb with the exact
CI-tested tree f7ec8d4395f52b7b501424591dc4936031a183b8. CI 35793755621
passed 59 backend tests, four JavaScript tests, browser workflow tests and the
amd64 container build. A new subprocess regression executes the real module
entrypoint and checks HTTP health and database creation.

PilotSuite-only alpha.6 backup 89e963d5 was created and confirmed before updating;
HA configuration/database and unrelated Apps were excluded. alpha.7 initially
failed before startup callbacks/schema migration because main ran before newly
added route handlers were defined. alpha.8 moves the entrypoint after all handlers.
After installing alpha.8, an explicit start recovered the previously failed App.
Supervisor reports version 0.1.0-alpha.8 and state started. Runtime logs at
2026-09-23T00:45:49Z confirm hard_read_only, ready=True, stream=True,
snapshot_fresh=True and zone_resolved=True. Temperature/humidity/motion/illuminance
are available; presence/light are partial. Readiness does not mean every source
is complete or physically fresh.

## Implemented

Contract: docs/OBSERVATION_LEARNING.md and ADR-017. Only explicitly relevant
entities feed zone evaluation; unreviewed and ignored entities are excluded.
Zone tabs, mutable names, multiple HA-area sources, extra entity candidates and
direct start/pause remain available. The user confirmed Badbereich activation in
alpha.6; do not recreate it or infer that its new role groups were reviewed.

Compact zone cards summarize temperature, humidity, presence and light; entity
selection and raw neurons are expandable. Plural sensor roles support climate
median with source range/quality, separate reference temperatures and presence
from any active group member. A multi-room median is a zone summary, not an
individual room temperature. Missing or conflicting data remains visible.

Learning defaults off per zone. Explicit consent allows bounded live presence
activity evidence (14-day retention, 5,000 global records, five-minute zone-wide
cooldown). Candidates require at least five activations on three distinct UTC
dates in a two-hour UTC window. They carry unknown confidence, not causal or
person-specific claims. Feedback is independently persisted; export/reset and
consent revocation are implemented. No production consent was enabled and no
synthetic evidence was seeded during deployment. Climate suggestions remain
deterministic heuristics, separate from these activity candidates.

SQLite schema 4 stores zone definitions/selections, role groups, consent, evidence
and feedback, with migration backups and shared revision conflict checks. The
actual archive file was not inspected on the HA host. The successful startup
completed initialization; migration/backup details are covered by tests.

The reconnect correction from PR #4 (CI 35792464489, merge aac362a) remains:
short streams retain bounded 1/2/4/8/16/30-second backoff, reset only after a
60-second stable subscribed stream. Authentication failures do not report connected.
Ingress peer restrictions and hard-disabled HA actuation remain in force.

## Acceptance limits and next work

Startup/transport readiness is live-verified for alpha.8. Role selection, consent,
revision conflicts, feedback and reset passed browser/API tests, but these are not
proof of interactive acceptance in the user's actual HA Ingress session. The MCP
proxy cannot inspect protected APIs through the peer guard; do not bypass it.
No real multi-day learned routine is claimed. Live disconnect/load soak is pending.

Next: review relevant sources and plural roles in the actual zone UI; optionally
grant learning consent, then evaluate real evidence and durable feedback. Validate
a second unlike zone before 1.0. No autonomous HA action engine, native adapter,
voice integration, LLM dependency or causal habit model is implemented.

For downgrade recovery restore the scoped App-and-data backup 89e963d5; never
feed schema 4 to older code. No restore drill was performed. Historical alpha.5
and alpha.6 release evidence remains in git history and merged PRs #1/#3/#5.
The canonical repository remains GreenhillEfka/pilotsuite.
