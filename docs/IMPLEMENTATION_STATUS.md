# PilotSuite capability and acceptance ledger

## Alpha.36 candidate: consistent inventory snapshots

Reproduced and fixed stale snapshot promotion after reconnect, mixed freshness across
one inspection batch, and recommendations/previews surviving relevant catalog changes.
The catalog guard includes metadata and availability while allowing normal available
value changes. Repair preview refuses stale transport or changed catalog before any
plan persistence. Existing non-executable repair semantics and general Apply remain.
Seven new synthetic integration regressions cover the failures, HTTP 409, harmless
value changes and absence of context/plan/HA mutations. All 475 Python tests pass.
No household identifiers, configurations or live automations were modified.

Release/installation evidence remains separate in RELEASE_STATE.json. Alpha.35 was
freshly verified installed/offered/started before work; Alpha.36 is not yet delivered.
Next: complete exact candidate CI and the scoped-backup release gate, then deliver
and perform the available read-only acceptance for the saved Erdkellerbereich and
other existing zones. Authenticated UI acceptance must not be inferred from MCP.

## Repository contract integrity after Alpha.35

| Capability | Delivered scope |
|---|---|
| API inventory | All 48 registered `/api/v1` method/path pairs grouped by semantic owner |
| Effect clarity | Inspection, preview, persistence, restore and apply described separately |
| Drift guard | Dependency-free exact set check of explicit routes against `docs/API.md` |
| Runtime impact | None: no endpoint, payload, app tree, version, option or installation change |
| Local regression | Validator plus 468 Python and 56 JavaScript tests pass |

Final remote CI remains the merge gate. The installed Alpha.35 receipt is unchanged.

## Installed Alpha.35 — cumulative inventory integrity

| Capability | Delivered scope |
|---|---|
| Package continuity | Same-zone/revision results accumulate across explicit batches of at most eight |
| Completeness view | Exact requested/total progress plus readable and unreadable counts |
| Integrity filters | References, trigger IDs, unreadable and all-readable; deterministic order |
| Draft continuity | Unsaved role choices and explicit replacement selections remain intact |
| Conservative invalidation | Reload, zone/revision change or invalidation discards transient results |
| Persistence/control | None added; no queue, automatic scan, repair execution or HA write |
| Regression | Ten synthetic automations, two batches, one unreadable config, no mutations |

PR 76 release faf3611; candidate CI 36267009996 and main CI 36267117823 passed all
four jobs. Backup c194bc96 contains only Alpha.34 app/data/options. Alpha.35 is
installed/offered/started with unchanged options/auto_update and healthy readiness.
Authenticated Alpha.35 Ingress remains open; see RELEASE_STATE.json.

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
