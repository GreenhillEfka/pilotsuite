# Capability and acceptance ledger

Stand: released and installed 0.1.0-alpha.6. Local/CI tests are not live HA
acceptance. Candidate 9d3b809 passed CI 35790792191: backend, browser and amd64
image. Merge 290ef42 was installed after confirmed App-only backup dc8bd58c.
Runtime logs confirm hard_read_only, ready, connected stream and resolved zone.
The user confirmed successful Badbereich activation in the actual alpha.6 UI.

| Capability | Code state | Acceptance / remaining work |
|---|---|---|
| Add-on packaging | Implemented | alpha.6 installed and started after app-only backup dc8bd58c |
| Ingress routes / peer restriction | Implemented, local HTTP tests | CI browser passed; actual alpha.6 zone activation confirmed, exhaustive visual/asset review still open |
| HA snapshot and event stream | Implemented; reconnect integration pending CI | Short streams retain exponential backoff; stable idle streams reset it; live disconnect/load soak pending |
| Readiness | Stream + snapshot freshness; scope and capabilities separate | Not a physical sensor freshness guarantee |
| Climate normalization | C/F/K to Celsius, finite values, humidity bounds | Sensor role assignment and conflicting readings still pending |
| Suggestions | Deterministic climate rules; stable IDs; unknown confidence | Not learned habits; no persistent feedback yet |
| Habitus zones and roles | Logical zones and entity selection implemented | Stable IDs, multiple areas, extras, editor; contextual role priorities deferred |
| Learning and consent | Planned | Attribution, bounded evidence, replay fixtures, consent/export/delete |
| SQLite / migrations | Schema 3 for zones and selections; migration tests pass | Pre-migration backup, shared revisions, export, bounded selection journal; audit/plans remain JSONL |
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

## Current development gate

The reconnect correction previously proven in PR #2 is integrated onto alpha.6.
49 Python and four JavaScript model tests pass locally, plus repository validation,
frontend syntax and Python compilation. Exact-commit CI remains required before
merge. No release or deployment is part of this increment. Next after the reliability
gate: enforce confirmed-only inference and add explicit contextual sensor roles;
only then introduce consented, synthetic-fixture-first habit evidence and feedback.
