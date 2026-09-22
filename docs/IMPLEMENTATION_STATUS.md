# Capability and acceptance ledger

## Development branch: logical Habitus zones (2026-09-22)

PR #1 (`feat/entity-selection-package`) implements logical zones with stable IDs,
multiple HA-area sources and extra entity candidates; an Ingress editor, curated
entity selection, shared revisions, per-zone inference, neutral/cellar profiles,
JSON export and a bounded journal. Schema 3 backs up schema 1/2 before migration.
Existing decisions are preserved; new zones start paused in the UI. Global entity
counts deduplicate IDs. Contract: `docs/HABITUS_ZONES.md` and ADR-015.

46 Python tests and four JavaScript model tests pass locally. CI run 35786624245
passed backend, zone-creation browser regression and amd64 container for commit
33da5d6. A final follow-up corrects multi-zone status and adds schema-2 migration
coverage; use the latest PR checks for that head. No new version or HA installation
in this increment. Production alpha.4 evidence below remains the live baseline.
Contextual role priorities, import, permanent deletion and learning remain deferred.


Stand: capability correction 0.1.0-alpha.4. "Local tests" is not live HA acceptance.

| Capability | Code state | Acceptance / remaining work |
|---|---|---|
| Add-on packaging | Implemented | alpha.4 installed and started after app-only backup |
| Ingress routes / peer restriction | Implemented, local HTTP tests | Real browser API responses 200; new alpha.4 visual/asset rendering not yet independently checked |
| HA snapshot and event stream | Implemented | Reconnect resync/backoff tests; live disconnect/load soak pending |
| Readiness | Stream + snapshot freshness; scope and capabilities separate | Not a physical sensor freshness guarantee |
| Climate normalization | C/F/K to Celsius, finite values, humidity bounds | Sensor role assignment and conflicting readings still pending |
| Suggestions | Deterministic climate rules; stable IDs; unknown confidence | Not learned habits; no persistent feedback yet |
| Habitus zones and roles | Target accepted | Current resolver remains area-based; role editor/storage pending |
| Learning and consent | Planned | Attribution, bounded evidence, replay fixtures, consent/export/delete |
| SQLite / migrations | Planned | Alpha audit/plans still JSONL; migration/recovery tests required |
| Multi-user preferences | Planned | Separate preference from evidence; conflict rules required |
| Brain graph | Planned | Derived explanation graph, not a separate truth store |
| Native HA adapter / Assist | Optional, planned | No current custom integration in canonical repository |
| LLM / RAG | Optional, planned | Read-only tool boundary; no direct action execution |
| HomeKit candidates | Planned | Inventory-based review only; no automatic export |
| Module UI / Dev / Wiki | Planned | Current UI is observations/status/suggestions only |
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
