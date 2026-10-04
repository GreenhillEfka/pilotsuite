# PilotSuite continuation context

Canonical repository: `GreenhillEfka/pilotsuite`; app:
`0d79c5e8_pilotsuite`. Continue existing modules and preserve uncommitted work,
including the untracked `AGENTS.md`. Read `CURRENT_STATE.md`,
`docs/RELEASE_STATE.json`, `docs/RELEASE_RUNBOOK.md`, `DECISIONS.md`,
`docs/VISION.md`, `docs/ROADMAP.md` and zone/architecture contracts before changes.

## Boundaries

- Presence first: continuous/pulse/support differ; unknown is never silently vacant.
- Relevance authorizes live and available history; write authority is separate.
- HA areas do not redefine zones. Six public HA anchors and six PilotSuite zones
  were observed on 04 October; this is a snapshot, never a product limit.
- Habituszonen is an ontology/layout reference, not proof of occupancy.
- One app, existing SQLite owners, no second engine or configuration.
- Ingress, authentication and sandbox remain intact; no household test switching.
- General Apply is closed; bounded helper/metadata/publication paths already exist.
  `presence_adoption_review` is not universal hard read-only.
- Implemented, tested, installed and household-accepted are separate states.

The user permits reusing/adopting inspected existing automations. Structural
alignment alone does not establish equivalent behavior. Do not create/rename
household helpers, edit/enable/disable automations, activate outputs, transfer
control or grant learning just from a structural link.

## Current continuation

Alpha.76 from PR #160 is installed, started, ready, stream-connected and fresh.
Its versioned frontend assets were checked in authenticated Ingress after a
mixed-cache failure in Alpha.75. Its four app options stayed unchanged. Current
readiness reports a resolved zone after the Wohnbereich mapping correction.
`CURRENT_STATE.md` and `docs/RELEASE_STATE.json` own the source, CI and scoped
backup receipt; the narrow user-approved Synology backup-list exception remains
defined in the release runbook. The night heartbeat stays paused.

The visible product is still reduced to creating, displaying and documenting
Habituszonen. Preserve existing runtime stores and execution gates; hiding
modules is not evidence that background work stopped. Six current HA zones have
HA-owned light groups and positive opt-ins; Bad, Gang, Koch and Wohnbereich have
optional native Sonos Sound-Cloud presence coupling. PilotSuite documents these
relations by stable identity and does not own their execution. A cross-zone
Light-Cloud is not established by the current groups.

Authenticated structural adoption saved/read back Erdkellerbereich,
Gangbereich, Wohnbereich and Eingangsbereich with curated members and read-only
HA links. Only Eingangsbereich currently matches HA structure without deviations.
Kochbereich has an old replaced member identity; Badbereich's HA label has 858
members. Alpha.77 locally develops revision-bound link-only saving and a
labelled area subset for these cases. Neither path is released or household-
accepted yet. Do not silently migrate stale identities or bulk accept disabled
label members. Active light/media actuation, presence/control takeover and
physical household acceptance remain deferred. Re-read live registries before
further association. Do not restart the heartbeat or create extra agents/tasks.
