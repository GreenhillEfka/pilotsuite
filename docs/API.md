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
| `GET` | `/api/v1/selections/{area_id}` | Read an entity-selection inventory. The parameter is the historical selection scope and is normally a zone ID. |
| `PATCH` | `/api/v1/selections/{area_id}` | Save explicit entity decisions with revision checking. |
| `GET` | `/api/v1/zones/{zone_id}/context` | Read roles, learning configuration, evidence summaries, patterns and drafts. |
| `PATCH` | `/api/v1/zones/{zone_id}/context` | Save roles and explicit learning configuration; may reset owned evidence only when requested. |
| `GET` | `/api/v1/zones/{zone_id}/context/export` | Export the zone's owned learning evidence and configuration. |
| `POST` | `/api/v1/zones/{zone_id}/feedback` | Save a user decision for one owned pattern; does not change observation counts. |
| `POST` | `/api/v1/zones/{zone_id}/history` | Read a bounded historical view without importing it. |
| `POST` | `/api/v1/zones/{zone_id}/history/import` | Import explicitly selected historical observations into the owned learning store. |

## Foundations and presence adoption

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/zones/{zone_id}/helpers/inspect` | Inspect selected helpers without changing them. |
| `POST` | `/api/v1/zones/{zone_id}/helpers/provision` | Execute the explicit helper-provisioning contract after its own validation. |
| `GET` | `/api/v1/zones/{zone_id}/presence-runtime` | Read the presence-foundation runtime configuration. |
| `PATCH` | `/api/v1/zones/{zone_id}/presence-runtime` | Save presence runtime configuration with the endpoint's consent and revision checks. |
| `POST` | `/api/v1/zones/{zone_id}/presence-adoption/review` | Perform an explicit read-only adoption review of existing presence automations. |

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
