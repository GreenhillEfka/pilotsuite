# Work package: cumulative inventory integrity

## User outcome

An explicit package scan remains bounded, but the user can assess the complete result
of the current session instead of losing older packages. Missing reads remain visible
alongside structural entity-reference and trigger-ID findings.

## Included

- browser-only accumulation bound to the loaded zone and revision;
- requested/total, readable/unreadable and finding-category counts;
- deterministic filters and ordering;
- retained unsaved function assignments and replacement choices;
- clear empty states and responsive, keyboard-native controls;
- synthetic full-app regression across two packages and one unreadable configuration.

## Excluded

- background or automatic scanning;
- a persistent queue, second inventory store or household telemetry;
- inferred replacements, configuration edits, repair execution or actuator calls;
- behavioral/safety proof, dynamic dependency completeness or Ingress authentication.

## Acceptance

1. One explicit action reads no more than eight configurations.
2. A later package adds to, rather than replaces, the current session.
3. Progress includes unreadable configurations without treating them as clean.
4. Filtering is presentation-only and preserves explicit replacement choices.
5. Zone/revision changes and invalidation discard results; late responses stay rejected.
6. Existing drafts, plan boundaries, general Apply gate and HA state remain unchanged.
