# Capability and acceptance ledger

Stand: capability correction 0.1.0-alpha.4. "Local tests" is not live HA acceptance.

| Capability | Code state | Acceptance / remaining work |
|---|---|---|
| Add-on packaging | Implemented | alpha.4 installed and started after app-only backup |
| Ingress routes / peer restriction | Implemented, local HTTP tests | Real browser API responses 200; new alpha.4 visual/asset rendering not yet independently checked |
| HA snapshot and event stream | Implemented; unreleased short-connection backoff fix | Three new synthetic reconnect regressions; 31 tests on reliability branch; live disconnect/load soak pending |
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

## Unreleased reliability gate

The isolated reconnect fix preserves increasing delay after short authenticated
connections and resets only after 60 seconds of subscribed uptime following
successful resynchronization. Idle streams need no sensor events to qualify.
No real HA outage was induced. Version remains alpha.4; do not reinstall it to
test this unversioned development change. Exact-commit CI and integration with the
ongoing PR #1 zone package precede release preparation and app-only recovery checks.

PR #1's synthetic UI browser job passed at `6096783`; that is development evidence,
not a new feature in installed alpha.4 or proof of authenticated live Ingress.
