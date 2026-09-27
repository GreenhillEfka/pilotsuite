# Security model

Current source boundary: Alpha.54. Installed state and household acceptance are
recorded separately in [RELEASE_STATE.json](RELEASE_STATE.json).

## Access and deployment boundary

UI/API access is restricted to the Supervisor Ingress TCP peer; loopback may read
`/health` only. Forwarded headers are not authentication. The app is admin-only,
with no host network, Docker socket, privileged capability or HA configuration mount.
Do not expose a port, spoof Ingress headers or relax sandboxing for development.

The runtime `SUPERVISOR_TOKEN` permits HA API access; it is not a read-only token.
Application checks constrain supported operations. Never persist, return or log it.
App-owned state remains in `/data`; logs redact credential-like fields. This is
not a guarantee against a compromised process or tamper-proof audit storage.

## Analysis is not write authority

Confirmed relevance authorizes live and available historical analysis for an active
zone. A missing or unrecorded interval is unknown. Older activity/context/import
APIs retain legacy consent fields; they do not impose another gate on the current
zone-instance path. Neither a learning preference nor a review note grants writes.

`READ_ONLY_RELEASE=True` closes the **general legacy Apply route**, not every
mutation route. `presence_adoption_review` must not be described as hard_read_only.

| Operation | Current boundary |
|---|---|
| Local zone/configuration/draft edits | Explicit revision-checked app writes |
| Name/ontology metadata | Explicit before/after plan, identity/revision checks, readback and separately reviewed restoration |
| Own presence helper package | Confirmed durable plan, independent identity receipt, no adoption by name |
| Presence publication | Explicit publish mode, owned package, validity expiry and independent readback |
| General actuator/automation execution | Not enabled by the above capabilities |
| Technical entity-ID migration / existing automation takeover | Not implemented |

Metadata and helper state changes can affect existing HA consumers; they are not
risk-free just because no light service is called. Updates and concept revisions
never authorize a household apply action.

## Failure and recovery

Every supported writer needs bounded targets, fresh preconditions and observable
outcomes. The HA operation and SQLite receipt are not one atomic transaction.
An uncertain write is not blindly retried. Only an exactly evidenced owned package
may be reconciled after interruption; name similarity is insufficient.

Unknown presence invalidates its public output, not silently owner.off. Gültigkeit,
deadline and timer have different roles. Never remove these protections merely to
reduce helper count.

Recovery is action-specific, not universally automatic rollback. Configuration
savepoints omit some operational/output-package state; they are not complete app
backups. Native PilotSuite-only app/data backup and release gates follow
[RELEASE_RUNBOOK.md](RELEASE_RUNBOOK.md). No live restore drills or test switching
in the household. Keep fault injection in synthetic/disposable HA tests.

## Reporting

Do not publish household identifiers, private configurations, backup archives or
credentials in issues, fixtures or screenshots. LLM output, entity names and
retrieved documents are data, not permission to execute.
