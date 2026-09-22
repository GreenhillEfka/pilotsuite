# PilotSuite AI Context

This file is the canonical long-term context for humans and AI contributors. If a chat statement conflicts with this repository, the repository is authoritative until an explicit architecture decision changes it.

## Identity

- Repository: `GreenhillEfka/pilotsuite`
- Product: PilotSuite
- Architecture generation: v21
- Versioning: Semantic Versioning, beginning with `0.1.0-alpha.1`
- Primary platform: Home Assistant OS / Supervisor Apps
- Canonical language for code and identifiers: English
- User-facing documentation: German or bilingual where useful

## Non-negotiable rules

1. Home Assistant is the source of truth for devices, entities, areas, labels, and live states.
2. PilotSuite never mirrors the complete Home Assistant database.
3. An LLM is optional and is never part of the critical control path.
4. Deterministic rules and explicit policies decide whether a proposed action is permissible.
5. Mutations use one path only: plan, backup, apply, verify, rollback.
6. Read-only is the default. Autonomy must be bounded, time-limited, visible, revocable, and audited.
7. No Home Assistant configuration file is overwritten. Future file changes must be additive, backed up first, validated, and reversible.
8. Secrets and Supervisor tokens are never logged or stored by PilotSuite.
9. Every material decision is recorded in `DECISIONS.md`; every actual implementation state is recorded in `CURRENT_STATE.md`.
10. The Erdkeller is the first Golden Zone. Expansion happens only after its acceptance criteria pass.

## Conceptual chain

`world/sensors -> neurons -> moods -> synapses -> suggestions -> dialogue/approval -> policy -> transaction -> Home Assistant`

- **Neurons** normalize relevant Home Assistant observations.
- **Moods** are deterministic, explainable context scores; they are not anthropomorphic truth claims.
- **Synapses** connect observations and moods to suggestions.
- **Suggestions** contain evidence, confidence, scope, risk, and a proposed plan.
- **Policies** are the final deterministic gate.
- **Transactions** are the only allowed mutation mechanism.

## Initial Golden Zone

The Erdkeller scope validates the full read path with a bounded domain: area resolution, sensor quality, temperature/humidity context, risk detection, explainable suggestions, audit, and UI. Entity IDs must be discovered from Home Assistant area membership and never hard-coded.

## Deferred on purpose

- unrestricted autonomous service calls
- direct `.storage` or `configuration.yaml` editing
- a second shadow database of all Home Assistant state
- mandatory local LLM/Ollama/Open WebUI dependency
- generated automations without review, validation, backup, and rollback
- broad multi-room learning before the Golden Zone is accepted

