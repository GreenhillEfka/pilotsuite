# Architecture Decision Log

## ADR-025 — Review briefs are derived and cannot authorize execution

The pattern workbench derives briefs and evidence graphs from the canonical report.
Existing feedback owns preference; no duplicate lifecycle or evidence store is added.
Context must match the candidate's local window and day group. Zone-wide coverage
stays explicitly zone-wide. A brief includes no executable actions; acceptance is
not actuation consent. Exports are explicit user downloads and may contain private
routine/source information. See docs/PATTERN_WORKBENCH.md.

Alpha.17 reuses the history retrospective function for retained evidence, with a
fixed rolling retention period split chronologically 70/30. Qualification uses only
the earlier partition; later evidence checks repeat observation without a confidence
estimate or predictive-accuracy claim. Day groups, local windows and zones remain
separate. Parameters may already reflect full-period review, so this is no unbiased
holdout validation. Existing preference and evidence owners remain unchanged.

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

## ADR-026 — Repeatable, source-bound release procedure

Accepted 2026-09-23. `docs/RELEASE_RUNBOOK.md` is required continuation context.
Every behavioral change after publication gets a new release number before delivery;
source SHA/tree, CI, installed version and live acceptance are distinct evidence.
Read-only preflight fails on stale markers, missing changelogs, version reuse or
non-descendant candidates. It cannot authorize installation. A completed scoped
app/data/options backup and concrete partial recovery remain mandatory. With
auto-update enabled, establish that recovery point before publishing the version.
Known Store access denials are recorded, not bypassed or repeatedly rediscovered.

Operational clarification 2026-09-23, requested by the user: RELEASE_RUNBOOK is the
single procedure; RELEASE_STATE.json is the compact last verified receipt, never
a replacement for live checks. Native Core backup/details is the working authorized
detail route. A denied Supervisor gateway is not proof all backup access is denied.
The normal Store path records canonical version/commit/app-tree association and
explicitly distinguishes it from independent checkout/image attestation. No repeated
install when current, no blanket re-authorization, no new credential or access bypass.

## ADR-027 — User-authored routine drafts in the canonical PlanStore

Accepted 2026-09-23 after the user approved the routine-draft concept. Build the
first bounded slice: persistent revisioned drafts referencing existing patterns,
editable declarative intent/targets/manual override, source-change review and JSON
export. Reuse PlanStore and shared SQLite migration 7; preserve legacy denied
JSONL plans without duplicating them. Do not persist a second evidence snapshot.
Learning reset and user-authored draft deletion are separate, explicitly described
operations. All new learning tests are synthetic. Structural completeness grants
no approval; automation comparison and risk remain unassessed, apply remains denied.
The next slice compares existing HA automations read-only; no automation writes or
broader execution authorization are implied. Contract: docs/ROUTINE_DRAFTS.md.

## ADR-028 — Bounded, transient existing-automation reference review

Accepted 2026-09-23 as the next read-only comparison slice in ADR-027. Reuse the
HA client and canonical PlanStore draft; query search/related only on explicit
request for saved confirmed targets/current pattern sources. Report source/target
reference overlap, not equivalence, causality, enabled status or safety. Show
unsupported indirect/dynamic references even for empty results. Keep results out
of SQLite/audit/learning; bind the transient view/export to revisions and sources.
Bound time, inputs and responses; reject failures without partial-clean claims.
No new consent, configuration collection or execution. Detailed semantics of an
explicitly selected existing automation are the next separate slice. Contract:
docs/AUTOMATION_REVIEW.md.

## ADR-029 — Selected structural inspection, open review plan and change receipt

Accepted 2026-09-23 as continuation of ADR-028 and the requested further concept
packages. Read one explicitly selected current match through automation/config;
reuse the canonical HA client and PlanStore draft. Bound configuration work and
return only whitelisted structure, scoped references and unknowns. No raw config
persistence, automatic scans, template evaluation or permissions change.
Keep all derived checklist items open. Compare canonical config fingerprints on
explicit retries; export only the current transient report with its draft basis.
Neither matching structure nor unchanged config establishes safety or equivalence.
No schema change or second evidence owner. The next separate slice may persist
user-authored review notes bound to draft revision/fingerprint in PlanStore, never
an approval to act. Contract: docs/AUTOMATION_INSPECTION.md.

