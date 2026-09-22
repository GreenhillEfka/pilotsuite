# Current State

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
