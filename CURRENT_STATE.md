# Current State

## Development: zone overview and evidence progress

PR #9 now also provides per-zone activity-v1 minimum events (5–100) and days
(3–14), revision-safe persistence, bounded validation, parameter-specific pattern
identity and a module status overview. Evidence is retained on parameter edits;
consent does not change. docs/LEARNING_AND_ACTIONS.md separates implemented learning
from planned script/automation drafts and governed execution. 70 backend tests,
four JS tests and validation pass locally. The previous PR head d76b40a passed CI
35798093744 (backend/browser/container); the expanded head needs its own CI gate.
Main advanced to alpha.10 via PR #10 during this work. Its structured assessment
contract is merged and rule-strength ratios use the configured per-zone thresholds.
No installation or new learning/actuation consent performed in this increment.


Extends alpha.9 with expandable source details in reference cards; persisted
presence-group names; collection-state explanations; consent and first/last retained
evidence timestamps; per-UTC-window counts and missing candidate requirements.
No statistical confidence percentage or uninterrupted coverage is implied.
No schema migration, role rewrite, consent change or HA update in this increment.
Previous increment: 66 backend tests and four JS tests passed locally; repository validation passed.
Browser regression extended, but local Chromium is unavailable: CI must verify it.
Live read-only check confirms alpha.9 started, ready and real Ingress API HTTP 200.
The user's exact live selection remains uninspected through the protected APIs.
Next: CI browser/container gate, then release preparation and scoped backup before
any production update. Real multi-day habits and live interactive acceptance remain open.


## Release candidate: 0.1.0-alpha.10 structured activity evidence

The next bounded change gives `activity-v1` candidates independent observation
statistics, deterministic threshold ratios, nullable statistical confidence,
read-only risk and durable user preference fields. Deprecated flat alpha fields
remain compatibility aliases; feedback still changes no evidence. Synthetic tests
cover the contract and persistence. PR #10 candidate CI 35798185711 passed 64
backend tests, four JS tests, browser regression and amd64 container before the
release metadata commit. App-only backup 522eda91 was then created from running
alpha.9; the completed listing excludes HA configuration/database. The partial
restore target is PilotSuite and its data only; archive internals and a restore
drill were not performed. alpha.9 remains installed until the final release-metadata
CI passes. Production learning consent remains unchanged.

## Released and running: 0.1.0-alpha.9

PR #8 merged as 04db3fb103850dd1c6f495d035f646d488a27b3d. Its tree
cbe0f8e1140a0f0d57b444041f8213ce7a8ba529 exactly matches candidate b1553a2.
Final CI 35797007069 passed 63 backend tests, four JS tests, extended mobile
browser regression and amd64 container. A mismatched Docker version marker was
caught by the release test and fixed before this final CI and deployment.

ADR-018 and docs/SENSOR_REFERENCES.md define the revised contract: automatic
virtual references for temperature, humidity, illuminance, presence and light;
persisted empty groups; consistent presence display/learning sources; visible
legacy defaults and explicit external comparison-temperature labeling.

App-only backup 19bfccc7 was created and confirmed before merge (automatic app
updates were already enabled). Listing reports unprotected, HA/database excluded.
Only PilotSuite and its data were requested; archive contents were not inspected.
Recovery is an App-and-data partial restore of that backup, not a full HA restore;
no restore drill was performed. No database migration or role rewrite was added.

Supervisor confirms alpha.9 started with unchanged options. Runtime logs at
2026-09-23T01:23:08Z report hard_read_only, ready=True, stream=True,
snapshot_fresh=True, zone_resolved=True. Existing source availability remains
partial for presence/light; readiness is not a physical sensor completeness claim.
Actual user selection and UI behavior in the live Ingress session remain to be
accepted. Do not infer that the user's exact presence-saving issue was reproduced:
code inspection found an inconsistent fallback and explicit-empty-group loss;
API persistence and browser reopen tests cover the corrections. Learning consent
was not changed by this deployment. New sensor classes require typed semantics;
no generic energy/alarm aggregation and no native HA reference entities yet.

