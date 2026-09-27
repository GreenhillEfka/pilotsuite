# Work package: static event-filter references

## Goal

Keep the existing automation review internally consistent for Home Assistant event
triggers. If discovery finds an automation because a literal entity is constrained in
`event_data.entity_id`, the structural inspection must recognize the same entity as a
direct source reference instead of reporting a false source gap.

The gap was found during an explicitly authorized read-only inventory of an existing
multi-area zone. No household identifiers or configuration bodies are stored in this
repository; the regression uses synthetic data only.

## Scope

- inspect the literal `entity_id` field of an event trigger's `event_data` object;
- merge that static reference into the existing source-alignment projection;
- keep action event payloads opaque so payload data cannot become a claimed target;
- keep dynamic, templated or malformed filters unknown and privacy-bounded;
- replace the stale packaged candidate banner with a version-only statement whose
  installation status remains owned by `docs/RELEASE_STATE.json`.

## Explicit exclusions

- no recursive template interpretation or arbitrary event-payload semantics;
- no new scanner, store, route, queue, learner or second automation owner;
- no automation repair, import, write, activation or execution approval;
- no zone rename, split or inferred mapping from Home Assistant area names;
- no household fixture or identifier in source control.

## Acceptance criteria

1. A literal event-filter entity that matches a draft source closes only that direct
   source-reference gap.
2. An action's `event_data.entity_id` never becomes an action target.
3. A dynamic event filter stays unresolved, opens review and does not expose its text.
4. The complete Python, JavaScript and repository contract suites remain green on the
   exact candidate and final main source.
5. The actual Alpha.51 publication, scoped backup and installation are recorded only in
   `docs/RELEASE_STATE.json`.

## Next step

Repeat the read-only automation review in authenticated Ingress for the saved
`Erdkellerbereich`, then one unlike saved zone. Confirm all four saved zones and the
corrected event-filter source explanation; do not change household configuration or
Apply authority.
