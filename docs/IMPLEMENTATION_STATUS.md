# PilotSuite capability and acceptance ledger

## Installed Alpha.26 — 2026-09-25

Exact source, CI, backup and installation receipt: RELEASE_STATE.json. PR59 is
merged and delivered. The broader Issue56 remains open; no executor is enabled.

| Capability | Scope |
|---|---|
| Existing roles, zones, history, daily brief, drafts/notes | Retained baseline; learning remains scoped and opt-in |
| Zonenbasis UI | German planning cards; missing/unknown/conflict states; no readiness-as-permission |
| Explicit automation import | Transient authenticated read-only API; bounded source/fingerprint and static-reference limitations |
| Helper inventory hints | Global cached registry; config/ownership/absence remain unverified |
| Diff/transform/mapping/comfort primitives | Isolated preparations, not a durable adoption workflow or controller |
| HA helper generation / timer runtime / takeover | Not implemented or enabled in Alpha.26 |
| Exact candidate and main CI | All jobs passed, six browser steps and amd64 build; 355 local Python / 48 JS |
| Runtime acceptance | Installed26, started, hard_read_only, ready, stream/freshness/zone verified |
| Household Ingress / demonstrated comfort gain | Still separate and not verified by synthetic CI |

Module reference overlap does not establish execution ownership. Fingerprints describe
one read, not perpetual validity. No new learning or authority follows import. Synthetic
390/1440 screenshots were viewed; improve narrow-card German word wrapping next version.

Next: ONE actual bounded helper executor in existing PlanStore with full application
and UI integration, restart/timeout/conflict tests and action-specific recovery. Test
against disposable HA before household writes; do not claim cross-system atomicity.


## Alpha.27 candidate (not a deployment receipt)

Integrated maintenance/API/UI: three bundled version notes, authoritative cached
HA update-entity identity check, native installation link; local configuration
savepoint creation/preview/paused restore with private files, checksum, before-point,
transaction rollback and idempotent replay; guarded rescue page on DB bootstrap
failure; explicit inspection of existing storage helpers, never ownership by name.
Golden Zone bootstrap label fixed without changing option values or live zones.
Local 386 Python/48 JS passed; remote browser/deployment acceptance pending.
No HA provisioning or automation takeover enabled. Scope: MAINTENANCE_AND_RECOVERY.md.
