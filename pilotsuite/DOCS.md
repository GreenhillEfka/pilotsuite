# PilotSuite configuration

## Options

| Option | Default | Meaning |
|---|---:|---|
| `log_level` | `info` | Runtime log level; secrets are redacted regardless |
| `golden_zone_area_ids` | `[erdkeller]` | Exact Home Assistant area IDs included in the first proving scope |
| `refresh_interval_seconds` | `30` | Full snapshot reconciliation interval |
| `audit_retention` | `5000` | Maximum retained PilotSuite audit events |

This release is always read-only. There is intentionally no option that can enable Home Assistant mutations.

## First start

After starting, open the Web UI and confirm:

- Home Assistant connector: connected
- World snapshot: areas, entities, and states present
- Golden Zone: resolves the Erdkeller area ID
- Policy mode: hard read-only
- Release: `0.1.0-alpha.2`

If the Golden Zone does not resolve, obtain the exact area ID from Home Assistant and update `golden_zone_area_ids`. Display names are not treated as IDs because translations and renames would make them unstable.
