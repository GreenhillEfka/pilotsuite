# Capability and acceptance ledger

## History transport reliability increment

Connection failures during scoped history/statistics WebSocket requests are mapped
to the existing user-facing bounded history error; malformed text frames are mapped
to the typed HA protocol error. Successful reads, storage, consent and learning are
unchanged. Two synthetic regressions bring the local backend suite to 115 tests;
four JavaScript tests and repository validation also pass. Merge still requires
exact PR CI. Live remains alpha.12 with authenticated history interaction pending.

## alpha.12 released and installed

PR #14 released main commit 52bc972; CI 35805983743 passed 113 backend
tests, four JavaScript tests, Chromium browser flows and the amd64 container.
Scoped pre-update App-and-data backup f803e957 is complete and excludes Home
Assistant configuration/database. Supervisor reports alpha.12 installed, offered
and started. Runtime reports hard read-only, connected event stream, fresh snapshot,
resolved Golden Zone and readiness. The protected non-Ingress proxy continues to
reject API access with HTTP 403, as designed.

The code reads only saved relevant main groups through supported Home Assistant
APIs, keeps raw history transient, and imports historical activations only after an
additional interval-scoped consent. Event-origin identifiers remain memory-only and
are persisted only as coarse categories. Schema 6 creates a pre-migration backup and
shares the existing activity-v1 evidence owner. The update changed no production
role, learning/import consent, automation or actuator. Authenticated Ingress assets,
APIs, chart interaction and actual Recorder coverage remain live acceptance work.

## History increment (included in alpha.12)
Scoped HA raw/history and hourly statistic reads, zone graphs, weekly activity view
and time-separated reobservation checks implemented. Explicit one-time activity
import shares existing learning store; schema 6 with migration backup. 113 backend
and four JS tests pass; final release CI 35805983743 also passed Chromium browser
and container. See HISTORY_AND_TRENDS.md for consent, retention and limitations.
Live acceptance remains separate from test coverage.

## Merged after alpha.11: bounded origin hints

PR #11 merged as 203fb51 with the exact tree tested at 00773dc. Main CI
35802574356 passed 93 backend tests, four JS tests, Chromium browser regression
and amd64 container. The code is merged but not versioned, released or installed;
HA remains on alpha.11 and production learning consent is unchanged.

The next small slice subscribes to HA `call_service` and correlates its context
with activity state changes for 120 seconds in bounded memory. Correlation only
runs with active per-zone learning consent and an eligible source; disconnect or
loss of all eligible sources clears it. SQLite/export/UI receive only coarse origin
categories, never HA user/context IDs or service payloads. Parented service context
is displayed as a possible automation/script chain, not as causal proof. PilotSuite
is read-only and emits no own-action evidence.

Live origin acceptance remains separate and may use only already-consented
learning. No version bump, HA update, role change or production consent change.

## alpha.11 released and installed

PR #9 merge a1bb95f matches the final tested tree c2a4707. CI 35800786084
passed 85 backend tests, four JS tests, browser and amd64 container. Backup
1b74df9a created/confirmed before publication; Supervisor update/start successful.
Runtime confirms alpha.11 read-only, ready, connected and freshly reconciled.
Post-start real Ingress context/selections/zones/status requests return HTTP 200.
Schema-5 initialization completed during startup; migration copy files were not
independently inspected. No production role or consent change was performed.
Interactive live UI acceptance and real multi-day learning remain pending.

## alpha.10 release candidate

The next candidate separates activity observation statistics, deterministic rule
threshold ratios, nullable confidence, read-only risk and persisted preference.
Synthetic regression covers evidence/feedback invariance. PR #10 candidate CI
35798185711 passed 64 backend tests, four JS tests, browser and amd64 container.
App-only alpha.9 backup 522eda91 is complete; final release-metadata CI and live
deployment verification remain. Learning consent is unchanged.

## alpha.9 update

PR #8 / merge 04db3fb; final CI 35797007069 passed 63 backend tests, four JS
tests, browser and container. App-only backup 19bfccc7 confirmed. Supervisor and
startup logs verify alpha.9 started/read-only/ready with connected event stream.
Automatic typed references, illuminance, explicit-empty groups and unified
presence-source semantics are implemented. Actual live user role-selection
acceptance remains open. See CURRENT_STATE.md and docs/SENSOR_REFERENCES.md.

