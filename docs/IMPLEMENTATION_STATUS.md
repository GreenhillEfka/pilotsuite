# Capability and acceptance ledger

## History increment (development, not installed)
Scoped HA raw/history and hourly statistic reads, zone graphs, weekly activity view
and time-separated reobservation checks implemented. Explicit one-time activity
import shares existing learning store; schema 6 with migration backup. 105 backend
and four JS tests pass locally; CI browser/container gate pending. See
HISTORY_AND_TRENDS.md for consent, retention and limitations. Live remains alpha.11.

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
| Add-on packaging | Implemented | alpha.8 installed and started after app-only backup 89e963d5 |
| Ingress routes / peer restriction | Implemented, local HTTP tests | CI browser passed; interactive alpha.8 role/learning acceptance in actual HA session still pending |
| HA snapshot and event stream | Integrated reconnect correction retained | Short-stream exponential backoff and stable-stream recovery tested; live soak pending |
| Readiness | Stream + snapshot freshness; scope and capabilities separate | Not a physical sensor freshness guarantee |
| Climate normalization | C/F/K to Celsius, finite values, humidity bounds | Plural roles, separate references and source spread implemented; live mapping review pending |
| Suggestions | Deterministic climate rules; stable IDs; unknown confidence | Climate heuristics plus separate activity candidates with independent feedback; not causal habits |
| Habitus zones and roles | Logical zones and entity selection implemented | Stable IDs, multiple areas, extras, editor; role groups with climate median/min/max, separate references and presence-any implemented |
| Learning and consent | Bounded activity candidates implemented | Live event replay tests, role groups, opt-in, retention/export/reset; extended HA learning acceptance still pending |
| SQLite / migrations | Schema 4 for zones, roles, consent, evidence and feedback; migration tests pass | Pre-migration backup, shared revisions, export, bounded selection journal; audit/plans remain JSONL |
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

1. Real HA Ingress loads root, JS, CSS and API without 404; no unintended peer access.
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
