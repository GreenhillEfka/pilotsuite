# Installation and read-only acceptance

## Requirements

Home Assistant OS or Supervised with the Apps panel; supported app architectures
are `amd64` and `aarch64`. The declared minimum HA version is in
[`pilotsuite/config.yaml`](../pilotsuite/config.yaml); declaration is not proof of
testing every HA version or architecture.

## First installation

1. Add `https://github.com/GreenhillEfka/pilotsuite` in the App Store's repository settings.
2. Install PilotSuite and review its options.
3. Set `golden_zone_area_ids` only for the initial bootstrap from actual HA area IDs.
4. Start the app and open its authenticated Ingress UI.

After bootstrap, the saved PilotSuite zones are authoritative. Do not split an
aggregate zone into HA areas or recreate existing zones from option values.
An existing installation uses [RELEASE_RUNBOOK.md](RELEASE_RUNBOOK.md), not these
first-install steps. Do not reinstall an already installed release.

## Acceptance without household writes

- Compare installed/offered metadata with the intended source/version receipt.
- Check startup/readiness, stream connection, projection freshness and zone resolution.
  A ready connection does not prove physical sensor coverage.
- In authenticated Ingress, confirm existing zones, current values, unknown states,
  open sections, focus and reading position after multiple passive refreshes.
- Keep presence calculation, an optional HA comparison and output publication distinct.
- Do not create helpers, rename entities, change learning fields, press Apply or
  switch devices to prove installation.

An internal HTTP response is not browser acceptance. Direct access returning
`403 Ingress access required` is expected; never weaken that boundary.
No browser session means that specific acceptance remains pending.

## Data preservation and recovery

The app can own zones, selections, evidence, drafts, configuration and transaction
receipts. Removing its data is destructive, not a routine rollback. Separately
created HA helpers or metadata changes are not automatically undone by uninstalling.

Before a behavioral release, verify the documented native PilotSuite-only backup.
A restore overwrites app data/options since that backup and requires the authorized,
scope-checked recovery procedure. Local configuration savepoints are not a substitute
for the complete app/data backup. See the release runbook; do not test restoration
against the household.