## Historical alpha.8 baseline

Stand: released and running 0.1.0-alpha.8, merge 3aec18f. CI 35793755621
passed 59 backend tests (including real module startup), four JS tests, browser
workflows and amd64 image build. Confirmed pre-update App-only backup: 89e963d5.
alpha.7 failed before schema migration due to handler definition order; alpha.8
fixes that startup defect. Supervisor reports started; runtime at
2026-09-23T00:45:49Z confirms hard_read_only, ready, connected stream, fresh
snapshot and resolved zone. Local/CI tests are not interactive live HA acceptance.
The user confirmed Badbereich activation in alpha.6. New role/learning interactions
and real multi-day activity candidates still need live acceptance; consent stays off.

| Capability | Code state | Acceptance / remaining work |
|---|---|---|
| Add-on packaging | Implemented | alpha.12 installed and started after scoped App-and-data backup f803e957 |
| Ingress routes / peer restriction | Implemented, local HTTP tests | CI browser passed and live direct proxy rejects with 403; authenticated alpha.12 root/assets/APIs/charts remain pending |
| HA snapshot and event stream | Integrated reconnect correction retained | Short-stream exponential backoff and stable-stream recovery tested; live soak pending |
| Readiness | Stream + snapshot freshness; scope and capabilities separate | Not a physical sensor freshness guarantee |
| Climate normalization | C/F/K to Celsius, finite values, humidity bounds | Plural roles, separate references and source spread implemented; live mapping review pending |
| Suggestions | Deterministic climate rules; stable IDs; unknown confidence | Climate heuristics plus separate activity candidates with independent feedback; not causal habits |
| Habitus zones and roles | Logical zones and entity selection implemented | Stable IDs, multiple areas, extras, editor; role groups with climate median/min/max, separate references and presence-any implemented |
| Learning and consent | Bounded activity candidates and coarse consent-gated origin hints implemented | Live event replay tests, role groups, opt-in, retention/export/reset; exact automation/manual attribution is intentionally not claimed; extended HA learning acceptance pending |
| SQLite / migrations | Schema 6 for zones, roles, consent, evidence, feedback and history provenance; migration tests pass | Pre-migration backup, shared revisions, export, bounded selection journal; audit/plans remain JSONL |
| Multi-user preferences | Planned | Separate preference from evidence; conflict rules required |
| Brain graph | Planned | Derived explanation graph, not a separate truth store |
| Native HA adapter / Assist | Optional, planned | No current custom integration in canonical repository |
| LLM / RAG | Optional, planned | Read-only tool boundary; no direct action execution |
| HomeKit candidates | Planned | Inventory-based review only; no automatic export |
| Module UI / Dev / Wiki | Planned | Zone tabs, compact cards, opt-in learning controls; broader module/Dev/Wiki UI deferred |
| Action plans | Dry-run, always denied | Typed action catalog and approval lifecycle pending |
| Backup / verify / recovery | Planned | No runtime execution or rollback engine implemented |
| Update / presets | Standard app versioning | Signed images and update/recovery drills pending |
| Legacy HA cleanup | Not verified comprehensively | Store repo removal does not prove HACS/config entries/entities removed |

## Next acceptance gates

1. Authenticated alpha.12 HA Ingress loads root, JS, CSS and API without 404; a short read-only history request renders graphs and no unintended peer access exists.
2. Real Golden Zone role mapping is reviewed; missing/conflicting data remains explicit.
3. HA restart/disconnect does not falsely report readiness; reconnect restores projection.
4. One consented read-only habit produces a traceable proposal and durable feedback.
5. A second unlike zone validates generality before 1.0; no automatic actuation.
6. Only then add one bounded, reversible action with fault-injection and recovery tests.

Known limitations: snapshots are not atomic HA transactions; stream replay is not
durable. Timestamp guarding prevents older state updates replacing newer values,
but deletion ordering still relies on subsequent reconciliation. Current climate
thresholds are heuristics, not a validated cellar-control policy. No ventilation
command may be inferred from relative humidity alone.

The retained reconnect correction from PR #4 passed CI 35792464489 before merge
aac362a; PR #5 records that gate. alpha.8 retains it with the new role/learning package.
