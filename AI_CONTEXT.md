# PilotSuite AI Context

Canonical: GreenhillEfka/pilotsuite / HA app 0d79c5e8_pilotsuite / architecture v21.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first.

## Resume — Alpha.27 delivered, 2026-09-25

Existing PR61 merged as f7b3267a3f2785433c1ca5048a180a8a24f45d3b. Exact candidate
CI36184691444 and main CI36193063595 passed all four jobs, including seven browser
steps. Fresh PilotSuite-only backup74c7be8d completed and was verified BEFORE
publication. One native check_updates, one PilotSuite update; no extra restart.
Alpha.27 is installed/offered/started, with hard_read_only startup and repeated
ready/connected/fresh/zone-resolved logs. All options and auto_update=true unchanged.
No other app, household configuration, roles or learning permission changed.
Do not repeat backup/update/rebuild/restart or connector configuration to resume.
Full identities and acceptance boundaries are in RELEASE_STATE.json.

## What this release actually adds

Existing maintenance service/UI: last three bundled package release notes and
cached exact-identity HA update status, with a native installation handoff. These
are not three installed versions, a self-updater or a downgrade selector.
PlanStore owns private checksummed zone-configuration savepoints and explicit
hash-bound restore with a before-point, SQLite rollback and idempotent receipt.
Restored zones are paused and learning consents cleared; newer additional zones
and existing evidence/review text survive. Detected database startup failure serves
an Ingress-guarded rescue view without overwriting the database. Explicit existing
storage-helper inspection handles renamed IDs and timer restore settings, never
creation/adoption or ownership by name. Bootstrap option labels, not values, changed.
Scope: docs/MAINTENANCE_AND_RECOVERY.md and IMPLEMENTATION_STATUS.md.

## Acceptance still separate

386 Python and 48 JavaScript tests rerun locally. Exact remote CI used the declared
runtime dependencies; maintenance screenshots at390/1440 were checksum-verified and
visually reviewed. This is synthetic actual-app testing, not household Ingress.
One native GET /api/v1/maintenance returned403, Ingress access required; route stopped
without retries, header/port/peer changes or weakened authentication. Authenticated
household browser and the app principal's helper-collection capability remain
unverified. No household savepoint restore or live disaster-recovery drill occurred.
Source/version/app-tree association is not independent installed-image attestation.
Partial humidity/motion/presence/light capabilities are not transport failures.

## Invariants and next implementation

HA owns device execution. PilotSuite owns zones/roles/bounded evidence and review
intent through existing ContextStore/PlanStore; no second learner or store. No
implicit learning, unscoped writes, guessed replacements or inferred ownership.
Preserve manual overrides, unknown original config fields and existing identities.
Registry absence cannot prove helper-collection absence. No HA .storage edits,
Ingress bypass or credentials/household data in public code, logs or handoffs.

Issue56 remains open: implement ONE actual bounded helper executor in the existing
PlanStore mutation path, with scoped plan/approval, before-image, apply, independent
read-back and action-specific recovery. Test timeout, lost response, restart and
concurrent edits in disposable HA before household writes. HA and SQLite are not
one atomic transaction; never blindly replay an unknown-outcome write or delete
pre-existing helpers. Complete UI-to-application integration before claiming
provisioned zones. Then presence timing and controlled existing-automation adoption.
Alpha.27 does not operate presence timers or light/music/climate controllers.
Refine narrow foundation-card German wrapping within the next behavioral version.

Keep a complete checkout, compile application AND tests, run full local tests before
one pinned change set, then exact remote CI and the unchanged release runbook.
Documentation-only handoffs do not justify another release. Final documentation CI
receipts belong in PR comments, not another status-only commit loop.
