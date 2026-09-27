# PilotSuite AI context

Canonical repository: `GreenhillEfka/pilotsuite`. Home Assistant app:
`0d79c5e8_pilotsuite`. Architecture: v23.

Read `CURRENT_STATE.md`, `docs/RELEASE_STATE.json`, `docs/RELEASE_RUNBOOK.md`,
`DECISIONS.md`, `docs/VISION.md` and `docs/ROADMAP.md` before changing code or deploying.

## Live release

Alpha.51 is merged, published and installed from main commit
`5250c6b7ef6aaef3fb7a88f28b51fef23c051a67`. The exact candidate and final main CI each
passed all five jobs. Scoped rollback backup `ca634a6c` contains only PilotSuite Alpha.50
and was verified with native `backup/details` before Store refresh and installation.

Live status: started in `presence_adoption_review`; ready, HA event stream connected,
snapshot fresh and zone resolved. All four Supervisor options and `auto_update` are
unchanged. Do not redeploy Alpha.50 merely to update documentation.

Alpha.51 adds one bounded read-only integrity correction: a literal
`event_data.entity_id` on an event trigger is recognized as a direct source reference.
Action event payloads remain opaque; dynamic filters remain unknown. It keeps the one
zone/store owner and does not add takeover, adaptive learning or device execution.

Current regression counts are 562 Python, 68 JavaScript and 62 API/repository contracts.

No authenticated HA browser session was available for household Ingress acceptance.
Direct app probing returned the intended `403 Ingress access required`; never bypass or
weaken it. No household helper, metadata, automation, consent or device state changed.

HA read-only inventory confirms the real `erdkeller` (`Erdkeller Innen`) and
`erdkeller_eingang` areas. They are inputs to the saved aggregate PilotSuite zone
`Erdkellerbereich`, not a reason to rename or split it automatically.

Next: perform authenticated read-only Ingress acceptance for saved `Erdkellerbereich`
and one unlike existing zone. Confirm all four saved zones and the corrected static
event-filter source explanation without applying household changes.
