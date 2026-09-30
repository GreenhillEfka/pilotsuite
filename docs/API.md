# API

All routes are relative to the Home Assistant Ingress root. Responses are JSON
unless noted. Except for the loopback `/health` probe, the TCP peer must be an
allowed Ingress peer; forwarded headers never grant access.

The method alone does not describe side effects. In particular, several `POST`
routes perform bounded read-only inspection, while configuration, feedback,
note, draft, savepoint and plan-apply routes can persist data or perform their
explicitly documented operation. Clients must not call a route merely because
it appears in this inventory.

## Runtime and observations

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/status` | Consolidated runtime and connector status. |
| `GET` | `/api/v1/architecture` | Immutable architecture and execution guardrails. |
| `GET` | `/api/v1/areas` | Home Assistant area inventory resolved by PilotSuite. |
| `GET` | `/api/v1/world` | Bounded world-model summary. |
| `GET` | `/api/v1/golden-zone` | Golden-zone entities and observations. |
| `GET` | `/api/v1/moods` | Deterministic mood scores and their evidence. |
| `GET` | `/api/v1/suggestions` | Current explainable suggestions. |
| `GET` | `/api/v1/audit` | Append-only PilotSuite audit tail; optional `limit` query. |
| `POST` | `/api/v1/refresh` | Refresh the read-only Home Assistant snapshot. |

## Zones, selections and learning context

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/zones` | List saved PilotSuite zones and their latest derived results. |
| `POST` | `/api/v1/zones` | Create a validated PilotSuite zone definition. |
| `PATCH` | `/api/v1/zones/{zone_id}` | Replace a zone definition with revision checking. |
| `GET` | `/api/v1/zones/export` | Export zone definitions and selections. |
| `GET` | `/api/v1/entity-catalog` | Read the bounded entity catalog used by zone configuration. |
| `POST` | `/api/v1/zone-candidates` | Read-only bounded member proposal from selected area_ids/entity_ids, including stable identities and existing roles. No selection or HA writes. |
| `GET` | `/api/v1/zone-labels` | Explicit HA label read plus counts including device membership and the canonical Habitus role vocabulary. No write. |
| `GET` | `/api/v1/zone-labels/{label_id}` | Propose up to 500 direct/device-inherited members with roles, identity and disabled status. Never starts analysis or control. |
| `GET` | `/api/v1/zones/{zone_id}/structure` | Read saved zone-label/member/role connection and explicit relevance decisions from existing stores. |
| `POST` | `/api/v1/zones/{zone_id}/structure/preview` | Preview the saved desired labels against the current registry. Durable `structure_labels` plan; apply and restore use the existing ontology endpoints. |
| `GET` | `/api/v1/selections/{area_id}` | Read an entity-selection inventory. The parameter is the historical selection scope and is normally a zone ID. |
| `PATCH` | `/api/v1/selections/{area_id}` | Save explicit entity decisions with revision checking. |
| `GET` | `/api/v1/zones/{zone_id}/context` | Read roles, learning configuration, evidence summaries, patterns and drafts. |
| `PATCH` | `/api/v1/zones/{zone_id}/context` | Save roles and explicit learning configuration; may reset owned evidence only when requested. |
| `GET` | `/api/v1/zones/{zone_id}/context/export` | Export the zone's owned learning evidence and configuration. |
| `POST` | `/api/v1/zones/{zone_id}/feedback` | Save a user decision for one owned pattern; does not change observation counts. |
| `POST` | `/api/v1/zones/{zone_id}/history` | Read a bounded historical view without importing it. |
| `POST` | `/api/v1/zones/{zone_id}/history/import` | Import explicitly selected historical observations into the owned learning store. |

## Live shadow comparison

Zone create/update optionally accepts `setup: {label_id, entity_ids,
relevant_entity_ids, roles?}`. `roles` maps selected entity IDs to Habitus role names.
The definition, stable member identities, roles and explicit relevance decisions
commit together under one zone revision in the existing SQLite transaction.
Omitting setup preserves older clients and stored structure. Identical saves are
no-ops. Duplicate zone-label ownership, replaced identities, disabled members,
multiple anchors and an anchor selected as its own evidence are rejected.
This save does not write HA, change learning, create helpers or enable a module.
The existing structure GET additionally returns `member_identities`, each with
`saved_entity_id`, currently resolved `entity_id` (or null), `name` and `status`.
Statuses reuse Organization's resolver (`bound`, `renamed`, `identity_unresolved`)
plus explicit `disabled`. `identity_basis: cached_registry_not_live_state` separates
registry identity from runtime state/freshness. Profile and relevance remain the
saved canonical values; this projection performs no HA network read or migration.
The editor opens definition/structure only with matching revisions.

