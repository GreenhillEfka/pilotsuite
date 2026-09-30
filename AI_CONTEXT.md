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

The 30.09.2026 timed Habitus setup assignment ended at 08:00 Europe/Berlin.
The user subsequently requested “weiter”: continue the existing implementation
package directly in this thread. The expired heartbeat is PAUSED; do not revive
it or create another timed loop, chat, agent or checkout.
Use `feat/habitus-zone-setup` / draft PR #153 and `docs/HABITUS_SETUP_PLAN.md`.
Keep progressing through zone/tag setup, presence/helper autolabeling and then
lighting. Climate, multimedia and pattern recognition follow the foundation.
CURRENT_STATE.md owns current progress; PR #153 holds exact candidate CI receipts.
Alpha.72 is developed/tested, while Alpha.71 remains installed. The latest “weiter”
is not the pending narrow backup-agent exception or a household-control handover.
Existing zones, identities and HA control remain intact during development.

Alpha.70 followed PR #149; PR #150 recorded its delivery. PR #151 delivered
Alpha.71 single Boolean/timer creation through existing transactions, without
assignment or automation wiring. Exact candidate/main CI, scoped backup, installation
and runtime are verified. CURRENT_STATE.md owns fresh progress; the receipt
plus live HA metadata owns installation, never a version marker or old narrative.

Next household acceptance is read-only authenticated Ingress for Erdkellerbereich
and an unlike zone. No authorized browser is currently available. Prior HA-MCP
states/history did not show a transition and do not prove wiring or safe takeover.
Legacy APIs/settings remain readable; require tested migration before removal.
