# Current State

Last updated: 2026-09-22

## Release

- Version: `0.1.0-alpha.2`
- Architecture: v21
- Stage: experimental alpha
- Mutation mode: hard read-only

## Implemented

- Home Assistant App repository metadata
- Multi-architecture container definition for `amd64` and `aarch64`
- Home Assistant REST and WebSocket connector through the Supervisor proxy
- Registry snapshot for areas, devices, entities, and current states
- In-memory world model; no duplicate Home Assistant database
- Area resolver and configurable Golden Zone
- Deterministic neuron normalization, mood calculation, and suggestion rules
- JSON API and Ingress dashboard
- Append-only audit log in `/data`
- Dry-run plan creation with a hard block on apply
- Liveness/readiness endpoints
- Unit tests and CI validation (14 tests)
- Canonical context, decisions, security, API, install, and roadmap documents

## Verified outside the repository

- GitHub repository is public: `GreenhillEfka/pilotsuite`
- GitHub connection has administrative and push access
- Target Home Assistant Core: `2026.9.3`
- HA-MCP: `8.5.0`
- The obsolete `pilotsuite-styx-core` App Store repository was removed from the
  target Home Assistant.
- Canonical App Store repository registered as `0d79c5e8`.
- PilotSuite `0.1.0-alpha.2` installed and running as
  `0d79c5e8_pilotsuite`.
- `/health/ready` returns HTTP 200 after repeated refresh cycles.
- Home Assistant WebSocket projection is connected with no current error.
- Golden Zone `erdkeller` resolves successfully with 48 projected entities.
- Runtime reports 48 neurons, 8 moods, and 1 deterministic suggestion.
- Live policy verification rejects apply with HTTP 409.
- No Home Assistant configuration was changed during installation or validation.

## Not implemented

- pre-built GHCR images
- service-call execution
- Supervisor backup creation
- automatic verification and rollback
- learning persistence beyond explicit audit records
- LLM provider integration
- native Home Assistant integration/entities

## Next acceptance step

Review the Ingress UI and validate the 48 projected Erdkeller entities and the
first deterministic suggestion against the real room semantics. Do not enable
mutations during this phase.
