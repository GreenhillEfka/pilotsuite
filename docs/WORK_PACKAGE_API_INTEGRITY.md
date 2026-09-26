# Work package: API contract integrity

## Goal

Make the current PilotSuite interface discoverable and prevent implementation and
documentation from silently drifting apart. The package replaces the historic partial
endpoint list with the complete registered `/api/v1` surface and records the important
effect boundary for every route group.

## Scope

- inventory all registered `/api/v1` method/path pairs from the actual application;
- group the 48 contracts by runtime, zones, learning, foundations, drafts, reviews,
  organization, maintenance and legacy dry-run plans;
- explain read-only inspections separately from explicit persistent or apply operations;
- correct the legacy transaction parameter from `{id}` to `{plan_id}`;
- retain the existing privacy, readiness, evidence and consent semantics;
- fail regression tests when a route is added, removed or renamed without updating
  the canonical API inventory.

## Explicit exclusions

- no new endpoint or payload field;
- no change to Home Assistant access, Ingress, options or runtime behavior;
- no version bump, app publication, backup, Store update or restart;
- no household read, write, learning consent or execution;
- no OpenAPI generator or second contract owner.

`aiohttp` route registration remains the executable owner. `docs/API.md` is the human
inventory, and one test compares its unique method/path set against that owner.

## Acceptance criteria

1. Every non-`HEAD` registered `/api/v1` method/path appears exactly once in
   `docs/API.md`.
2. No documented `/api/v1` method/path lacks a registered route.
3. The inventory identifies which apparently similar operations inspect, preview,
   persist, restore or apply.
4. Existing Python and JavaScript suites remain green; CI remains the final evidence.
5. The installed Alpha.35 receipt remains unchanged because the application tree is
   unchanged.

## Next step

Use an authenticated Home Assistant Ingress session for the explicit read-only
cumulative inventory scan in the saved Erdkellerbereich zone; then repeat against the
other three saved zones. Do not infer zone IDs, replacements or household intent.
