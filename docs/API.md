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

## API stability

### alpha.3 contract change

Suggestion `confidence` is now nullable: deterministic climate rules return null
instead of an uncalibrated number. New `severity` contains rule strength, not a
probability. IDs are stable for the versioned rule and normalized scope.
Status adds `ready`, `event_stream_connected`, `snapshot_fresh`, and
`missing_required_kinds`. Readiness requires the stream, a recent snapshot, a
resolved scope and valid temperature/humidity inputs. It does not certify physical
sensor freshness. All UI/API calls require the Ingress TCP peer; only `/health`
also permits loopback probes. Forwarded headers do not grant access.

The `/api/v1` prefix is stable, but alpha response fields may grow. Existing fields will not be silently repurposed.
