# PilotSuite continuation context

Canonical repository: `GreenhillEfka/pilotsuite`; app: `0d79c5e8_pilotsuite`.
Continue existing modules and preserve uncommitted work, including untracked
AGENTS.md. Do not recreate functions or redeploy an old ZIP.

Read CURRENT_STATE.md, docs/RELEASE_STATE.json, docs/RELEASE_RUNBOOK.md,
DECISIONS.md, docs/VISION.md and docs/ROADMAP.md before changes.
docs/ARCHITECTURE.md maps owners; docs/ZONE_INSTANCE_V2.md defines presence;
docs/UX_WORKSPACE.md and ADR-043 define the zone-first setup concept.

## Boundaries

- Presence first: continuous/pulse/support differ; unknown is never silently vacant.
- Relevance authorizes live and available history. Write authority is separate.
- Preserve four saved zones and entity cleanup. HA areas do not redefine zones.
- Habituszonen is an ontology/layout reference, not proof of occupancy.
- One app, existing SQLite owners, no second engine or configuration.
- Ingress/authentication/sandbox remain intact. No household test switching.
- General Apply is closed; bounded helper/metadata/publication paths already exist.
  Do not describe presence_adoption_review as universal hard_read_only.
- Implemented, tested, installed and household-accepted are separate states.

The user permits reusing/adopting existing automations. Prefer their inspected
logic over rebuilding it. The earlier comparison-only preference is not a permanent
product prohibition. Structural alignment does not establish equivalent behavior.
Until concrete live-change scope is answered, do not create/rename household helpers,
edit/enable/disable automations, activate outputs, transfer control or grant learning.

## Current continuation

Alpha.72 from PR #153 is installed and healthy, after exact candidate/main CI,
fresh PilotSuite-only backup and one targeted update. CURRENT_STATE.md and
RELEASE_STATE.json own the actual receipt and the narrow backup-list exception.
The user requested “Bitte abschließen”; delivery closure changes no household
bindings, control or learning permissions. The night heartbeat is PAUSED.

The implemented flow covers areas/tags, stable members and roles, explicit metadata
plans, presence/helper autolabeling and the primary-presence light comparison.
Active light actuation, automation takeover and household Ingress acceptance remain
open. Prior version receipts and implementation history remain in Git/ledger.

Next is authenticated read-only Ingress acceptance of Erdkellerbereich and one
unlike zone. No authenticated browser session was available for the release.
Verify actual saved bindings before household import/apply. Synthetic tests and
runtime readiness are not proof of household wiring or safe control handover.
Do not reinstall Alpha.72, reactivate the heartbeat or create extra agents/tasks.
