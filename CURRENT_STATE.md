# PilotSuite current state

## Review-note development candidate — 2026-09-23

Canonical project: `GreenhillEfka/pilotsuite`; app `0d79c5e8_pilotsuite`.
Continue **draft PR #50**, branch `feat/revision-bound-review-notes`, not a new PR
or implementation. It adds persistent review notes in the existing PlanStore.
**Development branch only: not versioned, published, merged or installed.**
The unchanged alpha.21 version markers are not permission to deliver changed code
under that release number. Assign a new version before any delivery.

The candidate adds three user-authored dispositions, optional bounded text,
draft/zone/reference/config-fingerprint binding, conservative stale/unverified
views, explicit reinspection on save, conflict-safe deletion and JSON export.
Schema 8 adds one bounded table after the existing SQLite migration backup.
Learning evidence, preference, risk, consent and the denied apply path are unchanged.
Contract: [docs/REVIEW_NOTES.md](docs/REVIEW_NOTES.md), ADR-030.

## Validation and delivery gates

Six local Python validation/projection tests and seven JavaScript state tests pass;
Python compilation and JavaScript syntax checks pass. Full CI adds seventeen API,
PlanStore, migration and concurrency regressions plus a browser editor contract.
The first full run exercised all 215 Python tests: the 23 new cases passed, with
two legacy expected-schema assertions requiring 7-to-8 updates. All 16 JavaScript
tests, the existing full-shell Chromium flow and amd64 container passed that run.
The new standalone browser fixture needed an explicit UTF-8 document/asset charset;
its original document omitted this while using non-ASCII role names. Those test
corrections are in commit `26c20103a936379e556def62a079094fa97712df`.
Read **the latest exact HEAD CI and final receipt in PR #50**; earlier run results
are not a final green claim. Local synthetic Chromium navigation was environment-
blocked before execution; no local browser pass is claimed.

HA-MCP was not exposed by tool discovery in this continuation. No live HA metadata,
backup, Store refresh, update, Ingress session or household configuration was read
or changed. This is a current tool-availability observation, **not** a new rejection
of the known native Store routine and not evidence that HA permissions changed.
Do not retry the old denied custom bridge or request broader credentials.

Because the last verified app setting has auto_update enabled, keep this increment
off `main` until a fresh PilotSuite-only backup of the current installed release is
completed and its native details verified. The alpha.18 backup below is not a fresh
alpha.21 recovery point for this increment. Do not automatically merge this PR.

## Last verified deployed state — previous continuation

Alpha.21 was installed and started on 2026-09-23 through the normal Store update.
Release `1223f96f45053f7bf3d509bd7ad72c85b9f6cab1`, app tree
`3228fa2b5cae4d0db00dc7646aa6e39bb43b6b77`; release CI `35914643847` passed.
PR #49 merged the installation handoff at
`c3e87fb81a24267b8584f2d68df25bd8f9539aba`, the baseline for this development.
Native `ha_manage_app(action="check_updates")` had refreshed the alpha.21 offer.
Backup `ae7a3fba` contains the prior alpha.18 app/data/options, 53,964,800 bytes,
unprotected, no HA configuration/database/folders or failed components.
Exactly one update was followed by target version/start/hard_read_only/readiness,
connected stream, fresh snapshot and Golden Zone confirmation. No extra restart.
These are retained receipts, not live checks performed during this increment.
Machine-readable last deployment: [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).
Procedure: [docs/RELEASE_RUNBOOK.md](docs/RELEASE_RUNBOOK.md).

## Next concrete delivery task

Resume PR #50 and check its exact latest CI, fixing any remaining regression first.
When HA-MCP is available, reread current app/source metadata, make and verify the
fresh scoped backup, then assign the next unused release version, update all release
markers/changelogs, run release preflight and exact candidate CI. Recheck main/open
work, merge without force only after these gates, verify exact main CI, refresh the
Store only if needed and update once. No speculative restart or permission change.

Authenticated live temporal/draft/inspection/review-note UI, existing app
`automation/config` capability, Recorder coverage and real multi-day evidence remain
separate acceptance tasks. No automatic collection, real household scan or new
learning consent is part of development testing. The next concept slice after
review-note acceptance is a derived compact review summary with explicit missing
requirements, not another store or an execution permission.

## Preserved history

[CURRENT_STATE_HISTORY_2026-09-23.md](CURRENT_STATE_HISTORY_2026-09-23.md) contains the
complete older ledger, unchanged blob `1853f2444eb24315028c1f4a1c27c823afa84f28`.
Its old installed versions and blockers are historical. The prior compact alpha.21
handoff remains in baseline commit `c3e87fb81a24267b8584f2d68df25bd8f9539aba`.