## Historical alpha.8 deployment

Last updated: 2026-09-23 (runtime log UTC)

## Released and running: 0.1.0-alpha.8

PR #7 merged as 3aec18fce0b9d1e36abed1f81b38a034d36dcdcb with the exact
CI-tested tree f7ec8d4395f52b7b501424591dc4936031a183b8. CI 35793755621
passed 59 backend tests, four JavaScript tests, browser workflow tests and the
amd64 container build. A new subprocess regression executes the real module
entrypoint and checks HTTP health and database creation.

PilotSuite-only alpha.6 backup 89e963d5 was created and confirmed before updating;
HA configuration/database and unrelated Apps were excluded. alpha.7 initially
failed before startup callbacks/schema migration because main ran before newly
added route handlers were defined. alpha.8 moves the entrypoint after all handlers.
After installing alpha.8, an explicit start recovered the previously failed App.
Supervisor reports version 0.1.0-alpha.8 and state started. Runtime logs at
2026-09-23T00:45:49Z confirm hard_read_only, ready=True, stream=True,
snapshot_fresh=True and zone_resolved=True. Temperature/humidity/motion/illuminance
are available; presence/light are partial. Readiness does not mean every source
is complete or physically fresh.

## Implemented

Contract: docs/OBSERVATION_LEARNING.md and ADR-017. Only explicitly relevant
entities feed zone evaluation; unreviewed and ignored entities are excluded.
Zone tabs, mutable names, multiple HA-area sources, extra entity candidates and
direct start/pause remain available. The user confirmed Badbereich activation in
alpha.6; do not recreate it or infer that its new role groups were reviewed.

Compact zone cards summarize temperature, humidity, presence and light; entity
selection and raw neurons are expandable. Plural sensor roles support climate
median with source range/quality, separate reference temperatures and presence
from any active group member. A multi-room median is a zone summary, not an
individual room temperature. Missing or conflicting data remains visible.

Learning defaults off per zone. Explicit consent allows bounded live presence
activity evidence (14-day retention, 5,000 global records, five-minute zone-wide
cooldown). Candidates require at least five activations on three distinct UTC
dates in a two-hour UTC window. They carry unknown confidence, not causal or
person-specific claims. Feedback is independently persisted; export/reset and
consent revocation are implemented. No production consent was enabled and no
synthetic evidence was seeded during deployment. Climate suggestions remain
deterministic heuristics, separate from these activity candidates.

SQLite schema 4 stores zone definitions/selections, role groups, consent, evidence
and feedback, with migration backups and shared revision conflict checks. The
actual archive file was not inspected on the HA host. The successful startup
completed initialization; migration/backup details are covered by tests.

The reconnect correction from PR #4 (CI 35792464489, merge aac362a) remains:
short streams retain bounded 1/2/4/8/16/30-second backoff, reset only after a
60-second stable subscribed stream. Authentication failures do not report connected.
Ingress peer restrictions and hard-disabled HA actuation remain in force.

## Acceptance limits and next work

Startup/transport readiness is live-verified for alpha.8. Role selection, consent,
revision conflicts, feedback and reset passed browser/API tests, but these are not
proof of interactive acceptance in the user's actual HA Ingress session. The MCP
proxy cannot inspect protected APIs through the peer guard; do not bypass it.
No real multi-day learned routine is claimed. Live disconnect/load soak is pending.

Next: review relevant sources and plural roles in the actual zone UI; optionally
grant learning consent, then evaluate real evidence and durable feedback. Validate
a second unlike zone before 1.0. No autonomous HA action engine, native adapter,
voice integration, LLM dependency or causal habit model is implemented.

For downgrade recovery restore the scoped App-and-data backup 89e963d5; never
feed schema 4 to older code. No restore drill was performed. Historical alpha.5
and alpha.6 release evidence remains in git history and merged PRs #1/#3/#5.
The canonical repository remains GreenhillEfka/pilotsuite.
