# PilotSuite continuation context

Canonical repository: `GreenhillEfka/pilotsuite`; app: `0d79c5e8_pilotsuite`.
Continue existing modules and preserve uncommitted work. Do not recreate earlier
features or redeploy an old ZIP.

Before changes read CURRENT_STATE.md, docs/RELEASE_STATE.json,
docs/RELEASE_RUNBOOK.md, DECISIONS.md, docs/VISION.md and docs/ROADMAP.md.
docs/ARCHITECTURE.md maps actual owners; docs/ZONE_INSTANCE_V2.md defines presence.

## Non-negotiable boundaries

- Presence first: continuous/pulse/support differ; unknown is never silently vacant.
- Relevance authorizes live and available history. Write authority is separate.
- Preserve all four saved zones and entity cleanup. HA areas do not redefine a zone.
- Habituszonen is an ontology/layout reference, not proof of occupancy.
- One app, existing SQLite owners, no second engine or configuration.
- Ingress/authentication/sandbox remain intact. No household test switching.
- General Apply is closed; bounded helper/metadata/publication paths already exist.
  Do not describe the current review mode as universal hard_read_only.
- Release source, tests, installation and household acceptance are distinct.

PR #118 replaced stale entry documentation with a zone-first consolidation plan.
Alpha.55 implements its navigation/primary presence view in the existing frontend.
Use the receipt for delivery, never a version marker alone. Existing legacy
analysis and shadow contracts remain readable; a tested migration is required
before removing their settings or endpoints. AGENTS.md, when present, is preserved.

Use CURRENT_STATE.md for the next task. Use the release receipt plus a fresh HA
metadata read for installation, never an old narrative version claim.

The latest user correction explicitly permits reusing/adopting existing automations.
Prefer existing logic over rebuilding it. Alpha.61 bindings/comparison and the
existing inspector are the starting point; the earlier comparison-only preference
is not a permanent product prohibition. Current runtime still leaves HA automations
in control. Structural alignment never establishes safe/equivalent behavior.
Until the pending live-change scope is answered, develop/test adoption review but
do not edit, enable or disable household automations or transfer control. A future
write needs concrete reviewed changes, fresh preconditions, backup and recovery.
Earlier timed runs and the explicit completion of PR #144 are closed. The new
user request "Eine Stunde Bedienung und Oberfläche intuitiver gestalten" authorizes
one focused UI run on 28 September, 19:33:18–20:33:18 UTC. No new package or release
starts after 20:13:18 UTC. Reused heartbeat only; do not extend the window.
Household and release boundaries remain unchanged.
