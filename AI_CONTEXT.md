# PilotSuite AI context

Canonical repository: `GreenhillEfka/pilotsuite`. Home Assistant app:
`0d79c5e8_pilotsuite`. Architecture: v23.

Read `CURRENT_STATE.md`, `docs/RELEASE_STATE.json`, `docs/RELEASE_RUNBOOK.md`,
`DECISIONS.md`, `docs/VISION.md` and `docs/ROADMAP.md` before changing code or deploying.

## Live release

Alpha.52 is merged, published and installed from main commit
`72820d46bf7a6bdd921ca1216be8f29f87992fcd`. The exact candidate and final main CI each
passed all five jobs. Scoped rollback backup `97450786` contains only PilotSuite Alpha.51
and was verified with native `backup/details` before Store refresh and installation.

Live status: started in `presence_adoption_review`; ready, HA event stream connected,
snapshot fresh and zone resolved. All four Supervisor options and `auto_update` are
unchanged. Do not redeploy Alpha.51 merely to update documentation.

Alpha.52 corrects one automation-review integrity gap: disabled or dynamically enabled
steps remain visible but no longer satisfy confirmed source/target alignment.
Availability is inherited through nested branches, the UI explains the distinction,
and presence adoption consumes the same confirmed projection. It keeps the one
zone/store owner and adds no takeover, adaptive learning or device execution.

Current regression counts are 567 Python, 68 JavaScript and 62 API/repository contracts.

No authenticated HA browser session was available for household Ingress acceptance.
Direct app probing returned the intended `403 Ingress access required`; never bypass or
weaken it. No household helper, metadata, automation, consent or device state changed.

HA read-only inventory confirms the real `erdkeller` (`Erdkeller Innen`) and
`erdkeller_eingang` areas. They are inputs to the saved aggregate PilotSuite zone
`Erdkellerbereich`, not a reason to rename or split it automatically.

Next: perform authenticated read-only Ingress acceptance for saved `Erdkellerbereich`
and one unlike existing zone, confirming all four saved zones and the distinct
active/disabled/dynamic-unknown reference explanations without household changes.
