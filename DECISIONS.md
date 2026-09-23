# Architecture Decision Log

## ADR-023 — Origin hints are consent-gated, ephemeral and non-identifying

Home Assistant context fields are correlation links, not verified human or
automation identities. PilotSuite may subscribe to `call_service` beside
`state_changed`, but correlates only while an enabled zone has explicit activity
learning consent and a valid source. Opaque context/user identifiers and service
payloads are never persisted or exported. Correlation lives in bounded memory for
120 seconds / 2,048 service contexts and is cleared on disconnect or when no
eligible consented source remains.

Stored evidence uses coarse categories: direct user context, correlated parented
service context, correlated unparented service context, uncorrelated derived
context or unknown. A user context is not proof of physical/manual operation; a
parented service context is not proof of one particular automation or script.
Current read-only PilotSuite creates no own-action evidence. Future own actions must
be marked explicitly by the single transaction owner and excluded from learning,
not guessed from generic HA context chains. See `docs/EVENT_ATTRIBUTION.md`.

## ADR-022 — Local rhythms, sampled observability and separately consented context

Stored UTC events are grouped using a saved IANA timezone and optional weekday /
weekend separation. UTC defaults preserve legacy behavior and candidate identity.
DST repetition cannot fabricate extra days. Time grouping participates in identity.
Observability uses bounded five-minute checkpoint buckets, not inferred uptime or
physical sensor coverage. New context evidence requires separate consent and uses
only explicitly saved complete light/lux groups at event processing time. It is
co-occurrence, not a causal switching sequence or an executable plan. Schema 5
backs up before adding context/checkpoint tables; reset, retention and source edits
cover the new evidence. See docs/RHYTHMS_AND_CONTEXT.md for limits and recovery.


## ADR-021 — Bounded per-zone learner parameters, separate action authorization

Activity-v1 thresholds are stored in the canonical zone context JSON with backward
compatible defaults, integer limits and existing revision conflict protection.
Omitted detector settings preserve the previous values. Parameter changes re-evaluate
retained evidence without deleting or inflating it. Nondefault configurations have
distinct candidate identities; feedback remains bound to its original configuration.
No schema migration, arbitrary algorithm loading or new actuation permission.
Modules expose implemented/planned/blocked state. Native HA scripts/automations are
the preferred future delivery for stable rules after inventory review, preview,
separate plan-bound approval, backup, apply and verification. See LEARNING_AND_ACTIONS.md.


## ADR-020 — Explain evidence progress without inventing confidence

The existing activity detector exposes counts and missing requirements per UTC
window. Totals from different windows must not qualify a candidate. First/last
retained evidence timestamps are not continuous coverage or a collection start.
Consent, zone enablement, transport readiness and suitable sources are separate
collection gates. UI surfaces persisted presence sources and compact source details.
No new consent, thresholds, storage schema or actuation is introduced.


## ADR-019 — Activity candidates expose independent assessment dimensions

The `activity-v1` candidate contract separates observed statistics, deterministic
rule strength, statistical confidence, action risk and user preference. Rule
strength reports only ratios against the five-event/three-day candidate threshold.
It is not a probability and does not imply causality. Confidence stays null until a
validated estimator exists. Current risk is `read_only`; no action is attached.
Persisted feedback is exposed canonically as preference and never mutates evidence
or rule strength. Earlier flat fields remain deprecated compatibility aliases until
an announced API-version transition; they are not a second stored model.

## ADR-018 — One main group yields one virtual reference per supported class

Main groups produce automatic typed zone references; external comparison sources
are separate. Presence display and opt-in learning use the same saved group, with
no all-relevant fallback. Explicit empty groups persist and never trigger fallback.
Illuminance uses validated lux values and a median with spread, not a switching rule.
Legacy singleton climate defaults remain visible until explicitly edited.
See docs/SENSOR_REFERENCES.md for semantics and unsupported-class limits.

## ADR-017 — Confirmed-only observations, role groups and bounded activity learning

The user approved removing the automatic selection exception. Only explicitly
relevant, supported candidates generate neurons, mood evidence or learning evidence.
No migration infers relevance. This supersedes the optional-selection part of ADR-016.

Roles are groups of up to 20 suitable relevant sources, not device_class overrides.
Explicit climate groups use normalized valid values' median with min/max/spread and
missing-source status. With no role, only one unambiguous climate candidate is used.
References remain separate. Presence uses any-on; all-off requires all sources valid.
Source-level evidence accompanies aggregate moods. Multi-room groups are summaries,
not claims about a single room or replacements for independent safety alarms.

The first learner is a deterministic recurring-activity candidate detector, not a
full habit model. It records only fresh subscribed off-to-on events from consented,
relevant presence group members in an enabled zone. A five-minute zone cooldown
avoids multi-detector inflation. Snapshots/reconnects are never learning evidence.
Five events on three UTC dates in the same UTC two-hour bucket produce a candidate;
confidence remains unknown, outages are unobserved, and no causal inference is made.

Schema 4 shares the canonical SQLite database, backs up before migration and defaults
learning off. Retention: 14 days, 5,000 evidence records globally, 2,000 feedback rows.
Feedback never changes counts. Revoke stops collection; reset deletes evidence and
feedback and stops learning; changing the presence group clears its prior evidence
and feedback. New consent timestamps prevent replay of older events. UI informs
before granting consent/reset/group change. HA actuation remains hard-disabled.


## ADR-016 — One visible workspace per zone

Zone tabs select the context for entity choices, evaluation, proposals and observations.
Direct start/pause changes only the zone enabled flag with revision protection.
Entity selection mode remains distinct and advanced; saving relevant entities does
not silently activate a paused zone. Source areas use checkboxes. New zones stay
paused and neutral. Existing stored definitions and decisions remain authoritative.