Metadata synchronization preserves unrelated labels, names and physical location.
Removing a member stops its selected analysis but does not delete HA labels blindly.
One concrete preview/apply covers the selected changes. HA and SQLite are not an
atomic system; operation readback and conflict/unknown outcomes remain visible.

When a zone has saved structure, the existing presence-package/single-helper
preview includes readable names and the zone/Habitus labels for its newly created
objects. Creation, stable-identity receipt, metadata before/after and readback use
the same durable plan. A lost metadata response requires independent readback,
never duplicate helper creation. Manual metadata changes block recovery rather
than being overwritten. Full-package binding includes its five own members in
the zone structure and scope in the existing configuration transaction, with
publication still in comparison mode. Historical callers without a label
connection retain their separate explicit ontology workflow.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/zones/{zone_id}/presence-shadow` | Read latest confirmed shadow state without starting collection or advancing its checkpoint. |
| `POST` | `/api/v1/zones/{zone_id}/presence-shadow` | Explicit revision-bound start/stop. Persists only settings/latest checkpoint, never learning consent, history or HA actions. |

## Foundations and presence adoption

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/zones/{zone_id}/helpers/inspect` | Inspect selected helpers without changing them. |
| `POST` | `/api/v1/zones/{zone_id}/helpers/provision` | Execute the explicit helper-provisioning contract after its own validation. |
| `GET` | `/api/v1/zones/{zone_id}/presence-runtime` | Read the presence-foundation runtime configuration. |
| `PATCH` | `/api/v1/zones/{zone_id}/presence-runtime` | Save presence runtime configuration with the endpoint's consent and revision checks. |
| `POST` | `/api/v1/zones/{zone_id}/presence-runtime/replay` | Replay one allowlisted synthetic presence scenario without reading or changing HA, consent or stored runtime state. |
| `POST` | `/api/v1/zones/{zone_id}/lighting-preview` | Preview one allowlisted synthetic daylight/mood scenario without reading or changing HA, consent or stored state. `zone_inputs` separates configured/currently usable lights, indoor illuminance and binary brightness; `daylight_basis` states that scenario lux is synthetic and no configured signal is thereby confirmed as an outdoor daylight reference. The legacy aggregate `configured_reference_count` is only a configured-signal count, not provenance evidence. |
| `PUT` | `/api/v1/zones/{zone_id}/lighting` | Save revision-bound light comparison settings in the existing ContextStore. Requires configured primary zone presence and stable relevant targets/sources. Compare or pause only; no actuator calls. Current proposals are part of the existing presence GET. |
| `POST` | `/api/v1/zones/{zone_id}/lighting-decision` | Explicit transient check of the current canonical zone roles, cached observations and freshly read related automation structures. Returns exactly one next step, never treats indoor lux as confirmed outdoor daylight, never infers physical measurement freshness from transport freshness, persists nothing and cannot execute. |
| `POST` | `/api/v1/zones/{zone_id}/presence-adoption/review` | Explicit read-only structural review. Saved organization bindings select existing-control mode; otherwise the legacy review remains compatible. No execution. |

The existing zone-presence GET includes `lighting.current.daylight.status` when a
comparison is available: `valid`, `not_configured`, `connection_unconfirmed`,
`provenance_unconfirmed`, `time_unknown`, `stale`, `unit_invalid` or `value_invalid`.
This explains the first failing existing gate; only `valid` accompanies a numeric
lux value. `manual_sources` retains the observed state per configured entity.
Diagnosis is read-only and does not relax proposal gates or authorize execution.

