# Home Assistant compatibility

PilotSuite `0.1.0-alpha.8` targets Home Assistant Core `2026.9.3` and the 2026 Supervisor App format.

Implementation choices:

- current terminology is **App**; user-facing references may add “Add-on” for familiarity;
- `repository.yaml` is at the repository root;
- the Dockerfile is the single build source; no deprecated `build.yaml`;
- multi-architecture `ghcr.io/home-assistant/base-python` image;
- `SUPERVISOR_TOKEN` bearer authentication;
- Core API proxy at `http://supervisor/core/api`;
- WebSocket proxy at `ws://supervisor/core/websocket`;
- Ingress on port `8099`;
- `/data` for app-owned persistent state;
- no direct `.storage` or Home Assistant YAML access.