## ADR-030 — Explicit review notes keep assessment, freshness and permission separate

Accepted design continuation of ADR-029 on 2026-09-23; implemented in development
PR #50, not a deployment or execution authorization. The existing PlanStore owns
bounded user-authored notes/dispositions for explicitly selected automations. Its
ReviewNotesMixin and HTTP/UI modules are code organization, not independent stores
or engines. Shared SQLite schema 8 adds a per-draft note/revision table after the
existing migration backup. Existing evidence, preference, risk and consent stay
unchanged; apply remains denied.

Bind each note to the draft/zone revisions, source/target scope fingerprint and
selected configuration fingerprint. GET, restart and persisted hashes never assert
current HA configuration: report not_rechecked until an explicit fresh read, and
only describe matching the last read, not continuous validity. Edits, reset, expiry
and unavailable targets mark the basis stale without erasing user text. Notes in a
shared workspace do not establish an authenticated individual author.

Saving reuses the bounded selected-automation inspection and then checks current
basis, note revision and maximum inspection age atomically with the SQLite write.
No HA I/O while holding the projection lock, no client-supplied inspection reports,
raw configuration or private upstream errors. HA and SQLite are not one transaction;
changes immediately after the HA read remain possible and explicitly unverified.

Separate monotonic review revisions protect competing writers and deletion; keep
an empty revision row after the last note is deleted to prevent stale revision
reuse. Deleting the draft also checks the notes revision before removing both.
The editor preserves text on errors and basis reload, and requires explicit save
or confirmed deletion. One bounded current note per selected automation, no silent
eviction or unlimited journal. Export is explicit and may include private user text.
No note or checkbox closes the derived checklist automatically, raises confidence,
creates an automation, changes policy, or grants permission to act.

Contract: docs/REVIEW_NOTES.md. PR #50 remains off main until fresh live/source and
scoped-backup gates, a new release number and exact CI satisfy ADR-026. Last-known
alpha.21 deployment and its older alpha.18 recovery backup are not fresh evidence
of the current live system. Resume the existing PR rather than recreating this slice.


## ADR-031 — Derived review compass is navigation, not authorization

Accepted continuation of ADR-025/027–030 and the explicit user mandate of
2026-09-24. The canonical PlanStore projects five sections from existing draft,
notes, inventory and retained evidence in its current transaction. No new state
owner, migration, learner, global safety score or action gate. Existing explicit
HA review routes enrich only automation/note sections after their current scope
checks. GET never performs an HA configuration review or saves an assessment.
Existing retention housekeeping remains unchanged.

The frontend composes only same-basis server sections and their declared next
steps; current sources/evidence/intent always come from the newest projection.
Transient reads expire for navigation after five minutes and do not prove ongoing
config validity. Filters, ordering and expansion are transient, zone-scoped view
state. User text, note dispositions and execution permission remain independent.
An allowed internal navigation ID is not an HA service or permission. Apply stays
closed. Contract: docs/REVIEW_COMPASS.md. Live acceptance is separate from tests.

The user's express resumed development mandate supersedes historical pause/next
slice instructions, not the release runbook or household consent boundaries.


## ADR-032 — Maintenance recovery stays narrow and native install remains native

Accepted 2026-09-25 for the explicit versions/savepoints/rescue/existing-helper request.
The canonical PlanStore owns local configuration points and preview-bound paused
restore; no HA configuration is written. Restore always captures a before-point,
keeps newer additional zones, revokes restored learning consents, advances revisions
and records idempotent completion. No evidence/raw credential/full-DB backup export.
Detected DB bootstrap failures keep only an Ingress-protected recovery page alive;
never auto-replace the database. Native HA remains responsible for cold app backup,
version installation and full app recovery; expose clear links, not a fake self-
updater requiring broader Supervisor rights. Existing helpers are inspected only
on explicit user request and matched by immutable storage identity. The historical
Golden Zone option is first-start bootstrap, not a second live zone editor.
Contract and limits: docs/MAINTENANCE_AND_RECOVERY.md.