## Routine drafts, comparisons and review notes

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/zones/{zone_id}/drafts` | List derived routine drafts for the current zone revision. |
| `POST` | `/api/v1/zones/{zone_id}/drafts` | Create a draft from one owned pattern; never executes it. |
| `PATCH` | `/api/v1/zones/{zone_id}/drafts/{draft_id}` | Save user-authored draft fields with revision checking. |
| `DELETE` | `/api/v1/zones/{zone_id}/drafts/{draft_id}` | Delete one PilotSuite draft after revision validation. |
| `POST` | `/api/v1/zones/{zone_id}/drafts/{draft_id}/automation-review` | Read and compare selected existing automations. |
| `POST` | `/api/v1/zones/{zone_id}/drafts/{draft_id}/automation-inspection` | Re-read one selected automation for a current detailed inspection. |
| `POST` | `/api/v1/zones/{zone_id}/automations/import` | Import one existing automation as a detached, non-executable review snapshot. |
| `GET` | `/api/v1/zones/{zone_id}/drafts/{draft_id}/review-notes` | Read the saved personal review note and its reference state. |
| `PUT` | `/api/v1/zones/{zone_id}/drafts/{draft_id}/review-notes` | Re-inspect the referenced automation, then save the note only if revisions still match. |
| `DELETE` | `/api/v1/zones/{zone_id}/drafts/{draft_id}/review-notes` | Delete the note with note, draft and zone revision checks. |

## Existing-inventory organization

Alpha.61 adds optional `presence_output` (one occupancy/presence binary sensor) to
the existing organization assignments. `GET .../presence` projects these canonical
bindings under `existing`: owner/timer/sensor observations, identity/availability,
actual timer deadline, comparison and Boolean/sensor consistency. GET performs no
HA I/O and unavailable never becomes off. PATCH saves mapping only, preserving the
zone behavior, mode, other zones, legacy roles and consents. Outputs cannot be inputs.
With saved status/timer/output/automation bindings, `presence-adoption/review` reads
related and selected automations, bounded to 50, without legacy runtime setup.
`mode=existing_control`, `control_changed=false`, `persisted=false`, `checked_at`
and per-row `usage`/`observed_enabled` describe the dated read. Configuration-read
failure or changed basis invalidates the result; coverage is explicitly incomplete.
The historical endpoint name and `conflict` classification do not grant takeover;
`usage` distinguishes expected existing writers from consumers/mixed logic.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/zones/{zone_id}/organization` | Read role bindings, eligible inventory, naming proposals and existing plans. |
| `PATCH` | `/api/v1/zones/{zone_id}/organization` | Save explicit role bindings and timing with revision checking. |
| `POST` | `/api/v1/zones/{zone_id}/organization/{operation}` | Run one allowed operation: `analyze`, `names` or `repair-preview`. Analysis is read-only; the preview operations create review plans but do not apply them. |
| `GET` | `/api/v1/zones/{zone_id}/organization/plans/{plan_id}` | Read a specific organization plan. |
| `POST` | `/api/v1/zones/{zone_id}/organization/plans/{plan_id}/{operation}` | Run `restore-preview`, or explicitly confirmed `apply` under the plan contract. |

## Maintenance and savepoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/maintenance` | Read database, migration and savepoint status. |
| `POST` | `/api/v1/maintenance/savepoints` | Create an application-data savepoint. |
| `POST` | `/api/v1/maintenance/savepoints/{point_id}/preview` | Preview the bounded effects of restoring a savepoint. |
| `POST` | `/api/v1/maintenance/savepoints/{point_id}/restore` | Restore after the endpoint's explicit confirmation and freshness checks. |

