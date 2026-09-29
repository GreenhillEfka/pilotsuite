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

Timed overnight and additional-hour runs ended; the existing heartbeat stays paused.
The user subsequently said to continue the existing package directly in this chat.
PR #151 on `feat/zone-missing-helper` is merged and Alpha.71 safely delivered.
No new timed loop, chat or background job. This continuation does not change
household-write scope.

Alpha.70 followed PR #149; PR #150 recorded its delivery. PR #151 delivered
Alpha.71 single Boolean/timer creation through existing transactions, without
assignment or automation wiring. Exact candidate/main CI, scoped backup, installation
and runtime are verified. CURRENT_STATE.md owns fresh progress; the receipt
plus live HA metadata owns installation, never a version marker or old narrative.

Next household acceptance is read-only authenticated Ingress for Erdkellerbereich
and an unlike zone. No authorized browser is currently available. Prior HA-MCP
states/history did not show a transition and do not prove wiring or safe takeover.
Legacy APIs/settings remain readable; require tested migration before removal.
