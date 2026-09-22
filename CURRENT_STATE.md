# Current State

## alpha.8 corrective release candidate

alpha.7 merged as 5c25bc2 after CI 35793455952 (58 backend, 4 JS, browser,
amd64 build) and installed after confirmed alpha.6 backup 89e963d5. Real startup
failed with NameError _context_get: the module entrypoint ran before appended
handler definitions. This was not covered by module-import tests. Failure occurred
before app startup callbacks and therefore before schema migration.

alpha.8 moves the entrypoint below all handlers and adds an actual subprocess
startup/HTTP regression. It retains the full confirmed-selection, plural-role and
opt-in-learning package. Runtime recovery must be verified before claiming success.


Last updated: 2026-09-23

## alpha.7 candidate — confirmed selection, role groups and activity learning

Implemented contract: docs/OBSERVATION_LEARNING.md and ADR-017. Includes strict
selection, compact summaries, plural roles, explicit consent, bounded live evidence,
stable pattern candidates and independent persistent feedback, export and reset.
58 backend tests and four JS tests pass locally. Browser and container CI must pass
before installation. alpha.6 remains the deployed baseline until backup/update.
No learning is enabled by deployment; the user grants consent per zone in the UI.
The user confirmed Badbereich activation in alpha.6. Do not re-create existing zones.




## Reliability integration included in alpha.7 — reconnect backoff

The isolated, CI-proven reconnect correction from PR #2 is now applied to the
current alpha.6 zone code rather than the superseded alpha.4 base. Repeated short,
authenticated Home Assistant streams retain the bounded 1/2/4/8/16/30-second
backoff. A subscribed stream resets it only after 60 seconds of uptime, including
quiet installations with no state events. Authentication failures never report a
connected stream.

All 49 Python tests and four JavaScript model tests pass locally, including the
three synthetic reconnect regressions and the existing zone/selection suite.
Candidate 636c5a7 passed CI 35792464489 (tests, browser, amd64 container). PR #4 merged as aac362a with the same tree; PR #2 is superseded. PR #5 records this proof. These reliability changes are retained in the alpha.7 candidate.

## Released and installed: alpha.6 zone tabs and direct activation

PR #3 merged at 290ef423b0072a60d3239fb9992b72008677b470. Candidate
9d3b8097c5456284867f15b89d4a15c11f85fe6b passed CI 35790792191: backend,
browser (including activation, rename, pause, conflict and tab isolation), amd64 image.
The merge tree matches the tested candidate. Pre-update app-only backup dc8bd58c
is confirmed in the HA listing. Update completed; Supervisor reports alpha.6 started.
Runtime logs confirm hard_read_only, ready=True, stream=True, snapshot_fresh=True,
zone_resolved=True. The user subsequently confirmed that Badbereich could be
activated through the actual alpha.6 Ingress UI. This is direct workflow acceptance,
not a disconnect/load soak or a claim that every visual/asset path was inspected.
Fresh Safari calls through actual Ingress returned HTTP 200 for status, moods,
suggestions, Golden Zone and zone APIs, as recorded by PR #5.

An earlier activation attempt produced selection PATCH calls but no zone-definition
activation PATCH, exposing the confusing dual-control UI fixed in alpha.6. The later
successful user activation closes that specific workflow defect. Direct MCP reads
remain blocked by the Ingress peer guard.

Implemented: visible zone tabs; direct name/source editor and start/pause action;
area checkboxes; scoped moods, suggestions and observations. Selection mode moves
to advanced settings. Activation fetches the shared revision after selection saves.
46 backend and four JS model tests pass locally; extended CI browser regression passed.
alpha.6 is now deployed after scoped backup and update.
No existing zone choices or HA assignments are changed by deployment.


## Historical alpha.5 release evidence

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

1. Require complete alpha.7 CI, including integrated reconnect regressions.
2. Release a new version only after version/source identity, an app-only backup and
   targeted downgrade path are verified; then perform startup/readiness/log checks.
3. Verify role groups, opt-in learning and saved choices in actual HA Ingress; observe real activity before claiming a learned routine.

Contextual role priorities, import, permanent deletion, habit learning, voice,
native entities and the runtime actuation/rollback engine are not implemented.
Existing rules are deterministic climate heuristics, not learned habits.
The canonical repository remains GreenhillEfka/pilotsuite; do not restart the project.
