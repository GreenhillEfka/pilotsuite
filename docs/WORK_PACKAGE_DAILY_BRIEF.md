# Work package: zone daily brief / Alltagsbrief

Started 2026-09-24 at the user's explicit request after installing Alpha.23.
Canonical repository only. Branch: feat/zone-daily-brief. Starting main:
e214f1e38be3969ee7d8ba130e8ad5592e745fd2.

## Confirmed preceding delivery

Native HA-MCP installed 0.1.0-alpha.23 using exactly one ha_manage_app update.
Fresh PilotSuite-only backup 04725cd5 completed and backup/details verified
Alpha.22, 54,128,640 bytes, 2026-09-24T15:26:44.533466+00:00, no HA/database/folders,
empty failure lists and no encryption-key requirement. No archive download/restore.
The already offered target required no Store refresh. Metadata confirmed Alpha.23,
started, no pending update and unchanged options. Startup/readiness logs confirmed
hard_read_only, ready, connected stream, fresh snapshot and resolved Golden Zone.
Release CI 35991187908 and current-main CI 35996327515 succeeded. Main and release
app trees both equal 38ef81068ff75f135bce6734a43e2caca3c09b8c; source-only CI bundle
10806087279 was SHA256 verified. This is not an installed-image attestation.

One extra read of /health/ready through the native app proxy returned HTTP 403
Ingress access required. That route was stopped; no headers, ports, peers, rights
or credentials were changed. Authenticated live UI acceptance and independent
persisted-data inspection remain pending. Logs expose presence/light completeness
as partial; ready is a transport condition, not complete physical observations.

## Goal

One understandable brief for the selected zone: current observations, an existing
review candidate when its basis supports one, and explicit reasons when no useful
recommendation is justified. Comfort benefit before more review administration.
This package must not claim demonstrated household benefit from synthetic tests.

## Owner and boundaries

Derive from the existing selection inventory, role summary, ContextStore report
and review_brief output inside the existing context projection. No new database,
learner, event collection, HA lookup, feedback owner, automation scan or consent.
A short candidate is navigation into the existing workbench, not an executable
plan. Preference, activation counts, confidence, risk and permission stay separate.
Missing/paused/disconnected/changed-source data cannot become a current conclusion.
Rejected/deferred candidates remain in the existing evidence owner and are counted
separately, not promoted automatically. Counterexamples are descriptive; already-on
light does not prove a causal sequence, and no later activation is not proof of
absence. Never infer a new light action from an activity pattern alone.

## Coherent implementation stages

1. Backend projection and contract tests: bounded observation fields, same-zone /
   same-revision / current-source candidate basis, one stable candidate, reasons,
   evidence limits, preference exclusions and no mutation. Reuse zone_guide's
   existing context response rather than add another transport or store.
2. Integrate the compact brief into the actual zone UI, replacing duplication where
   appropriate; preserve selection/editor text, focus and zone-switch guards.
   Safe text rendering, mobile/desktop/keyboard and empty/error states.
3. Synthetic API/full-shell browser regressions. Demonstrate a helpful or reasonably
   withheld proposal in an authenticated session within already consented scope.
   No scope expansion when access or evidence is missing.
4. Versioned release only after complete candidate/source/CI and fresh prepublication
   scoped-backup gates in RELEASE_RUNBOOK.md. Alpha.23 stays the installed baseline
   until a subsequent release is explicitly verified; no second install in this start.

## Current stage

Package opened; implementation and tests have not yet been claimed. This is a work
coordination note, not an atomic global agent lock. Re-read PR/head before writing;
no competing implementation or force update. Next: implement stage 1 and record
actual checks, then continue the same PR for UI integration.
