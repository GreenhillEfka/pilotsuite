# Current State

Last updated: 2026-09-22

## alpha.6 release candidate: zone tabs and direct activation

The user reports Badbereich cannot be activated. HA logs show successful selection
PATCH calls for the new zone but no corresponding zone-definition activation PATCH
in the inspected window. This supports a confusing dual-control UI; it does not prove
a server-side rejection. Direct MCP reads remain blocked by the Ingress peer guard.

Implemented: visible zone tabs; direct name/source editor and start/pause action;
area checkboxes; scoped moods, suggestions and observations. Selection mode moves
to advanced settings. Activation fetches the shared revision after selection saves.
46 backend and four JS model tests pass locally; extended CI browser regression
must pass before release. alpha.5 remains deployed until scoped backup and update.
No existing zone choices or HA assignments are changed by deployment.


## Released and installed: 0.1.0-alpha.5

- PR #1 merged; release commit e94991af088a4ea1886d40ab020c3919535f8f8f.
- Release candidate b631f1cb9db0e65e91a4e7f2a5fb30c3de745080 passed CI run
  35787425872: backend/contracts, browser including mobile zone creation, amd64 build.
- Merge tree matches the tested candidate tree exactly (20edababa91113a44ea4dc6fe772fe8ee1cf3faa).
- 46 Python tests and four JavaScript model tests passed locally.
- PilotSuite-only pre-update backup ec38dcca created and confirmed in HA backup listing.
  Home Assistant settings/database and unrelated Apps were excluded.
- App Store refreshed; update completed for 0d79c5e8_pilotsuite.
- Supervisor confirms version 0.1.0-alpha.5 and state started; options preserved.
- Runtime log confirms version alpha.5, hard_read_only, ready=True, stream=True,
  snapshot_fresh=True and zone_resolved=True after startup.
- Temperature, motion, presence, light and illuminance available; humidity not_present.
- No unrelated HA configuration, automations or actuators changed.

## Implemented

Logical Habitus zones have stable IDs, mutable names, multiple HA-area sources and
extra entity candidates. The Ingress editor supports creating, editing and pausing
zones. Relevant/ignored/unreviewed selection persists in SQLite schema 3 with
pre-migration backups, shared revision conflict protection, JSON export and a journal
bounded to 5,000 transactions. Existing configured zones bootstrap once; new UI zones
start paused with a neutral profile and curated selection. Inference is per zone;
global entity counts deduplicate IDs. Contract: docs/HABITUS_ZONES.md and ADR-015.

Readiness is separate from domain completeness. Ingress TCP-peer restriction,
climate normalization, unknown values, stable proposal IDs, event reconnect/resync
and hard-disabled HA mutations remain in effect.

## Live acceptance limits

Startup and transport readiness are verified for alpha.5. Interactive creation,
selection save/reload and export through the user's actual HA Ingress session are
not yet independently verified for this release. CI browser tests are separate
evidence. Historical alpha.4 browser API HTTP 200 is not alpha.5 UI acceptance.
The MCP proxy's earlier 403 comes from the Ingress peer guard; do not bypass it.
Physical sensor freshness, contextual sensor roles and disconnect/load soak remain open.

For app downgrade recovery use the pre-update App-and-data backup ec38dcca; do not
feed a newer SQLite schema to older code. A recovery restore was not performed.

## Next

1. Verify alpha.5 zone editor, persisted selection and export in actual HA Ingress.
2. Review Erdkeller entity choices and a second unlike zone.
3. Follow docs/IMPLEMENTATION_STATUS.md and docs/ROADMAP.md for consented read-only
   learning, bounded evidence and durable proposal feedback.

Contextual role priorities, import, permanent deletion, habit learning, voice,
native entities and the runtime actuation/rollback engine are not implemented.
Existing rules are deterministic climate heuristics, not learned habits.
The canonical repository remains GreenhillEfka/pilotsuite; do not restart the project.
