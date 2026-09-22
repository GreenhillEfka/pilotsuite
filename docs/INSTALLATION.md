# Installation and first validation

## Requirements

- Home Assistant OS or Supervised with the Apps panel
- `amd64` or `aarch64`
- access to the private GitHub repository
- Home Assistant 2026.4.0 or newer

## Install

1. In Home Assistant, open **Settings -> Apps -> App store**.
2. Open repository management and add `https://github.com/GreenhillEfka/pilotsuite`.
3. Refresh the store if PilotSuite is not shown immediately.
4. Install **PilotSuite**.
5. In configuration, set `golden_zone_area_ids` to the exact Home Assistant area ID for the Erdkeller if it differs from `erdkeller`.
6. Start the app and open its Web UI.

## Acceptance check for 0.1.0-alpha.1

- the app reaches `running` without restart loops;
- `/health` reports `ok`;
- `/health/ready` reports Home Assistant connected;
- the status page shows version `0.1.0-alpha.1` and architecture `v21`;
- the Erdkeller area resolves and lists only its Home Assistant entities;
- moods and suggestions contain readable evidence;
- an Apply request is rejected with HTTP `409`;
- no Home Assistant state or configuration changes.

## Rollback

This release makes no Home Assistant configuration changes. Stop and uninstall the app to remove the runtime. Removing app data deletes only PilotSuite-owned audit and plan records.