## Legacy dry-run plan boundary

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/plans` | Create a dry-run plan; never executes it. |
| `POST` | `/api/v1/transactions/{plan_id}/apply` | Retained hard read-only boundary; returns `409` in this release. |

## Non-API routes

`GET /health`, `GET /health/ready` and `GET /version` provide liveness,
readiness and version metadata. The Ingress workspace, maintenance page and
static assets are intentionally not part of the JSON API inventory above.

## Error format

```json
{
  "error": "read_only_release",
  "message": "The active release cannot execute this transaction",
  "request_id": "..."
}
```

Domain conflicts and invalid input use structured `4xx` responses. Bounded
upstream failures use endpoint-specific `503` responses without echoing Home
Assistant credentials or partial household data. Unexpected failures use the
generic `internal_error` response and a request ID.

## Current readiness and capability contract

`ready` and `/health/ready` describe transport readiness only: connected
snapshot, live event stream and recent reconciliation. Zone resolution is
reported independently. A current transport snapshot is not proof that a
physical measurement is current.

`capabilities` reports per-kind status as `available`, `partial`, `unavailable`
or `not_present`, with entity and valid counts. These are observation states,
not permissions, safety certificates or implemented automation capabilities.
Mood `score` is nullable for missing evidence; clients must not convert null to
zero. Climate uncertainty counts observed climate sensors only.

## Learning and decision-model separation

Activity candidates expose independent `statistics`, `rule_strength`, nullable
`confidence`, `risk`, and `preference` fields. `rule_strength` is a deterministic
threshold relation, not a probability. Feedback changes only `preference`, never
stored evidence or observation counts. Review notes and execution rights are
separate again; neither a note nor a positive preference authorizes execution.

Origin counts contain coarse categories only. PilotSuite does not export Home
Assistant user or context identifiers. A correlated service context is not proof
of a specific person, automation or script. Correlation is memory-only and
consent-gated.

Zone context configuration accepts optional `context_learning` and detector
settings such as an IANA `timezone` and `day_mode`. Context consent requires
activity consent. Local-day statistics expose their timezone and day group;
clients must not label local windows as UTC. See
[RHYTHMS_AND_CONTEXT.md](RHYTHMS_AND_CONTEXT.md) for sampling, retention and
reset semantics.

## Stability

The `/api/v1` prefix is stable, but alpha response fields may grow. Existing
fields are not silently repurposed. Every explicitly registered `/api/v1` method and
canonical path must be present in the endpoint inventory; the repository validator
fails when implementation and documentation drift.

## Zone presence configurator and relevance-authorized data (Alpha.49 candidate)

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/zones/{zone_id}/presence` | Current typed presence, relevant live sources and configuration; no HA writes. |
| `PUT` | `/api/v1/zones/{zone_id}/presence` | Revision-bound behavior save; publish requires an owned verified output package. |
| `POST` | `/api/v1/zones/{zone_id}/data` | Relevant raw history and numerical/state visualizations, no extra data consent. |
| `POST` | `/api/v1/zones/{zone_id}/presence/package` | Prepare an explicitly reviewable owned output package or one missing Boolean/timer; no HA write. |
| `POST` | `/api/v1/zones/{zone_id}/presence/package/{plan_id}/apply` | Confirm exact helper-creation plan with durable receipts and no blind replay. |
| `GET` | `/api/v1/zones/{zone_id}/ontology` | Current entity/label inventory and canonical Habitus roles. |
| `POST` | `/api/v1/zones/{zone_id}/ontology` | Preview custom display name and exact role labels; ID migration remains blocked. |
| `POST` | `/api/v1/zones/{zone_id}/ontology/{plan_id}/apply` | Apply exact metadata plan; no physical area or entity-ID mutation. |

| `POST` | `/api/v1/zones/{zone_id}/ontology/{plan_id}/restore-preview` | Prepare a guarded metadata rollback only if the current after-image still matches. |

The package preview accepts `{revision}` for the complete owned output package.
Alpha.71 additionally accepts exactly `{revision, helper_role, duration_seconds}`:
`helper_role` is `presence_status` (duration null) or `presence_timer` (integer
1–86400 seconds). A `presence_helper` plan creates one unconnected helper through
the same confirmed apply endpoint. Existing/unresolved role bindings, owned packages
and registry collisions block creation. It does not require a PilotSuite presence
configuration and does not alter assignments, automations or publication. Durable
identity receipts are historical creation evidence, not current functionality;
lost responses never authorize blind replay or ownership inferred from a name.


### Unreleased connected zone setup

The optional zone `setup` accepts an existing `label_id`, or `label_id: null` plus
`label_name` (1–80 characters) to plan a new zone label. This saves intent only.
`entity_ids`, `relevant_entity_ids` and optional per-member `roles` are validated
against stable registry identities. Areas/extra candidates are read-only proposals.
Pending names cannot duplicate another planned zone or an existing HA label.
An unbound pending label can be explicitly replaced with an existing label after
an unresolved creation; name equality never silently establishes ownership.

`structure/preview` includes new label creation and all member metadata in the
same durable `structure_labels` plan (maximum 500 members plus one label). Native
create response, independent readback and final SQLite binding are separate proofs.
The immutable proposal uses an internal label reference; only the actual returned
label ID is sent with member metadata. Apply may resume confirmed pending steps;
uncertain metadata is read back only, never repeated. A lost creation response
without a durable receipt remains unknown. `binding` records the resulting zone
revision. Reverse metadata plans preserve the created label and its zone binding;
there is no automatic deletion of an object that other HA consumers may now use.

Fresh labels, device membership, anchors and shared roles are checked before
application, sensitive anchor edits and completion. Each changed entity retains
an exact before/after image; final readback detects intervening edits. HA registry
writes and SQLite are not an atomic distributed transaction. Unresolved/partial
outcomes remain inspectable in the existing organization plan history.
