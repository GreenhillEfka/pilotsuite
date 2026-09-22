# Development

## Local tests

The domain core uses the Python standard library. Run:

```bash
python -m unittest discover -s pilotsuite/tests -v
```

## Local server without Home Assistant

```bash
cd pilotsuite
PILOTSUITE_DATA_DIR=/tmp/pilotsuite-data \
PILOTSUITE_OPTIONS=/dev/null \
python -m pilotsuite.app
```

The UI starts on `http://localhost:8099`. Home Assistant connectivity is degraded, while liveness remains healthy.

## Container build

```bash
docker build -t pilotsuite:0.1.0-alpha.6 pilotsuite
docker run --rm -p 8099:8099 \
  -e PILOTSUITE_DATA_DIR=/tmp/data \
  pilotsuite:0.1.0-alpha.6
```

## Contribution rules

- update `CURRENT_STATE.md` with reality, not intent;
- record irreversible or structural decisions in `DECISIONS.md`;
- keep `VERSION` and `pilotsuite/config.yaml` identical;
- add tests for every deterministic rule;
- never introduce a second service-call path;
- never log Supervisor credentials or raw authorization headers;
- keep HA entity selection registry- and area-based.
