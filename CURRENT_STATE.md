# Current state — Alpha.66 installed; household acceptance pending

## Verified delivery

PR #142 merged as `d0cbb2131d05e5d39520d18ce89b466ff32cb2c2`.
Exact candidate CI `36461713597` and release-main CI `36461940133` passed all
five jobs: tests, 11 browser suites, amd64 container, reproducible checkout and
disposable Home Assistant protocol. App tree:
`7a60131d68254efa9f8bbcec97ae60f67752a3a9`; local and connector trees matched.

Fresh PilotSuite-only backup `0eee33cb` completed at 17:51:58 UTC before publication:
exactly Alpha.65 app/data/options, 54,476,800 bytes, no HA/database/folders/failures,
local and unprotected. Native list and backup/details verified metadata; no extraction
or restore drill. One Store refresh and one targeted update installed Alpha.66.
No extra restart/rebuild or other-app update. All four options remain unchanged.
Startup remains `presence_adoption_review`, ready, connected, snapshot-fresh and
zone-resolved. Raw log timestamps are recorded as emitted, not clock-attested.
Full evidence: [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).

## What Alpha.66 changes

The existing explicit presence-automation review now presents reuse strategies for
controllers, consumers and mixed logic, direct affected references and six open
behavior/recovery checks. Empty or unresolved structure never establishes takeover
readiness; unresolved inspected configs participate in the review fingerprint.
Three regression methods first reproduced four incorrect verdict/fingerprint cases.
New projection/integration coverage and extended Chromium flow pass: 632 Python /
75 JS / 62 contracts; discovery/compilation and zero-ResourceWarning audit pass.
Zone/workspace browser suites passed locally; screenshot inspected. All 11 browser
suites passed exact candidate/main CI. Synthetic is not household acceptance.

No executable automation edit, takeover, new persistence, engine or route. Existing
import/diff/transform modules and PlanStore remain the future implementation basis.
No household binding/helper/metadata/automation/output/consent changed. AGENTS.md
remains unchanged and untracked; Ingress/authentication intact.

## Active two-hour run and next task

User mandate: administration, configuration and lighting, 2026-09-28
17:05:52–19:05:52 UTC. No new packages/publications after 18:45:52 UTC.
Reused heartbeat active for this window only; pause at completion, never extend it.
Finish the Alpha.66 documentation receipt before starting another package.

Latest user correction permits adoption/reuse. The unanswered question concerns
the scope of live edits, not permission to develop the feature. Until answered,
no household automation edit/enable/disable or active control transfer.

Next bounded investigation: inconsistent usable-source counts and guidance in the
existing lighting/configuration path. Preview accepts raw nonempty state whereas
the decision brief validates lux. Reproduce invalid lux/binary states and missing/
derived versus explicit-empty roles first; reuse canonical owners, preserve roles,
drafts and consent. No household switching. An executable automation change path
requires its own concrete before/after plan, approved scope and recovery tests.

Authenticated household Ingress and actual four-zone acceptance remain open.
Review Erdkellerbereich and one unlike zone read-only when an authorized session
exists; do not guess household bindings or replace an existing public sensor.

## History

Earlier three-hour and one-hour windows remain closed. Alpha.65 receipt:
`cdd238e9e2cc720544b3d7227b7607e0c642b68a:docs/RELEASE_STATE.json`.
Alpha.64 measurements/tradeoff remain in ROADMAP.md and its historical receipt.
