# PilotSuite AI context

Canonical repository: `GreenhillEfka/pilotsuite`. Home Assistant app:
`0d79c5e8_pilotsuite`. Architecture: v23.

Read `CURRENT_STATE.md`, `docs/RELEASE_STATE.json`, `docs/RELEASE_RUNBOOK.md`,
`DECISIONS.md`, `docs/VISION.md` and `docs/ROADMAP.md` before changing code or deploying.

## Live release

Alpha.49 is merged, published and installed from main commit
`dde31b82fc0829a96f7d058f25c62be9c0641574`. The exact candidate and final main CI each
passed all five jobs. Scoped rollback backup `f627af26` contains only PilotSuite Alpha.48
and was verified with native `backup/details` before publication.

Live status: started in `presence_adoption_review`; ready, HA event stream connected,
snapshot fresh and zone resolved. All four Supervisor options and `auto_update` are
unchanged. Do not redeploy Alpha.49 merely to update documentation.

Alpha.49 delivers the zone presence configurator, relevance-authorized history and
ontology review described in `docs/ZONE_INSTANCE_V2.md`. The implementation keeps one
zone/store owner. It does not provide general technical entity-ID migration, automatic
takeover of existing helpers/automations, adaptive comfort learning or a general device
execution grant.

Five integrated defects were fixed before release: stale save/cancel revision bases,
global-refresh stale-control races, missing stable accessible labels, an invalid empty
entity default and an incomplete synthetic HA refresh fixture. Current regression counts
are 556 Python, 68 JavaScript and 62 API/repository contracts.

No authenticated HA browser session was available for household Ingress acceptance.
Direct app probing returned the intended `403 Ingress access required`; never bypass or
weaken it. No household helper, metadata, automation, consent or device state changed.

Next: authenticated read-only Ingress acceptance for saved `Erdkellerbereich` and one
unlike existing zone. Verify all four saved zones remain present, refresh recovery,
history gaps, ontology preview and unsaved-input preservation. Do not apply household
changes during that acceptance.
