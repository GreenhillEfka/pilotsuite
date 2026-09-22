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
  "message": "0.1.0-alpha.1 cannot execute Home Assistant mutations",
  "request_id": "..."
}
```

## API stability

The `/api/v1` prefix is stable, but alpha response fields may grow. Existing fields will not be silently repurposed.

