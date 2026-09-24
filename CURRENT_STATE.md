# PilotSuite current state

## Active development — 2026-09-24

The user explicitly resumed the hourly autonomous development mandate; see
[DEVELOPMENT_MANDATE.md](docs/DEVELOPMENT_MANDATE.md). PR #52 on
`feat/review-compass-workspace` implements the next bounded package, **Alpha.23
Prüfkompass**, in the existing PlanStore and routine workbench. This replaces the
historical paused-task/next-slice instruction, not any household permission.

Five server-derived sections, one revalidated next step, transient zone filters,
accessible explanations and same-basis automation/note enrichment are integrated.
No new store, schema, learner or execution gate. The existing draft HEAD handler
is corrected to use the read-only path. Contract: docs/REVIEW_COMPASS.md.
Local canonical-code tests: **247 Python and 48 JavaScript passed**. Local browser
navigation is administratively blocked; no bypass attempted and no local browser
pass claimed. Exact candidate CI including the new full-app synthetic browser test
must be recorded in PR #52 before release. Local Python is 3.13; CI uses 3.14.

**Production remains Alpha.22, started, with no offered update at the entry read.**
No new backup, publication, installation, restart, HA configuration, automation,
actor, learning consent, permission or other-app change has occurred in this slice.
RELEASE_STATE.json remains the actual Alpha.22 receipt below, not a candidate claim.
Before a future merge: exact CI plus a fresh completed PilotSuite-only backup of
the then-installed version; follow RELEASE_RUNBOOK.md with auto_update unchanged.

Next: finish the exact PR #52 browser/CI and source review, then the existing scoped
backup and native Store release gates. Real authenticated UI, app configuration
read capability, independent data-preservation and useful real evidence remain
separate acceptance items. Do not repeat Alpha.22 installation.


## Verified Alpha.22 Store delivery — 2026-09-24

Canonical repository `GreenhillEfka/pilotsuite`; app `0d79c5e8_pilotsuite`.
**0.1.0-alpha.22 is published, installed and started through the normal Home
Assistant Store. Runtime checks passed. Authenticated live UI acceptance is pending.**
The existing PR #50 package was delivered without new implementation or versioning.

## Source and CI receipt

| Evidence | Verified value |
|---|---|
| PR #50 candidate | `ca6ba76f90c706cd3f7158aa07eec1605c81089a` |
| Published merge / pre-update main | `7990f5a3225aec53548dd8cb5bc79e74707b9fd9` |
| Candidate and published repository tree | `a73c3ada0695becd5823d1e0c386a06151cd5279` |
| Deployed version's application tree | `0d427053cdf246e63e044a11c15494f18dbeab08` |
| Exact candidate CI | [35928225010](https://github.com/GreenhillEfka/pilotsuite/actions/runs/35928225010), completed/success |
| Exact release main CI | [35929637405](https://github.com/GreenhillEfka/pilotsuite/actions/runs/35929637405), completed/success |

All three jobs passed on both exact runs: tests/contracts/source preflight, full-shell
and review-note-editor browser flows, and amd64 container build. The candidate log
confirms 215 Python and 28 JavaScript tests. All five version markers and both
changelogs identify alpha.22. The PR test merge tree was compared with the candidate;
the actual merge retained that same tree. Main was reread immediately before update.
No independent Supervisor checkout or installed-image attestation is claimed.
Browser tests/screenshots are synthetic, not an authenticated household UI receipt.

## Backup and native deployment receipt

The initial HA read confirmed alpha.21 installed/started, alpha.21 offered and
existing auto_update=true. The fresh PilotSuite-only backup **33908293** completed
before publication. Native details verified alpha.21, **54005760 bytes**, unprotected,
no HA configuration or database, no additional folders and no failed components.
Backup date: `2026-09-23T22:36:25.821711+00:00` (24 September in Europe/Berlin).
Scope/completion were verified through native metadata, not archive extraction or a
restore drill. PilotSuite health was checked after its normal backup lifecycle.

PR #50 was marked ready and merged with an expected-head guard, without force.
After the exact release main CI passed, the normal Store still offered alpha.21.
One native `ha_manage_app(action="check_updates")` without slug/repository changed
only PilotSuite's offered version to alpha.22. Fresh metadata confirmed the offer.
Exactly one `ha_manage_app(action="update", slug="0d79c5e8_pilotsuite")` completed.
No separate restart/rebuild or second installation was requested.

Post-update metadata confirms installed/offered alpha.22, state started and
update_available=false. Startup logs confirm alpha.22 / architecture v21 /
hard_read_only. Readiness, connected stream, fresh snapshot and resolved zone passed.
Presence and light capabilities remain partial as before the update; other observed
capabilities are unchanged. This is not a physical-sensor freshness guarantee.
Options were compared before/after and match; auto_update remains true.
No HA configuration, automation, actor, learning consent, permission or other app
was changed. No custom bridge or alternate deployment route was used.

RELEASE_STATE.json records the scoped alpha.21 rollback basis `33908293`.
The older backup `ae7a3fba` contains alpha.18 and is not this update's recovery point.
Recovery was not needed or performed.

## Delivered package and next boundary

ADR-030 / REVIEW_NOTES.md: PlanStore-owned, revision-bound shared review notes,
reference/config fingerprints, stale views, explicit selected reinspection and
schema-8 migration after a SQLite backup. REVIEW_NOTES_USABILITY.md: independent
assessment/freshness counts, direct selected recheck, conservative editor reset
and saved-text conflict comparison. No autosave or inferred action approval.
Notes remain separate from evidence, preference, risk, consent and execution.
Apply remains denied. Migration-preservation tests passed synthetically; an
independent live database/data-preservation inspection was not performed.

If live metadata still reports alpha.22 installed, do not repeat backup, update,
rebuild or restart. Pending: authenticated actual Ingress assets/API and note/editor
workflow, existing app config-read capability without escalating rights, Recorder
coverage, reconnect soak and traceable real habits. No extra consent or household
scan is authorized by this receipt. A future compact derived review-requirements
summary is not implemented here and would not be an execution authorization gate.
Do not automatically resume a paused development task.

This handoff changes only documentation outside the application directory. Its
exact PR/final-main CI receipt belongs in the handoff PR conversation; no further
release or repeated deployment is required for recording that result.
Previous candidate ledgers remain at `ca6ba76` and earlier commits. Older full history
remains in CURRENT_STATE_HISTORY_2026-09-23.md and
 docs/IMPLEMENTATION_HISTORY_2026-09-23.md. Follow RELEASE_RUNBOOK.md for future releases.
