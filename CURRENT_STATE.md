# Current state — Alpha.68 installed; household acceptance pending

## Verified delivery

PR #146 merged as `3a3347c6b4c23a20e9a466aaf1211d8d05f1a3b0`.
Exact candidate `6438fafca1b092d3f568fd0dc36ac9fcff8bf91f` passed CI
`36478670271`; release-main CI `36482802805` passed all five jobs:
tests, all 11 browser suites, amd64 container, reproducible checkout and disposable
Home Assistant protocol. Candidate/main repository tree:
`8077768888873f6482e755ab7c0f270d5b76f52d`; app tree:
`16c2f6814b4ee6e8a809c920c25ba69ee4da43d1`.
Own diff review and versioned source preflight passed.

Fresh PilotSuite-only backup `ca4c7d47`, 20:56:16 UTC, was completed and natively
verified before version publication: exactly Alpha.67 app/data/options, 54,497,280
bytes, no HA/database/folders/failures. Local and unprotected; no extraction or
restore drill. One Store refresh and one targeted update installed Alpha.68;
no extra restart/rebuild or other-app update.

Installed/offered Alpha.68 is started. All four app option values are unchanged.
Startup remains `presence_adoption_review`; ready, stream connected, snapshot fresh
and zone resolved, including repeated post-start checks. General Apply remains
closed; existing bounded executors are not described as universal hard_read_only.
Log timestamps are copied as emitted, not clock-attested.
Full source/backup/runtime evidence: [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json).

## Implemented and tested

Four setup shortcuts reuse existing presence, source, entity and zone editors.
A hidden-role focus failure was reproduced first in the workspace browser; source
editing now focuses a visible field and presence editing focuses the grace time.
The main-source link stays in configuration. Dirty drafts and unavailable editors
retain explicit protection. No new engine, store, API or configuration owner.

637 Python / 75 JS / 62 API contracts, discovery and compilation passed again on
release-main. Repeated resource audit: zero ResourceWarnings. An initial restricted
local run could not start loopback test servers; the permitted rerun passed.
Workspace and zone-instance browser suites passed locally on the candidate app
tree; all 11 passed exact candidate/main CI. Synthetic 390/768/1440-pixel light/dark
checks cover focus, navigation, drafts and no HA writes. Screenshots are not real
Ingress acceptance.

No household binding/helper/metadata/automation/output/consent changed. No data or
schema migration. AGENTS.md remains unchanged and untracked; Ingress/authentication
intact. Four-zone preservation is tested synthetically, not independently read
back from the installed PilotSuite UI.

## Scope and remaining acceptance

The one-hour UI run ended with draft PR #146. The user's subsequent "Ok" accepted
the recommended completion of that existing package through the release runbook.
This is not a time-window extension or a new feature package. The heartbeat remains
paused; earlier runs and this release completion are closed.

No authenticated HA browser session is connected. Actual Ingress navigation and
four-zone household acceptance remain open. First inspect Erdkellerbereich and one
unlike zone read-only, preserving all four saved zones, entity cleanup and Habituszonen.

Supplementary HA-MCP reads found the existing-zone Boolean/public occupancy sensor
off and a three-minute timer idle. The 18:00–21:00 UTC history window returned only
held initial states for six selected inputs/outputs, no transitions or pagination.
This neither proves physical vacancy nor validates wiring, timer expiry, quiet
occupancy or unknown handling. Habituszonen was read, not edited. No raw household
configuration or identifiers are copied into the release receipt.

User permits reuse/adoption of existing automations, but concrete live-edit scope
is still unanswered. No automation edit/enable/disable or productive control transfer.
Next: authenticated read-only zone acceptance and evidence-backed reuse review.
Missing/derived versus explicit-empty lighting roles remain a separate bounded
investigation, not part of this release completion.

## History

Alpha.67 receipt: `1375aec60c78f90b9d0e2c15b4eda8e5a6132141:docs/RELEASE_STATE.json`.
The initial Alpha.68 safe-handoff record is retained in PR #146 and its Git history.
Alpha.64 measurements/tradeoff remain in ROADMAP.md and its historical receipt.
