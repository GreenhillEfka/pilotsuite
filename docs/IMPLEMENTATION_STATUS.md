# PilotSuite capability and acceptance ledger

## Installed Alpha.27 — 2026-09-25

Exact source, CI, backup and installation receipt: RELEASE_STATE.json. Existing PR61
is merged and delivered. Broader Issue56 remains open; no helper executor is enabled.

| Capability | Scope |
|---|---|
| Existing roles, zones, history, daily brief, drafts/notes | Retained baseline; learning remains scoped and opt-in |
| Zonenbasis UI | German planning cards, missing/unknown/conflict states; no readiness-as-permission |
| Explicit automation import | Transient read-only API; bounded fingerprint/static-reference limitations |
| Versions and native install handoff | Three bundled release notes, cached exact-identity HA update state; no self-update/downgrade/history claims |
| Local configuration savepoints | Checksummed private files; exact preview/basis confirmation; before-point, SQLite rollback, paused restore and idempotent receipt |
| Restored data boundaries | Saved zone configuration only; consents cleared; newer additional zones, evidence and review text preserved |
| Database-startup rescue | Guarded maintenance view; original database retained, no HA processing or automatic recovery |
| Existing helper inspection | Explicit bounded storage reads by immutable identity; renamed IDs and timer restore warnings; no creation/adoption/ownership |
| Groups/templates/YAML helper configuration | Not falsely verified by storage collection inspection |
| Golden Zone option | First-start bootstrap relabel only; values and live zones unchanged |
| HA helper generation / timer runtime / takeover | Not implemented or enabled |
| Exact candidate and main CI | All four jobs passed, seven browser steps and amd64 build; 386 local Python / 48 JS |
| Runtime acceptance | Installed/offered27, started, hard_read_only, repeated ready/stream/freshness/zone verified |
| Household browser / helper reads under app principal | Pending; one native maintenance GET returned403, no route retry or bypass |
| Household restore / demonstrated comfort gain | Not performed or proven by synthetic CI |

Scope and recovery limitations: MAINTENANCE_AND_RECOVERY.md. Local savepoints are not
native app backups and cannot repair corrupt SQLite or restore old app binaries.
The release used one completed PilotSuite-only native backup, one Store refresh and
one update; no additional restart or household changes. All options unchanged.

Checksum-verified synthetic maintenance screenshots at390/1440 were visually reviewed.
Remote actual-app browser tests passed; neither is authenticated household acceptance.
Module reference overlap does not establish execution ownership; fingerprints describe
one read, not perpetual validity. No new learning/authority follows inspection.

Next: ONE actual bounded helper executor in existing PlanStore with full application
and UI integration, restart/timeout/conflict tests and action-specific recovery in
disposable HA before household writes. Do not claim cross-system atomicity. Presence
timing and controlled existing-automation adoption follow that capability. Refine the
prior narrow foundation-card German wrapping during the next behavioral version.
