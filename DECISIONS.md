# Architecture Decision Log

## ADR-001 — One canonical repository

**Status:** accepted — 2026-09-22

`GreenhillEfka/pilotsuite` is the only canonical implementation. Earlier PilotSuite, Styx, and Habitus repositories are reference material, not merge targets or runtime dependencies.

## ADR-002 — Add-on-first architecture

**Status:** accepted — 2026-09-22

PilotSuite runs as one Home Assistant Supervisor App. A custom integration may be added later only where native Home Assistant entities or services create concrete value. This avoids coordinating multiple backends during the proving phase.

## ADR-003 — Home Assistant remains source of truth

**Status:** accepted — 2026-09-22

PilotSuite reads registries and states through supported APIs and maintains only a bounded in-memory projection plus PilotSuite-owned metadata. It does not clone the Home Assistant state database.

## ADR-004 — LLM outside the critical path

**Status:** accepted — 2026-09-22

An LLM may explain, summarize, or propose. It cannot bypass policy evaluation or execute Home Assistant actions directly. PilotSuite remains useful without an LLM.

## ADR-005 — One transaction path

**Status:** accepted — 2026-09-22

All future mutations use `plan -> backup -> apply -> verify -> rollback`. Separate ad-hoc action paths are forbidden.

## ADR-006 — Read-only alpha

**Status:** accepted — 2026-09-22

`0.1.0-alpha.1` rejects every apply request in code, regardless of options. This lets the connector, world model, resolver, audit, API, and Golden Zone be validated without changing the house.

## ADR-007 — Erdkeller as Golden Zone

**Status:** accepted — 2026-09-22

The Erdkeller is the first bounded end-to-end scope. Entity selection is derived from Home Assistant area membership, not a hard-coded entity list.

## ADR-008 — No build.yaml

**Status:** accepted — 2026-09-22

The Dockerfile is the single build source according to the Home Assistant 2026 BuildKit migration. The Home Assistant multi-architecture Python base image is pinned.

