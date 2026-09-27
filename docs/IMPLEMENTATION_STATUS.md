# PilotSuite capability ledger — Alpha.54 installed

`docs/RELEASE_STATE.json` is the delivery receipt. None of the rows below implies
household acceptance.

The 2026-09-28 concept consolidation changes documentation only. Its simplified
navigation, unified everyday presence view and internal deduplication are planned,
not installed features. Older activity/context/history-import APIs still retain
legacy learning flags; the current zone-instance path does not require them.

The pure presence kernel is shared, but Alpha.48 shadow and Alpha.49+ zone-instance
configuration/checkpoints still coexist in ContextStore. They are not yet one
runtime/configuration. See ARCHITECTURE.md and ROADMAP.md for the consolidation path.

| Capability | Actual boundary |
|---|---|
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
| Live runtime | Alpha.54 started, ready, stream connected, snapshot fresh and zone resolved |
| Four saved PilotSuite zones | Documented as preserved across updates; not independently read back in an authenticated Ingress session after Alpha.54 |
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
