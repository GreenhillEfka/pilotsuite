# Current state — Alpha.51 delivered

Alpha.51 is the delivered bounded automation-reference integrity correction. The authorized
read-only inventory showed a real existing automation whose static source constraint is
stored as `event_data.entity_id`. PilotSuite's discovery found that automation, while
the existing draft inspector did not recognize the nested literal and could report a
contradictory source gap. The inspector now includes that exact trigger filter only.
Action event payloads remain opaque, and dynamic filters remain unresolved without
exposing authored text. No household configuration was copied into tests or source.

Local checks pass 562 Python tests, 68 JavaScript tests, Python compilation and 62
repository/API contracts. Exact candidate commit `2d4b771` and final main commit
`5250c6b` passed all five CI jobs. The packaged documentation now states only its own
version; actual delivery remains owned by `docs/RELEASE_STATE.json`.

Alpha.50 was the previous installed release. Its owned-package recovery boundary remains
unchanged in Alpha.51.
The exact candidate and final main commit passed all five CI jobs: unit/contract tests,
amd64 container build, reproducible source checkout, disposable Home Assistant protocol
and the complete Chromium application flow.

The package adds the existing-workspace zone presence configurator, relevance-authorized
history and ontology previews described in `docs/ZONE_INSTANCE_V2.md`. It keeps the one
canonical zone/store ownership model. No new learning engine, queue or shadow
configuration was introduced.

During integrated browser acceptance, five real defects were fixed: stale revision bases
after save and cancel, global-refresh races leaving actionable stale controls, missing
stable accessible labels, an invalid empty entity default, and an incomplete HA refresh
fixture. Regression coverage now exercises the full refresh/lock/recovery path.

The live app starts in `presence_adoption_review`, reports ready transport, connected
event stream, fresh snapshot and resolved zone. Its four Supervisor options and
`auto_update` remained unchanged. No household helper, metadata, automation, consent or
device state was changed. The scoped pre-release backup and exact delivery evidence are
in `docs/RELEASE_STATE.json`.

Authenticated household Ingress was not independently observable because no signed-in
browser session was available. Direct app access correctly rejected the probe with
`403 Ingress access required`; that protection was not bypassed.

Alpha.50 closes a restart-integrity gap in owned output packages. Durable
receipts now retain both the HA creation identifier and independent registry identity.
After an interrupted confirmed transaction, only exactly evidenced owned outputs can be
reconciled; pending steps can then continue and a fully created package can be bound
without replaying creation. Name similarity never proves ownership, and an unknown
outcome without receipt remains blocked. Final binding rechecks zone revision and every
output identity. No household helper or other HA object was used for these tests.

Local checks passed 560 Python and 68 JavaScript tests plus repository compile/diff and
62 API/repository contracts. Exact PR and final main CI passed all five jobs. Backup
`c31afe38` contains only Alpha.49 app/data/options. Store refresh exposed Alpha.50, one
update installed it, and logs confirm `presence_adoption_review`, ready transport,
connected stream, fresh snapshot and resolved zone. Options remain unchanged.

HA read-only inventory still exposes the real `erdkeller` (`Erdkeller Innen`) and
`erdkeller_eingang` areas used by the saved aggregate `Erdkellerbereich`. Authenticated
Ingress remains unavailable in this session, so preservation of all four saved zones is
not claimed from an internal HTTP response.

Alpha.51 is installed and started. Fresh backup `ca634a6c` contains only Alpha.50
app/data/options. Logs confirm version Alpha.51, `presence_adoption_review`, connected
stream, fresh snapshot and resolved zone. Options and `auto_update` remain unchanged.
Direct proxy reads still correctly return `403 Ingress access required`; protection was
not weakened and all four saved zones are therefore not claimed from internal HTTP.

Next: authenticated read-only Ingress acceptance of `Erdkellerbereich` and one unlike
existing zone, confirming all four saved zones and the corrected event-filter source
explanation without any household apply action.
