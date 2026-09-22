# Architecture Decision Log

## ADR-009 — Reviewed target architecture (2026-09-22)

Accepted: one repository, one modular add-on, one semantic owner. An optional
thin HA integration may expose native entities and Conversation; it must not
contain inference, learning, policy, or a second PilotSuite configuration store.
HA owns raw registry/state truth. PilotSuite owns its composed Habitus zones,
roles, policies and preferences, referencing HA identifiers. This intentionally
supersedes the old HA repository's ownership of curated PilotSuite zone storage.
UI ownership is not data ownership; HA UI edits call the canonical owner.

## ADR-010 — Evidence is not preference (2026-09-22)

Severity, data quality, statistical confidence, user preference and action risk
are separate fields. Unknown confidence is null, not a heuristic percentage.
Feedback must not mutate observed event counts. Suggestion identity depends on
versioned rule and normalized scope, never a changing measurement or score.

## ADR-011 — Storage and learning (2026-09-22)

Target: SQLite for PilotSuite-owned zone definitions, bounded learning evidence,
feedback, proposals and transaction journal; schema migrations and retention
required. Existing alpha JSONL remains until a tested migration is implemented.
No full HA history clone, graph database, broker or vector database is required.
The graph is a view of evidence, not a competing source of truth.

## ADR-012 — Action-specific recovery (2026-09-22)

ADR-005 describes the single governed execution path, not universal reversibility.
Every future action declares preconditions, authorization scope/expiry,
idempotency behavior, backup requirements, verification and recovery semantics.
Irreversible effects must be explicit. Configuration files are never blindly
overwritten; additive changes require backup and validation. No alpha actuation.

## ADR-013 — Prove learning early, autonomy late (2026-09-22)

Read-only learning and feedback precede actuation. Test a second unlike zone
before stabilizing the architecture. Use HA Assist and existing device integrations
instead of rebuilding STT/TTS or promising uniform support for every voice device.

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
