# PilotSuite AI context

Canonical repository: `GreenhillEfka/pilotsuite`. Home Assistant app:
`0d79c5e8_pilotsuite`. Architecture: v23.

Read `CURRENT_STATE.md`, `docs/RELEASE_STATE.json`, `docs/RELEASE_RUNBOOK.md`,
`DECISIONS.md`, `docs/VISION.md` and `docs/ROADMAP.md` before changing code or deploying.

## Live release

Alpha.53 is merged, published and installed from main commit
`8a46aaecf19deae1eae3d95b265fe46f3bb94e94` (PR #112). The exact candidate and
final main CI each passed all five jobs. Scoped rollback backup `94c7032e` contains
only PilotSuite Alpha.52 and was verified with native `backup/details` before Store
refresh and installation. See `docs/RELEASE_STATE.json` for the release receipt.

Live status: started in `presence_adoption_review`; ready, HA event stream connected,
snapshot fresh and zone resolved. All four Supervisor options and `auto_update` are
unchanged. Do not redeploy Alpha.51 merely to update documentation.

Alpha.53 stabilizes the reading position during passive context, zone, presence and
shadow updates; unchanged responses keep the DOM, focus and open details. The live
zone source list and trace are collapsible. See `docs/UI_REFRESH_REVIEW_2026-09-27.md`.
Alpha.52's automation availability distinction remains in place. Keep the one
zone/store owner; no takeover, adaptive learning or device execution was added.

Current regression counts are 567 Python, 70 JavaScript and 62 API/repository contracts.

No authenticated HA browser session was available for household Ingress acceptance.
Direct app probing returned the intended `403 Ingress access required`; never bypass or
weaken it. No household helper, metadata, automation, consent or device state changed.

HA read-only inventory confirms the real `erdkeller` (`Erdkeller Innen`) and
`erdkeller_eingang` areas. They are inputs to the saved aggregate PilotSuite zone
`Erdkellerbereich`, not a reason to rename or split it automatically.

Next: perform authenticated read-only Ingress acceptance for saved `Erdkellerbereich`
and one unlike existing zone after at least two passive refreshes: confirm the
reading position, open sections, focus, current values and all four saved zones.
Also confirm the active/disabled/dynamic-unknown reference explanations. Do not
change household configuration or perform an Apply action.
