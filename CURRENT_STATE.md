# Current state — Alpha.55 presence-first workspace candidate

## Verified baseline

Work continues only in GreenhillEfka/pilotsuite. Concept PR #118 merged as
`c04cf90770ed4166d692b5dc8f018be2ef57e35f`; its main CI run `36359118246` succeeded.
Fresh HA-MCP reads on 2026-09-28 confirmed Alpha.54 installed/offered, started,
auto_update enabled. The Alpha.54 release receipt remains in
[docs/RELEASE_STATE.json](docs/RELEASE_STATE.json) until delivery is verified.

## Implemented in this candidate

Alpha.55 reuses the existing workspace and zone-presence API. Three primary entries
(Zonen, Werkzeuge, System) group the old view keys without replacing preferences,
forms or stores. Zone state, history and configuration share one primary presence
card. Module aggregates, the legacy shadow comparison and synthetic replay sit
under explicit diagnostic details. Organization remains available under Werkzeuge.

Missing/unavailable presence is explicit, required-source gaps remain visible,
paused operation is not labelled comparison, and HA publication is separate from
calculation. Failed reads disable stale actions while retaining a read-only retry;
a valid recovered basis is read immediately. No kernel, schema, stored zone,
source selection, write capability or authentication boundary changes.

## Verification and release gate

The navigation regression failed against the six-entry baseline before the change.
Local verification: 568 Python and 73 JavaScript tests, repository/API invariants,
discovery, frontend syntax and all 11 existing synthetic browser suites passed.
The extended actual-app fixture uses four zones and covers occupied, empty/unknown,
paused, required unavailable sources, failed reads, passive scroll/focus preservation,
draft guards, keyboard/direct links and 390/768/1440-pixel light/dark views.
Screenshots are synthetic evidence, not household screenshots. SQLite ResourceWarnings
still occur in the Python suite; no leak-free claim is made.

PilotSuite-only backup `89e5ef42` was completed before version publication and
verified through snapshot list plus native `backup/details`: exactly Alpha.54 app,
54,446,080 bytes, unprotected local agent, no HA/database/folders, no failures or
agent errors. Archive extraction and a restore drill were not performed.

Exact candidate CI, main CI and installation must still be verified after publishing
the reviewable feature PR. Container/protocol checks are CI gates, not claimed as
local checks. AGENTS.md is pre-existing local untracked work and remains untouched.

## Remaining acceptance and next scope

No authorized authenticated household browser is connected. No Ingress/auth/sandbox
bypass was attempted. A local synthetic browser is not household Ingress acceptance.
All four saved household zones have not been independently read back after Alpha.54.
Inspect Erdkellerbereich and one unlike saved zone read-only when authorized browser
access exists; preserve entity cleanup and compare multiple passive refreshes.

Own-output activation, automation takeover, entity-ID migration and adaptive learning
are not authorized by this UI change. Runtime deduplication remains a later measured
package, not part of Alpha.55. See [docs/ROADMAP.md](docs/ROADMAP.md).
