# PilotSuite capability ledger — Alpha.55 installed

`docs/RELEASE_STATE.json` is the delivery receipt. None of the rows below implies
household acceptance.

Alpha.56 is a development candidate: complete loss of direct optional coverage
now yields unknown rather than vacant. Regression tests cover the pure evaluator,
SQLite restart, HTTP projection and invalidation-only publisher path. Installed
version and completed delivery remain owned by RELEASE_STATE.json.

PR #118 consolidated the concept without changing app behavior. PR #119 delivered
Alpha.55 with three navigation groups and one primary zone-presence view; exact CI
and installation are recorded in RELEASE_STATE.json. Internal deduplication remains
planned. Older activity/context/history-import APIs still retain
legacy learning flags; the current zone-instance path does not require them.

The pure presence kernel is shared, but Alpha.48 shadow and Alpha.49+ zone-instance
configuration/checkpoints still coexist in ContextStore. They are not yet one
runtime/configuration. See ARCHITECTURE.md and ROADMAP.md for the consolidation path.

| Capability | Actual boundary |
|---|---|
| Three-entry navigation and primary presence view | Alpha.55 implemented, tested and installed; synthetic four-zone/browser evidence, household acceptance pending |
| Typed zone presence configurator | Implemented, tested and installed since Alpha.49/50; household Ingress acceptance pending |
| Relevant live analysis | Implemented without a second learning-consent gate or learner; source combinations and bounded TV/usage hints are synthetic-test evidence, not household approval |
| History visualization | Implemented and tested for bounded recent and requested older windows; available Recorder data is not an exhaustive history import |
| Session presence timeline | Latest 128 changes in memory, not a new durable history |
| Own helper package/publisher | Implemented and tested with receipt-bound restart recovery; installed code exists, but no household output package was applied or accepted; an existing canonical sensor blocks automatic duplicate creation |
| Display name/ontology labels | Preview/apply/readback/restore delivered; physical areas preserved |
| Technical entity-ID rename | Blocked pending complete consumer migration |
| Existing automation/helper takeover | Not implemented |
| Static event-filter references | Alpha.51 installed; literal trigger `event_data.entity_id` is recognized while action payloads remain opaque |
| Step availability in automation review | Alpha.52 installed; available, disabled and dynamic/unknown nested references are separate and only available matches confirm alignment |
| Passive reading position | Alpha.53 installed and synthetically tested; authenticated household Ingress acceptance pending |
| Required unknown source in a shared presence group | Alpha.54 installed after red/green regression and exact CI; household validation pending |
| Adaptive habit learning | Not implemented |
| Automated browser acceptance | Exact candidate and main source passed complete Chromium flow |
| Live runtime | Alpha.55 started, ready, stream connected, snapshot fresh and zone resolved |
| Four saved PilotSuite zones | No zone/schema migration in Alpha.55; not independently read back in an authenticated Ingress session after the update |
| Authenticated household Ingress | Still pending; access protection was not weakened |

The general legacy Apply boundary remains closed. `presence_adoption_review` is a bounded
review mode, not a general execution grant. No household configuration change was used to
prove this delivery.

The existing Habituszonen dashboard is an ontology and layout reference. Some of its
templates label every state other than `on` as `Ruhezustand`; that presentation must
not be used as proof that `unknown` or `unavailable` means vacant. Its configuration
was not changed.

Next: perform authenticated read-only acceptance of `Erdkellerbereich` and one unlike
existing zone, including all four saved zones, unsaved UI input across refresh and
the distinct active/disabled/unknown reference explanations. An internal HTTP response
is not substituted for the remaining Ingress observation.
