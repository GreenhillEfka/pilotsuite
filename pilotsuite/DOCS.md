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
- Release: `0.1.0-alpha.6`

## Habitus zones and entity selection

Each Habitus zone has a visible tab. Select a tab to see only that zone's entity
choices, evaluation, suggestions and observations. Use **Name / Bereiche bearbeiten**
to rename it or tick HA-area sources (e.g. Bad and Toilette).

For a new zone: **+ Neue Zone** → name and area checkboxes → **Zone speichern** →
select relevant entities → **Auswahl speichern** → **Auswertung starten**.
The same button pauses an active zone without losing its choices. Save or discard
pending entity edits before switching tabs or starting/pausing. Selection mode is
under advanced settings and is not the zone activation switch. An active zone with
no suitable selected observations is explicitly shown as having no observations.
Neutral zones report observation/data quality; they do not claim learned habits.

Existing `golden_zone_area_ids` are imported once into persistent zones. After that,
use the zone editor for source changes; changing bootstrap options does not replace
stored definitions. Missing sources and temporarily absent entities preserve saved
choices. Export provides a reviewable JSON copy; import is not implemented.

Before updating, create a PilotSuite-only backup. SQLite schema migrations back up
older databases automatically. For downgrade recovery restore the previous App and
its data from the pre-update backup; do not open a newer schema with older code.
