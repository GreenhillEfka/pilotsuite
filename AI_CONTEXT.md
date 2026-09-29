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
Latest explicit extension: 29 September 06:43:54–07:43:54 UTC. Existing heartbeat
reused; stop new packages at 07:23:54 and release publication at 07:28:54, pause at
end. `feat/zone-missing-helper` is a non-release development candidate; Alpha.70
remains installed. See CURRENT_STATE for gates and exact handoff. No household write
scope has changed. The following overnight window is historical, not current:
Earlier timed runs are closed. An explicitly authorized overnight development
window runs from 28 September 22:26:57 UTC to 29 September 06:30 UTC
(08:30 Europe/Berlin). The existing heartbeat is active; no extra background jobs.
No new feature package after 05:45 UTC and no new publication after 06:00 UTC.
At 06:30 UTC stop development/release/install, report saved work and pause it.
Prioritize a complete, zone-centered configuration journey: grouped existing
automations, helper reuse/missing-helper plans, understandable presence and actual
HA-owned parameters. No new intelligence. ADR-043 and UX_WORKSPACE.md specify the
concept and bounded sequence. Research primary sources and translate findings into
regressions and code; keep one active package, branch and reviewable PR.
Alpha.70 is installed after PR #149, exact candidate/main CI and verified scoped
backup. PR #148 delivered Alpha.69; PR #147 recorded Alpha.68. Do not repeat installs.
Current work on feat/zone-presence-setup is closing documentation and acceptance
handoff, no new feature package. Safe app releases remain allowed after every
runbook gate; this does not authorize unconfirmed live household edits.
Existing-zone HA-MCP state/history reads did not observe a presence transition and
do not establish Ingress acceptance, saved PilotSuite bindings or safe takeover.
Household and release boundaries remain unchanged.
