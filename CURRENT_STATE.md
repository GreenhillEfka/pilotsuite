# Current state — Alpha.65 installed; household acceptance pending

## Verified delivery

PR #140 merged as `91553c840a826b552181bfe8f9132022b79d9823`.
Exact candidate CI `36457661481` and release-main CI `36458315513` passed
all five jobs: tests, 11 browser suites, amd64 container, reproducible checkout
and disposable Home Assistant protocol. App tree:
`e8f470a74bdfb87d63a4b401b4647785e62fb383`; local and connector trees matched.

Fresh PilotSuite-only backup `44da1956` completed at 17:19:26 UTC before publication:
exactly Alpha.64 app/data/options, 54,487,040 bytes, no HA/database/folders/failures,
local and unprotected. Native list and backup/details verified metadata; no extraction
or restore drill. One Store refresh and one targeted update installed Alpha.65.
No extra restart/rebuild or other-app update. All four options remain unchanged.

Startup remains `presence_adoption_review`, ready, connected, snapshot-fresh and
zone-resolved. Raw log timestamps are recorded as emitted, not independently
clock-attested. Full evidence: [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).

## What Alpha.65 changes

Only the existing pure lighting preview: missing daylight/current brightness,
manual override and unknown/vacant presence interrupt the stable-band observation.
Recovery must establish a new stable band; the last proposal's cooldown remains.
The fixed recovery scenario in the existing UI explains the full new waiting
period. No live lighting controller, persistence or configuration migration.

Two new regression methods first failed in seven cases; all pass after the fix.
Third test and extended Chromium flow verify the timeline. 628 Python / 75 JS /
62 API contracts, discovery and compilation pass. Repeated exact-source audit:
zero ResourceWarnings. Local workspace and Organization suites pass, screenshot
inspected; all 11 suites pass exact candidate and main CI. Synthetic is not household.

No household binding, helper, metadata, automation, output activation or consent
changed. AGENTS.md remains unchanged and untracked; Ingress/authentication intact.

## Active two-hour run and next task

New explicit user mandate: administration, configuration and lighting, 2026-09-28
17:05:52–19:05:52 UTC. No new packages/publications after 18:45:52 UTC.
Reused heartbeat active for this window only; pause at completion, never extend it.
Finish the Alpha.65 documentation receipt before starting the next package.

Next code investigation: inconsistent usable-source counts and guidance in the
existing lighting/configuration path. Preview currently checks raw nonempty state,
whereas the decision brief validates lux; reproduce invalid lux/binary states and
missing/derived versus explicit-empty role handling before any fix. Keep one owner
and preserve existing roles/drafts/consents; no new engine or household switching.

Authenticated household Ingress and actual four-zone acceptance remain open.
Review Erdkellerbereich and one unlike zone read-only when an authorized session
exists. Existing automations remain controllers; Boolean/timer/public-sensor
bindings are not guessed. No existing-chain public sensor is automatically created.

## History

Earlier three-hour and one-hour windows remain closed. Alpha.64 receipt:
`6b7204e3a8620c05978c4a73a54bec2b078ba554:CURRENT_STATE.md`.
Its measured checkpoint optimization/tradeoff remains in ROADMAP.md and that receipt.
Alpha.63 unchanged-save/session/deadline behavior and all prior presence safeguards
remain intact; no scheduler, generic actuation or automation-takeover change.
