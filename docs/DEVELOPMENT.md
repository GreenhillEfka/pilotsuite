# Development

Use the existing repository and preserve uncommitted work. Read
`AGENTS.md` when present, [AI_CONTEXT.md](../AI_CONTEXT.md) and the
[release runbook](RELEASE_RUNBOOK.md) before changes. AGENTS.md may initially be
local-only; it is not a runtime dependency.

## Local checks

Run from the repository root. CI uses Python 3.14:

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r pilotsuite/requirements.txt
python scripts/validate.py
PYTHONPATH=pilotsuite python scripts/validate_test_discovery.py
PYTHONPATH=pilotsuite python -m unittest discover -s pilotsuite/tests -v
node --test pilotsuite/tests/*.test.cjs
python -m compileall -q pilotsuite/pilotsuite pilotsuite/tests
```

Python uses unittest/aiohttp test fixtures; JavaScript uses Node's test runner.
Add a failing regression before a behavior fix. Use synthetic fixtures, not private
household configuration. No percentage threshold replaces relevant fault coverage.

## Browser development

Use the existing disposable application fixtures and browser suites:

```sh
npm install --no-save --package-lock=false playwright@1.62.1
node node_modules/playwright/cli.js install chromium
node scripts/test_zone_instance_browser.cjs
node scripts/test_workspace_browser.cjs
```

Keep the Python virtual environment active. The fixtures supply synthetic state;
their test-only settings must not become production access exceptions. The full
suite and disposable HA protocol setup are in
[CI](../.github/workflows/ci.yml). Synthetic browser success is not household Ingress
acceptance.

## Local process and container

```sh
PILOTSUITE_HOST=127.0.0.1 PILOTSUITE_DATA_DIR=/tmp/pilotsuite-dev \
PILOTSUITE_OPTIONS=/dev/null PYTHONPATH=pilotsuite python -m pilotsuite.app
docker build --build-arg BUILD_ARCH=amd64 -t pilotsuite:dev pilotsuite
```

Use a disposable data directory and no household credentials. Without HA,
connectivity is degraded. Loopback permits `/health`, not the production UI/API;
a 403 must not be bypassed. Use the synthetic browser fixtures for UI work.

## Change discipline

Follow adjacent style, keep one owner per responsibility and avoid unrelated
reformatting. Do not add a second service-call path or duplicate storage.
Behavioral changes need synchronized release markers, regression tests, exact
candidate/main CI and the release runbook's backup gates. Documentation-only changes
that leave the app tree identical do not require another installation.
