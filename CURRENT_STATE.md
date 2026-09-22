# Current State

Last updated: 2026-09-22

## Release

- Version: `0.1.0-alpha.1`
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
- Unit tests and CI validation
- Canonical context, decisions, security, API, install, and roadmap documents

## Verified outside the repository

- GitHub repository exists and is private: `GreenhillEfka/pilotsuite`
- GitHub connection has administrative and push access
- Target Home Assistant Core: `2026.9.3`
- HA-MCP: `8.5.0`
- No Home Assistant configuration was changed while creating this project

## Not implemented

- installation on the target Home Assistant
- pre-built GHCR images
- service-call execution
- Supervisor backup creation
- automatic verification and rollback
- learning persistence beyond explicit audit records
- LLM provider integration
- native Home Assistant integration/entities

## Next acceptance step

Install the app from the repository, start it, and verify `/health`, `/api/v1/status`, the Ingress UI, Home Assistant connectivity, and Erdkeller area resolution. Do not enable mutations during this phase.

