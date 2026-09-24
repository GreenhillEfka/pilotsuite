# Prüfkompass – vorhandene Routinen verständlich weiterprüfen

Alpha.23 was published through merged PR #52; exact candidate and release-main CI
passed. Installation is unverified. See CURRENT_STATE.md and
RELEASE_STATE.json.pending_release for the independent publication/preparation
receipt. No duplicate implementation or new version is needed to finish delivery.

## Product and ownership

A routine draft now contains a derived `review_compass` object. The canonical
PlanStore supplies draft, notes, current zone inventory and retained-evidence report
from its existing transaction. `core/review_compass.py` is a pure projection with
no database, network, clock, learner, approval engine or second source of truth.
No new schema/migration, endpoint for mutation, background scanner or queue store.
The existing ContextStore retention behavior is unchanged: GET can retain its
existing expiry housekeeping, but never saves draft text, notes, assessments,
consents, parameters, automation comparisons or actions merely by viewing them.

## Five independent questions

| Section | Basis and limits |
|---|---|
| Sources | Saved complete presence group, confirmed inventory and readable on/off projection. No physical freshness or continuous reachability guarantee. |
| Evidence | Same local window, day group, timezone, counts and existing chronological 70/30 reobservation. Zone coverage remains explicitly zone-wide. Missing later evidence is not absent behavior; repetition is neither prediction accuracy nor user preference. |
| Intent | Explicit goal, trigger, conditions, manual override and selected confirmed targets. Text is a description, not proof of actual behavior. |
| Automations | Only the existing explicitly requested bounded reference review or selected structural inspection. Empty matches never prove conflict freedom. |
| Notes | Authored disposition counts separately from stale, not-rechecked, changed-config and matches-last-read counts. Shared notes do not establish personal identity or action permission. |

States are missing, stale, partial, observed, unknown, described, limited and
last_read. There is no global score or all-green release/approval state. Facts
carry their scope and limitations. The canonical evidence, confidence, preference,
risk and execution fields are not rewritten.

## Basis and transient comparison

Schema `pilotsuite-review-compass-v1` binds zone/draft identities, source/draft/zone/
review revisions, complete source/target sets and the existing scope fingerprint.
GET yields `comparison_checked_at=null`; it never contacts HA configuration APIs.
Existing explicit comparison/inspection returns server-derived last-two sections
in the same response, after the existing post-network revision/scope checks.
The note-save path enriches those sections only after the existing atomic save
and thirty-second inspection-age guard succeeds, with the newly saved revision.

The browser combines only matching server sections. It takes sources, evidence
and intent from the latest GET, never an older comparison. It discards transient
sections for foreign IDs, changed revisions/references/config fingerprints,
invalid timestamps, future timestamps or age above 300 seconds. Five minutes is
only a navigation shelf-life, not certification that HA stayed unchanged.
Reload/restart cannot turn persisted fingerprints into fresh inspection evidence.
No additional time-based network requests are introduced.

## Exactly one next step and existing UI

The backend declares a bounded internal action ID, label and navigation priority
per incomplete section. The UI only picks the first declared step; it never
calculates a new safety/confidence decision. Before clicking it recomputes the
current projection and compares basis plus displayed step. Expired or changed
navigation is rejected with an explanation, not silently repurposed.

Navigation uses existing source/evidence views, draft editing, explicit comparison,
explicit selected inspection, review-note editing or existing limitations. Data
cannot supply a URL, arbitrary service or executable callback. `open_matches`
focuses the existing selected-match control; it does not inspect automatically.
GET, filters, sorting and panel expansion never trigger comparison or autosave.

The zone toolbar filters by next work type and sorts by work priority, canonical
last-edit order or title with stable identity tie-breaks. View state is in memory,
cleared on zone changes; it is neither a persistent task queue nor an identity model.
The explanation panel uses textContent, responsive layout and visible keyboard
focus. Existing dirty draft/note editors and conflict protection stay authoritative.
Current projections restore keyboard focus by stable draft/control identity without
rerendering on focusout. Primary navigation always revalidates before use.
Explicit existing JSON export includes the effective compass; no automatic export.

## Tests and independent acceptance

Synthetic Python contracts cover canonical ownership, projection parity with the
shared JSON fixture, unchanged authored records/consents, revision changes,
missing/invalid evidence, source/target gaps, reset, restart, HEAD, same-basis
comparison and save, and denied Apply. JavaScript tests cover age boundaries,
late/foreign answers, revisions, fingerprints, filtering, nonmutation and internal
navigation allowlists. Existing regression suites remain included.

The new full-app Chromium test runs the actual aiohttp app with temporary canonical
stores and mocked HA reads. Its only control channel is the parent process stdin;
no test endpoint or token is shipped. It exercises filters, explicit reads, draft
conflicts/text preservation, escaped note input, inspection changes, keyboard
focus, zone isolation and mobile/desktop overflow. CI also retains the existing
full-shell and note-editor browser tests. Screenshots are synthetic, not household
acceptance. Local browser administrative restrictions are not bypassed; browser
verification is recorded from the ordinary repository CI.

The next product gate after a verified release is a useful or reasonably rejected
proposal in an already consented real use case. Actual HA Ingress acceptance,
app-specific configuration read rights and independent data preservation remain
separate until observed. No broader learning, second-zone consent or actuation
permission is inferred.
