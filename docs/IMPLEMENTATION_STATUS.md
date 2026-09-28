# PilotSuite capability ledger — Alpha.61 installed

`docs/RELEASE_STATE.json` is the delivery receipt. None of the rows below implies
household acceptance.

Alpha.61 implements existing-control integration: canonical saved Boolean,
timer and public sensor bindings, observed comparison in the primary zone view,
explicit writer/consumer structural review. Existing HA automations remain owners;
no new controller/store, helper creation or automatic consumer migration. Local
unit and synthetic full-app tests pass: 612 Python / 75 JS / 62 contracts, zero
ResourceWarnings on the exact source. PR #132 and exact candidate/main CI passed
all five jobs. Scoped backup, Alpha.61 installation and unchanged options/startup
are verified in RELEASE_STATE.json. Household mapping and Ingress acceptance remain
open; existing automations were not changed. Earlier deliveries are history below.

Alpha.60 installed after PR #129 and exact candidate/main CI: dated publication evidence survives unchanged throttled ticks
without additional HA calls, and is withheld on stale/changed/unknown/conflicting
bases. Four added Python tests and one JS test plus an actual-app synthetic browser
flow pass; 596 Python/74 JS total. Scoped backup, installation and unchanged options
are verified in the receipt; authenticated household acceptance remains open.

Alpha.59 installed after PR #127 and exact candidate/main CI: one strict snapshot-age
predicate shared by readiness, event
evidence and presence, with no zone dependency on the shadow freshness adapter.
Four methods reproduced 17 failing baseline subcases; nine added tests and all
592 Python/73 JS cases pass. Three local browser suites and all 11 exact-CI browser
suites pass. Native backup, installation and unchanged options/startup are verified
in the receipt. Household acceptance remains open.

Alpha.58 installed after PR #125 and exact candidate/main CI: read-first durable
zone bootstrap; five new contention,
concurrency, rollback and preservation tests pass. Synthetic 60-cycle scenarios
reduce write reservations 180 to 60 while preserving all 60 checkpoints; no speed
gain claimed. Test-owned connections now close explicitly. 583 Python/73 JS and
two local browser suites pass. Native scoped backup and unchanged options/startup
are verified in the receipt; authenticated household acceptance remains open.

Alpha.57 is installed after PR #123 and exact candidate/main CI. It hardens the
existing publisher against delayed reads and stream loss, and preserves newer
checkpoints when marking an output conflict. Synthetic red/green regressions,
native backup and startup evidence are recorded separately from household acceptance.

Alpha.56 was delivered after PR #121 and exact candidate/main CI: complete loss of
direct optional coverage yields unknown rather than vacant. Regression tests cover
the pure evaluator, SQLite restart, HTTP projection and invalidation-only publisher
path. Delivery is recorded in RELEASE_STATE.json; household acceptance remains open.

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
| Existing Boolean/timer/public sensor read-only integration | Alpha.61 implemented, tested and installed; canonical organization profile, no takeover; household binding/acceptance pending |
| Static event-filter references | Alpha.51 installed; literal trigger `event_data.entity_id` is recognized while action payloads remain opaque |
| Step availability in automation review | Alpha.52 installed; available, disabled and dynamic/unknown nested references are separate and only available matches confirm alignment |
| Passive reading position | Alpha.53 installed and synthetically tested; authenticated household Ingress acceptance pending |
| Required unknown source in a shared presence group | Alpha.54 installed after red/green regression and exact CI; household validation pending |
| Complete loss of optional direct coverage | Alpha.56 installed after red/green regression, restart/HTTP/publisher tests and exact CI; unknown never silently becomes vacant |
| Publication freshness across awaited I/O | Alpha.57 installed; 13 failing baseline subcases fixed, current publication still works; HA/SQLite are not atomic |
| Zone bootstrap read contention | Alpha.58 installed; existing marker needs no write reservation, concurrent first start still rechecks transactionally; checkpoint writes unchanged |
| Shared strict snapshot freshness | Alpha.59 installed; future/invalid time is not ready or evidence-authorizing, valid age limits preserved, zone time path independent of shadow adapter |
| Dated publication evidence | Alpha.60 installed; unchanged ticks preserve the last readback date for less than 20 seconds only on a still-matching valid basis; GET never renews it |
| Adaptive habit learning | Not implemented |
| Automated browser acceptance | Exact candidate and main source passed complete Chromium flow |
| Live runtime | Alpha.61 started, ready, stream connected, snapshot fresh and zone resolved |
| Four saved PilotSuite zones | No automatic zone/schema migration in Alpha.55–61; not independently read back in an authenticated Ingress session after the update |
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
