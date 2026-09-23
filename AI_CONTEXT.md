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

Alpha.20 is published via PR #45 at 8be431a133d9694977193947c45de570b280edb6;
app tree 12f06b6c99fd3df9fdd5b9f28e11c6420ac21833, exact main CI 35909475569 green
(175 Python, nine JS, Chromium, amd64). ADR-028 / docs/AUTOMATION_REVIEW.md define
the bounded transient check: saved targets/current pattern sources, HA search/related,
separate source/target matches. No semantic duplicate/safety verdict, persisted
automation data, new collection/schema or execution. Empty matches retain warnings.

HA still runs/offers alpha.18; no update performed. Fresh verified scoped backup
c8347e4a contains alpha.18 app/data/options. Next delivery: exact source/backup
recheck and one normal Store update when alpha.20 is offered, then runtime and
authenticated temporal/draft/reference UI acceptance. Only about:blank is available;
alpha.16 user UI acceptance stands. No real automation scan/learning was performed.
Next concept: inspect one explicitly selected matching automation's trigger/condition/
action references read-only; templates/unsupported semantics remain unknown.

For release/deployment read docs/RELEASE_STATE.json, newest CURRENT_STATE receipt and
docs/RELEASE_RUNBOOK.md. Resume recorded next steps after live checks; do not
rediscover the routine or treat historical blockers as current.

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
Alpha.18 is installed and started; newest pre-alpha.20 recovery point is c8347e4a. Native backup/details
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
