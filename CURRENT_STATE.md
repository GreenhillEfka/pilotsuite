# Current state — Alpha.49 delivered

Alpha.49 is merged at `dde31b82fc0829a96f7d058f25c62be9c0641574`, published and installed.
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

Next: perform authenticated read-only Ingress acceptance for saved `Erdkellerbereich`
and one unlike existing zone, confirming four-zone preservation, refresh recovery,
history gaps and ontology preview without applying household changes.
