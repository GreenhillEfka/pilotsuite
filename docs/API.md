# API

All endpoints are relative to the Ingress root. Responses are JSON unless noted.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness; used by the Supervisor watchdog |
| GET | `/health/ready` | readiness including HA connector state |
| GET | `/version` | release and architecture version |
| GET | `/api/v1/status` | consolidated runtime status |
| GET | `/api/v1/architecture` | immutable architecture guardrails |
| GET | `/api/v1/areas` | resolved Home Assistant areas |
| GET | `/api/v1/world` | bounded world-model summary |
| GET | `/api/v1/golden-zone` | Golden Zone entities and observations |
| GET | `/api/v1/moods` | deterministic mood scores and evidence |
| GET | `/api/v1/suggestions` | current explainable suggestions |
| GET | `/api/v1/audit?limit=100` | append-only PilotSuite audit tail |
| POST | `/api/v1/refresh` | refresh read-only snapshot |
| POST | `/api/v1/plans` | create a dry-run plan; never executes |
| POST | `/api/v1/transactions/{id}/apply` | always returns `409` in this release |

## Error format

```json
{
  "error": "read_only_release",
  "message": "0.1.0-alpha.3 cannot execute Home Assistant mutations",
  "request_id": "..."
}
```

## alpha.4 readiness and capability contract

`ready` and `/health/ready` now describe transport readiness only: connected
snapshot, live event stream and recent reconciliation. Zone resolution is
`golden_zone.resolved`; `capabilities` reports per-kind status as `available`,
`partial`, `unavailable` or `not_present`, with entity/valid counts. These describe
observations, not permission or implemented automation capabilities.
Mood `score` is nullable for missing evidence; clients must not convert null to
zero. Climate uncertainty counts observed climate sensors only, never buttons
or unrelated diagnostic entities. The legacy `missing_required_kinds` field
remains informational for climate coverage; it no longer gates readiness.

## API stability

### alpha.3 contract change

Suggestion `confidence` is now nullable: deterministic climate rules return null
instead of an uncalibrated number. New `severity` contains rule strength, not a
probability. IDs are stable for the versioned rule and normalized scope.

Activity candidates from `GET /api/v1/zones/{zone_id}/context` expose independent
`statistics`, `rule_strength`, nullable `confidence`, `risk`, and `preference`
fields. `rule_strength` reports deterministic threshold ratios only; it is not a
probability. Posting feedback changes only `preference`, never stored evidence or
counts. The earlier flat `events`/`days`/`observed_total`/`origins`/`feedback`
fields remain deprecated read-only aliases until an announced API-version change.
Status adds `ready`, `event_stream_connected`, `snapshot_fresh`, and
`missing_required_kinds`. In alpha.3 readiness required the stream, a recent snapshot, a
resolved scope and valid temperature/humidity inputs; alpha.4 supersedes that rule. It does not certify physical
sensor freshness. All UI/API calls require the Ingress TCP peer; only `/health`
also permits loopback probes. Forwarded headers do not grant access.

The `/api/v1` prefix is stable, but alpha response fields may grow. Existing fields will not be silently repurposed.
