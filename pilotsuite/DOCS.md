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
- Release: `0.1.0-alpha.5`

## Habitus zones and entity selection

Open the zone editor to create or edit logical zones. Select one or more HA areas
as candidate sources and optionally add entity IDs. New zones start paused with a
neutral observation profile. Confirm relevant entities, save, and activate the zone
when ready. Relevance never grants actuator permission. Ignored and unreviewed
entities are excluded when curated selection is active.

Existing `golden_zone_area_ids` are imported once into persistent zones. After that,
use the zone editor for source changes; changing bootstrap options does not replace
stored definitions. Missing sources and temporarily absent entities preserve saved
choices. Export provides a reviewable JSON copy; import is not implemented.

Before updating, create a PilotSuite-only backup. SQLite schema migrations back up
older databases automatically. For downgrade recovery restore the previous App and
its data from the pre-update backup; do not open a newer schema with older code.
