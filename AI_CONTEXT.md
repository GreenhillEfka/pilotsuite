# PilotSuite AI context

Canonical repository: `GreenhillEfka/pilotsuite`. Home Assistant app:
`0d79c5e8_pilotsuite`. Architecture: v23.

Read `CURRENT_STATE.md`, `docs/RELEASE_STATE.json`, `docs/RELEASE_RUNBOOK.md`,
`DECISIONS.md`, `docs/VISION.md` and `docs/ROADMAP.md` before changing code or deploying.

## Live release

Alpha.50 is merged, published and installed from main commit
`9aea467a81fcdbd9fc96a0199cb2a1c57826702b`. The exact candidate and final main CI each
passed all five jobs. Scoped rollback backup `c31afe38` contains only PilotSuite Alpha.49
and was verified with native `backup/details` before Store refresh and installation.

Live status: started in `presence_adoption_review`; ready, HA event stream connected,
snapshot fresh and zone resolved. All four Supervisor options and `auto_update` are
unchanged. Do not redeploy Alpha.49 merely to update documentation.

Alpha.50 delivers the Alpha.49 zone presence configurator plus receipt-bound restart
recovery for its owned output package. The implementation keeps one zone/store owner.
It does not provide general technical entity-ID migration, automatic takeover of
existing helpers/automations, adaptive comfort learning or a general device execution
grant.

Current regression counts are 560 Python, 68 JavaScript and 62 API/repository contracts.
Creation and registry evidence are preserved cumulatively. Recovery resumes only an
already confirmed owned output transaction whose stable identifiers and exact zone
revision still match. A name-only or receipt-free match is never adopted or replayed;
a completed-but-unbound package can be bound after restart without recreation.

No authenticated HA browser session was available for household Ingress acceptance.
Direct app probing returned the intended `403 Ingress access required`; never bypass or
weaken it. No household helper, metadata, automation, consent or device state changed.

HA read-only inventory confirms the real `erdkeller` (`Erdkeller Innen`) and
`erdkeller_eingang` areas. They are inputs to the saved aggregate PilotSuite zone
`Erdkellerbereich`, not a reason to rename or split it automatically.

Next: perform authenticated read-only Ingress acceptance for saved `Erdkellerbereich`
and one unlike existing zone, confirming preservation of all four saved zones. Do not
apply household helper or metadata changes during that acceptance.
