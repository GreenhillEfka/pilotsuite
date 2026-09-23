# PilotSuite current state

## Verified continuation — 2026-09-23

Canonical project: `GreenhillEfka/pilotsuite`; app: `0d79c5e8_pilotsuite`.
**Alpha.21 is now installed, offered and started.** The previous Store-offer
blocker is resolved. Do not install, rebuild, restart or create another pre-update
backup just to repeat this completed step. Read live metadata before continuing.

Machine-readable operational receipt: [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).
Release procedure: [docs/RELEASE_RUNBOOK.md](docs/RELEASE_RUNBOOK.md).
Capability ledger: [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md).

## Completed in this continuation

1. Read canonical context, vision, decisions, implementation and release records.
2. The native `ha_manage_app(action="check_updates")` succeeded without changing
   credentials or permissions. The offered version moved from alpha.18 to alpha.21.
   No denied custom Supervisor bridge was retried.
3. Verified release commit `1223f96f45053f7bf3d509bd7ad72c85b9f6cab1`, its successful
   CI run `35914643847`, current main `da0754e8d6b4689548d38a5a26c2755ea000aa1c`
   and successful main CI `35915002481`. Test, browser and container checks passed.
   The current main app tree remains `3228fa2b5cae4d0db00dc7646aa6e39bb43b6b77`.
   No open PRs or repository rulesets were returned at the pre-write read.
4. Created and verified fresh scoped backup `ae7a3fba`, dated
   `2026-09-23T20:41:17.662809+00:00`, size 53,964,800 bytes. Native `backup/details`
   confirms only alpha.18 PilotSuite, no failed components, no Home Assistant or
   database, no folders, and an unprotected local backup. Standard app backup
   covers its data/options; no archive extraction or live restore drill occurred.
5. Rechecked installed/offered versions and updated PilotSuite once through
   `ha_manage_app(action="update")`. No additional restart was requested.
6. Supervisor now reports installed/offered alpha.21, started, no update pending.
   Startup identifies alpha.21 and `hard_read_only`; subsequent readiness reports
   ready, connected stream, fresh snapshot and resolved Golden Zone. App options
   match the before-update read. No role, consent, HA configuration, automation,
   actuator, other app, Core, Supervisor or host change was requested.

Source association is canonical repository + offered version + verified unchanged
app tree, not independent Store checkout or installed-image attestation.

## Still pending — separate evidence, not an installation blocker

- Authenticated real HA Ingress acceptance of temporal views, routine drafts,
  reference review and selected automation inspection was not performed in this
  continuation. Synthetic Chromium CI is not that acceptance.
- The app's live `automation/config` read capability remains unverified. Never
  elevate privileges or weaken Ingress to make it pass.
- Existing user acceptance of alpha.16 guide/navigation/workbench and the reported
  history diagram rendering remain historical evidence, not alpha.21 acceptance.
- Extended Recorder coverage, reconnect soak and real multi-day habit acceptance
  remain separate from passing fixtures. No new learning consent was enabled.

## One concrete next development task

Implement explicit user-authored review notes in the existing PlanStore (ADR-029),
bound to the routine draft revision and selected automation configuration
fingerprint. Preserve notes but clearly mark them stale when either changes; an
unavailable or unverified live fingerprint must not be shown as current verification.
Keep evidence, user assessment and action permission separate. No note, checkbox or
export grants execution, creates an automation, imports evidence or changes consent.

Build one bounded increment with schema/migration backup, optimistic-concurrency,
persistence/restart, stale-state, invalid-input, export and browser tests. Reuse the
existing inspection and PlanStore owners, not a second approval or learning store.
Only a behavior-changing increment gets a new version and normal release gates.

## Historical receipts preserved without alteration

The former complete CURRENT_STATE.md is retained byte-for-byte as
[CURRENT_STATE_HISTORY_2026-09-23.md](CURRENT_STATE_HISTORY_2026-09-23.md), original
blob `1853f2444eb24315028c1f4a1c27c823afa84f28`. Its older versions, next steps and
blockers are dated history, not current instructions. No app code changed during
this documentation consolidation. Keep future current-state handoffs short and put
completed historical detail in the history rather than prepending endless receipts.