## ADR-015 — Logical Habitus zones own context, not HA topology (2026-09-22)

Zones have stable identity, mutable names, HA-area sources and extra entity
candidates. One SQLite store owns definitions and selection with a shared revision.
Existing configured areas are bootstrapped once without losing decisions. New zones
start with curated selection; the UI creates them paused with a neutral profile.
Inference is per zone. Global entity counts deduplicate IDs; zone proposals retain
their own scope. Cellar thresholds are opt-in for new zones. HA registries are never
rewritten. Disable preserves data; export and bounded journal support review.
See docs/HABITUS_ZONES.md for the implemented contract and deferred extensions.

## ADR-014 — Operational readiness is not domain completeness (2026-09-22)

Accepted after the alpha.3 live UI review: readiness measures a connected HA
snapshot, healthy event subscription and recent reconciliation. Zone resolution
and sensor capabilities are separate. Missing humidity does not disable motion,
light or temperature observations. Absent measurements are not sensor failures;
an existing invalid/unavailable climate sensor still contributes to climate
uncertainty. Buttons and unrelated diagnostics do not. Unassessable climate moods
use null, not zero. Capability availability never grants permission to actuate.

## ADR-009 — Reviewed target architecture (2026-09-22)

Accepted: one repository, one modular add-on, one semantic owner. An optional
thin HA integration may expose native entities and Conversation; it must not
contain inference, learning, policy, or a second PilotSuite configuration store.
HA owns raw registry/state truth. PilotSuite owns its composed Habitus zones,
roles, policies and preferences, referencing HA identifiers. This intentionally
supersedes the old HA repository's ownership of curated PilotSuite zone storage.
UI ownership is not data ownership; HA UI edits call the canonical owner.

## ADR-010 — Evidence is not preference (2026-09-22)

Severity, data quality, statistical confidence, user preference and action risk
are separate fields. Unknown confidence is null, not a heuristic percentage.
Feedback must not mutate observed event counts. Suggestion identity depends on
versioned rule and normalized scope, never a changing measurement or score.

## ADR-011 — Storage and learning (2026-09-22)

Target: SQLite for PilotSuite-owned zone definitions, bounded learning evidence,
feedback, proposals and transaction journal; schema migrations and retention
required. Existing alpha JSONL remains until a tested migration is implemented.
No full HA history clone, graph database, broker or vector database is required.
The graph is a view of evidence, not a competing source of truth.

## ADR-012 — Action-specific recovery (2026-09-22)

ADR-005 describes the single governed execution path, not universal reversibility.
Every future action declares preconditions, authorization scope/expiry,
idempotency behavior, backup requirements, verification and recovery semantics.
Irreversible effects must be explicit. Configuration files are never blindly
overwritten; additive changes require backup and validation. No alpha actuation.

## ADR-013 — Prove learning early, autonomy late (2026-09-22)

Read-only learning and feedback precede actuation. Test a second unlike zone
before stabilizing the architecture. Use HA Assist and existing device integrations
instead of rebuilding STT/TTS or promising uniform support for every voice device.

## ADR-001 — One canonical repository

**Status:** accepted — 2026-09-22

`GreenhillEfka/pilotsuite` is the only canonical implementation. Earlier PilotSuite, Styx, and Habitus repositories are reference material, not merge targets or runtime dependencies.

## ADR-002 — Add-on-first architecture

**Status:** accepted — 2026-09-22

PilotSuite runs as one Home Assistant Supervisor App. A custom integration may be added later only where native Home Assistant entities or services create concrete value. This avoids coordinating multiple backends during the proving phase.

## ADR-003 — Home Assistant remains source of truth

**Status:** accepted — 2026-09-22

PilotSuite reads registries and states through supported APIs and maintains only a bounded in-memory projection plus PilotSuite-owned metadata. It does not clone the Home Assistant state database.

## ADR-004 — LLM outside the critical path

**Status:** accepted — 2026-09-22

An LLM may explain, summarize, or propose. It cannot bypass policy evaluation or execute Home Assistant actions directly. PilotSuite remains useful without an LLM.

## ADR-005 — One transaction path

**Status:** accepted — 2026-09-22

All future mutations use `plan -> backup -> apply -> verify -> rollback`. Separate ad-hoc action paths are forbidden.

## ADR-006 — Read-only alpha

**Status:** accepted — 2026-09-22

`0.1.0-alpha.1` rejects every apply request in code, regardless of options. This lets the connector, world model, resolver, audit, API, and Golden Zone be validated without changing the house.

## ADR-007 — Erdkeller as Golden Zone

**Status:** accepted — 2026-09-22

The Erdkeller is the first bounded end-to-end scope. Entity selection is derived from Home Assistant area membership, not a hard-coded entity list.

## ADR-008 — No build.yaml

**Status:** accepted — 2026-09-22

The Dockerfile is the single build source according to the Home Assistant 2026 BuildKit migration. The Home Assistant multi-architecture Python base image is pinned.

## ADR-024 — Targeted history and shared retrospective activity evidence

Accepted 2026-09-23 for the history package. Read only saved relevant main groups
through HA APIs; do not copy Recorder. Separate sampled state graphs from hourly
statistics and prohibit statistics-based activation imports. One-time scoped
historical consent complements live consent. Import off→on transitions into the
existing activity-v1 store with provenance, bidirectional cooldown deduplication,
revision guards and existing retention. History never fabricates uptime samples.
Schema 6 backs up before adding provenance/receipts. Current source mapping applied
retrospectively is explicit. Chronological 70/30 reobservation checks do not claim
predictive accuracy or authorize actions. Contract: docs/HISTORY_AND_TRENDS.md.
Historical light-context persistence is deferred; no implicit extension of consent.
