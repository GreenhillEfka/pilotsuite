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
10. The Erdkellerbereich is the first Golden Zone. A second read-only zone must test generality before 1.0; broader actuation remains gated.

## Current package and verified deployment

Alpha.21 was published via PR #47 at `1223f96f45053f7bf3d509bd7ad72c85b9f6cab1`;
app tree `3228fa2b5cae4d0db00dc7646aa6e39bb43b6b77`. Exact release CI `35914643847`
and pre-deployment main CI `35915002481` passed. The release records 192 Python,
nine JavaScript, Chromium and amd64 checks; code tests and live UI acceptance
are different evidence.

**On 2026-09-23 alpha.21 was installed through the normal Store update path.**
The first-class `ha_manage_app(action="check_updates")` refreshed the offer from
alpha.18 to alpha.21 without changed credentials or permissions. Fresh scoped
backup `ae7a3fba` was verified with native `backup/details`; one app update followed.
Supervisor reports alpha.21 installed/offered/started, no update pending. Logs
confirm hard_read_only, ready, connected stream, fresh snapshot and resolved zone.
Do not repeat the completed update or the old denied custom Store bridge.

Authenticated alpha.21 Ingress/temporal/draft/inspection UI and the app's live
`automation/config` capability have not been accepted in this continuation. Do not
invent a browser pass or escalate permissions. Existing alpha.16 user UI acceptance
and reported history diagram rendering remain historical, separate evidence.
No production role/consent, HA configuration, automation, actuator or other app was
changed. Canonical repository/version/app-tree association is not an independent
Store checkout SHA or installed-image attestation.

## Resume workflow

Read `CURRENT_STATE.md`, `docs/IMPLEMENTATION_STATUS.md`, `DECISIONS.md` and
`docs/VISION.md` before working. For release/deployment also read
`docs/RELEASE_STATE.json` and `docs/RELEASE_RUNBOOK.md` (ADR-026). Recheck live state;
resume the recorded next step rather than recreating the project or access routine.
Current-state files are concise snapshots. The complete former release ledgers
are preserved unchanged in `CURRENT_STATE_HISTORY_2026-09-23.md` and
`docs/IMPLEMENTATION_HISTORY_2026-09-23.md`; their old next steps and blockers are
history, not present instructions.

The September 2026 review is the accepted target design, not a claim that every
capability is implemented. Keep source code, successful CI and live Home Assistant
acceptance separate. Old repositories are pinned reference sources, never runtime
dependencies. Do not introduce two learning engines or independently owned zone
stores. Current climate rules are heuristics, not learned habits. Raw history stays
transient unless a separate scoped import is explicitly consented to, using the
existing evidence owner. Missing history is not evidence of absent behavior.
PilotSuite remains read-only and emits no own-action evidence.

## One concrete next development task

Implement user-authored review notes in the existing PlanStore, bound to a routine
draft revision and selected automation configuration fingerprint (ADR-029).
Preserve notes but mark them stale on changes; do not portray an unverified or
unavailable fingerprint as a fresh live check. Add migration, optimistic revision,
restart/persistence, stale-state, input-validation, export and browser tests.

ADR-029 / `docs/AUTOMATION_INSPECTION.md` already provide selected structural
inspection, an open review plan, fingerprint comparison and combined export.
Notes are the next increment, **not implemented yet**. No raw configuration
persistence, new learning collection, HA write, automatic semantic verdict or
execution permission follows from recording a note or checking a review item.

## Conceptual chain

`world/sensors -> neurons -> moods -> synapses -> suggestions -> dialogue/approval -> policy -> transaction -> Home Assistant`

- **Neurons** normalize relevant Home Assistant observations.
- **Moods** are deterministic, explainable context scores; they are not anthropomorphic truth claims.
- **Synapses** connect observations and moods to suggestions.
- **Suggestions** contain evidence, confidence, scope, risk, and a proposed plan.
- **Policies** are the final deterministic gate.
- **Transactions** are the only allowed mutation mechanism.

The pattern workbench derives review briefs from canonical evidence and preference;
a review brief is not an executable action plan. See `docs/PATTERN_WORKBENCH.md`,
`docs/HISTORY_AND_TRENDS.md` and `docs/EVENT_ATTRIBUTION.md`.

## Initial Golden Zone

The Erdkeller scope validates the full read path with a bounded domain: area resolution, sensor quality, temperature/humidity context, risk detection, explainable suggestions, audit, and UI. Entity IDs must be discovered from Home Assistant area membership and never hard-coded.

## Deferred on purpose

- unrestricted autonomous service calls
- direct `.storage` or `configuration.yaml` editing
- a second shadow database of all Home Assistant state
- mandatory local LLM/Ollama/Open WebUI dependency
- generated automations without review, validation, backup, and rollback
- broad multi-room learning before the Golden Zone is accepted
