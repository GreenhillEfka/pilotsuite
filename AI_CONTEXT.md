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

## Current package

Alpha.19 candidate implements user-approved durable routine drafts (ADR-027,
docs/ROUTINE_DRAFTS.md). Existing PlanStore owns CRUD/revisions; shared SQLite schema
7 backs up before migration. No copied evidence or execution. Statistics, confidence,
rule strength, risk and preference stay separate. Automation comparison and risk
remain unassessed. Baseline main ae21e54 / CI 35898937373 is green.

HA freshly runs/offers alpha.18; release f3f5a25 / CI 35880705662. User confirmation
of availability is not temporal UI acceptance. Fresh scoped backup 14e86f1c holds
alpha.18 app/data/options before publishing alpha.19. Candidate CI/deployment pending.
Next: exact CI and release routine; then read-only existing-automation comparison.
Authenticated temporal/draft UI and real learning-quality/second-zone gates remain
separate. Alpha.16 guide/navigation/workbench user acceptance is preserved.

For release/deployment read docs/RELEASE_STATE.json, newest CURRENT_STATE receipt and
docs/RELEASE_RUNBOOK.md. Resume the recorded next step after live checks; do not
rediscover the procedure or treat historical blockers as current.

## Continue here — architecture review implementation

Read `docs/VISION.md`, `docs/IMPLEMENTATION_STATUS.md`, `DECISIONS.md`, and
`CURRENT_STATE.md` before working. Do not restart or recreate the project.
For every release or deployment also follow `docs/RELEASE_RUNBOOK.md` (ADR-026).
It preserves the verified scoped backup route and known Store access boundary;
do not rediscover alternate deployment paths or reuse a published version for fixes.
The September 2026 review is accepted as the target design, not a claim that
all capabilities are implemented. Keep source code, passing tests, and live
Home Assistant acceptance as three separate kinds of evidence.
Old repositories are pinned reference sources, never runtime dependencies.
Do not reintroduce two learning engines or independently owned zone stores.
Current alpha rules are climate heuristics, not learned habits.

Alpha.14 adds the pattern workbench on top of targeted transient HA
history/statistics views and the existing consented evidence owner. Do not copy
Recorder data or infer missing history as absence of behavior. The immediate live
continuation is alpha.17 temporal-view/export acceptance, after user acceptance of alpha.16.
Alpha.18 is installed and started; newest pre-alpha.19 recovery point is 14e86f1c. Native backup/details
works; the old permission-gate receipt is superseded. Source association uses the
canonical release and unchanged app tree, not an exposed Store checkout SHA.
Reliability corrections may continue as separate
small changes, but must not be represented as deployed. PilotSuite remains
read-only and emits no own-action evidence. See `docs/HISTORY_AND_TRENDS.md`,
`docs/EVENT_ATTRIBUTION.md` and `docs/PATTERN_WORKBENCH.md`.

## Conceptual chain

The user confirmed history diagram rendering on 2026-09-23. Recorder coverage is
still separate. The pattern-workbench candidate derives review briefs from canonical
evidence and preference; it is not an execution plan. See docs/PATTERN_WORKBENCH.md.

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
