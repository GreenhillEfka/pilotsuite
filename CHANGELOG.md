# Changelog

All notable changes follow [Semantic Versioning](https://semver.org/).

## [0.1.0-alpha.3] - 2026-09-22

### Fixed
- Route repeated Ingress slashes internally without losing the external prefix.
  Omitting the default ingress_entry alone was not a proven fix.
- Normalize climate units and reject invalid readings; missing climate data is not stable.
- Separate severity from unknown confidence; keep proposal identity stable.
- Track event stream health, resynchronize after reconnect and back off on clean close.
- Reject older state updates and exclude disabled entities from the projection.

### Security
- Restrict UI/API to the Ingress TCP peer; allow loopback liveness probes only.
- Home Assistant mutations remain hard-disabled.

### Added
- Reviewed full vision, capability/acceptance ledger and revised learning-first roadmap.
- Regression tests and periodic dashboard refresh.
- Real Supervisor/browser acceptance is still pending.

## [0.1.0-alpha.2] - 2026-09-22

### Fixed

- Raised the bounded Home Assistant WebSocket receive limit to 32 MiB so larger
  state and registry snapshots do not close the connection at `aiohttp`'s
  4 MiB default.
- Report the actual WebSocket message type and transport error when a snapshot
  connection fails.

## [0.1.0-alpha.1] - 2026-09-22

### Added

- Canonical PilotSuite v21 repository and project memory
- Installable Home Assistant Supervisor App skeleton
- REST/WebSocket Home Assistant connector
- Registry-backed world model and area resolver
- Erdkeller Golden Zone configuration
- Deterministic neurons, moods, synapses, and suggestions
- Read-only policy gate and dry-run plans
- Ingress dashboard, API, audit trail, tests, and CI

### Security

- Hard-disabled Home Assistant mutations for the complete alpha release
- No Home Assistant config mounts, host networking, privileged capabilities, or secret persistence
