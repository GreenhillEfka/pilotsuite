# Work package — structural step availability

## Goal

Prevent a disabled or dynamically enabled trigger/action from being presented as a
confirmed direct source or target match in the existing automation detail review.
The review must keep the reference visible while preserving the distinction between
structural availability and the unobserved runtime state of the whole automation.

The defect was found while checking the completeness of the Alpha.51 reference path:
`disabled_step` and `dynamic_enablement` were reported as limitations, but their
references still closed `source_gap` or `target_gap`. A disabled parent could also
leave nested actions looking active.

## Scope

- derive `available`, `unavailable` or `unknown` for each inspected step;
- inherit unavailable/unknown status through nested condition/action/wait branches;
- use only structurally available trigger/service-call references for confirmed
  alignment, while returning unavailable and unknown matches separately;
- keep gaps open when their only match is unavailable or unknown;
- use the same confirmed projection in the existing presence-adoption analysis;
- explain the distinction in the existing mobile/desktop review UI;
- preserve transient, sanitized, revision-bound and non-executable behavior.

## Excluded changes

- no assertion about the live enabled state of the complete HA automation;
- no automation edit, enable/disable operation, repair, import or service call;
- no new store, queue, learner, consent, preference or execution permission;
- no household identifiers or automation configuration in source/tests;
- no substitution for authenticated household Ingress acceptance.

## Acceptance criteria

1. Disabled and dynamically enabled matching triggers/actions remain visible but do
   not appear in confirmed source/target alignment.
2. A disabled parent makes nested matching children unavailable; an independent
   available sibling can still confirm the same reference.
3. Source/target gaps stay open when no structurally available match exists.
4. Presence-adoption classification consumes the confirmed projection and remains
   non-executable; older synthetic inspection shapes stay compatible.
5. Unit, API/integration and Chromium fixtures cover the behavior without household
   data or mutations.

## Next step

After exact candidate CI and backup-bound delivery, inspect the saved
`Erdkellerbereich` in authenticated read-only Ingress and compare one unlike saved
zone. Confirm all four saved zones plus the distinct active, disabled and unknown
reference explanations without applying a household change.
