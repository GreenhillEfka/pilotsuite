# PilotSuite capability and acceptance ledger

## Alpha.35 candidate — cumulative inventory integrity

| Capability | Candidate scope |
|---|---|
| Package continuity | Same-zone/revision results accumulate across explicit batches of at most eight |
| Completeness view | Exact requested/total progress plus readable and unreadable counts |
| Integrity filters | References, trigger IDs, unreadable and all-readable; deterministic order |
| Draft continuity | Unsaved role choices and explicit replacement selections remain intact |
| Conservative invalidation | Reload, zone/revision change or invalidation discards transient results |
| Persistence/control | None added; no queue, automatic scan, repair execution or HA write |
| Regression | Ten synthetic automations, two batches, one unreadable config, no mutations |

RELEASE_STATE remains the installed Alpha.34 receipt until source, CI, backup, Store,
runtime and live acceptance are completed separately.

## Installed Alpha.34 — 2026-09-26

PR 74, release 20adb0e; exact source/CI/backup/runtime receipt: RELEASE_STATE.json.

| Capability | Actual scope |
|---|---|
| Trigger integrity | Shared bounded projection in inventory and routine details; paths/counts only |
| ID cases | Missing/partial/matched/disabled/inactive/unknown; implicit indices and shared IDs |
| Honest limits | No flow/safety proof; unreferenced is not unused; dynamic/blueprint cases remain open |
| Review UI | Shared safe text, keyboard/mobile, unsaved selections retained, explicit reads only |
| Inventory recovery | Alpha.33 response isolation/read-only reconciliation preserved |
| Canonical persistence | ContextStore/PlanStore unchanged; no new store, schema or learner |
| Repair execution | Unavailable; review creates no HA write or approval |
| Existing naming executor | Unchanged and not invoked; technical-ID migration still blocked |
| Tests | 468 Python / 56 JS; 14 new Python regressions; nine CI browser suites |
| CI | Exact candidate and release-main all four jobs passed, amd64 included |
| Installation | Alpha.34 installed/offered/started; options/auto_update unchanged |
| Runtime | Ready, stream connected, snapshot fresh, zone resolved; mode unchanged |
| Household acceptance | Authenticated Ingress, app-principal rights, independent image/data checks remain open |

Backup 09436e7c verified before publication: Alpha.33 app/data/options only, no HA/DB/
folders or failed parts. One Store refresh/update, no extra restart or household edits.
HA-wide development reads are authorized independently of productive learning consent.
Four existing zones are user-confirmed; saved identities cannot be inferred from labels.

Next: read-only acceptance of integrity findings against the four existing saved
zones, starting with Erdkellerbereich.
