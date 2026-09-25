# Alpha.26 release closure review — 2026-09-25

## Scope

This is a read-only preparation release, not the completed autonomous zone system.
No general service-call transport, helper creation, automatic takeover or additional
learning collection is enabled. Existing Alpha.25 data and configuration remain.

| Surface | Implemented | Not claimed |
|---|---|---|
| Zonenbasis UI | German preparation cards, conflicts/unknowns, invalidation on reload errors, zone changes and unsaved edits | A configured module is not an accepted controller |
| Explicit automation import API | Bound size/depth/JSON, original fingerprint and detached config, static entity references, indirect/template limitations, concurrency/revision checks | No auto scan, persisted import store or complete dependency analysis |
| Helper reconciliation | Global registry hints with inspect/conflict/unverified outcomes | Exact ID is not ownership; absence is not permission to create |
| Import/diff/transform primitives | Preserve unknown metadata; reject unsupported edits; explicit identity required for verification | No HA change, atomic takeover or validated behavior equivalence |
| Presence/lighting/media/climate | Preparatory model and isolated policy functions | No running timer, heating controller, music scheduler or newly learned correlations |
| Migration/responsibility prototypes | Unit-tested structural examples | Not an executed/persisted ledger; shared module mentions do not prove competing writers |

## Reproduced defects

The native GitHub job log 108083712840 pinpointed a literal newline in the import
test that had never actually been replaced. After the real fix, full local discovery
collected 341 tests and exposed the separate unknown-field diff bug. Neither error
was caused by timer namespace choices. Both are fixed without weakening their intent.
Release review adds 14 regression tests and one full-app browser script. Test files
are included in the compilation gate, not hidden behind application-only compile.

Local full tests use Python 3.13 and aiohttp 3.13.3; exact CI uses its pinned environment.
Local system Chromium refuses localhost navigation under administrator policy. That
restriction is not bypassed: no local full-shell browser pass is claimed. Offline
component checks remain distinct; exact remote full-app browser CI is required.

## Primary references and implications

- Home Assistant timer documentation: https://www.home-assistant.io/integrations/timer/
  Restore does not replay every missed timer.finished event. A future executor must
  reconcile current sources/deadlines after restart, not treat idle as proven vacancy.
- Home Assistant automation triggers: https://www.home-assistant.io/docs/automation/trigger/
  A for-duration does not survive reload/restart. It cannot alone meet durable presence
  timing requirements. No new household timer is enabled by this release.
- Home Assistant WebSocket API: https://developers.home-assistant.io/docs/api/websocket/
  Retain the existing event stream and bounded snapshot reconciliation; no shadow HA.

The prior Deep Research request is not an available completed report in this session.
No research-completion claim or new external dependency is made.

## Remaining gate

Exact candidate and main CI, fresh scoped backup before publication, native Store
version/source match, one update and runtime logs. Authenticated household Ingress
and demonstrated comfort benefit remain separate. RELEASE_RUNBOOK.md is unchanged.
