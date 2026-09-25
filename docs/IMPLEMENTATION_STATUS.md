# PilotSuite capability and acceptance ledger

## Alpha.26 candidate / installed Alpha.25

Current exact release and candidate identities: RELEASE_STATE.json. PR59 is frozen
for validation and delivery; no executor is enabled. See ALPHA26_RELEASE_REVIEW.md.

| Capability | Scope |
|---|---|
| Existing roles, zones, history, daily brief, drafts/notes | Retained from installed baseline; learning remains scoped and opt-in |
| Zonenbasis UI | Planning-only, German, missing-source/unknown/conflict display; no readiness-as-permission |
| Explicit automation import | Transient authenticated read-only API; bounded source, fingerprint, static references and limitations |
| Helper inventory hints | Global registry used for hints; config/ownership/absence remain unverified |
| Diff/transform/mapping/comfort primitives | Isolated preparatory functions; no durable adoption workflow or device effect |
| HA writes / helper generation / timer runtime | Not implemented or enabled in Alpha.26 |
| Current source/test validation | Full local suite plus exact PR/main CI required; not household acceptance |
| Real HA Ingress acceptance | Pending authenticated session; never spoof peers or expose an unauthenticated port |

Module reference overlap does not establish execution ownership. Configuration
fingerprints describe a particular read, not ongoing validity. Unknown or disabled
HA fields are preserved; no silent learning or authority escalation follows import.

Next: after this release, one bounded helper executor in existing PlanStore with
single-owner lifecycle, timeout/restart/conflict fault tests and action-specific
recovery. Implement its actual UI/application path before claiming provisioned zones.
