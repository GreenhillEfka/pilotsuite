# Current state — Alpha.70 installed; household acceptance pending

## Overnight closing phase — ends 29 September 08:30 Europe/Berlin

Window: 28 September 22:26:57 UTC–29 September 06:30 UTC. Feature work completed;
no new feature package. No new publication after 06:00 UTC. At 06:30 UTC report
saved work and pause the existing heartbeat. Do not extend or create extra jobs/chats.
Only closing documentation, release evidence and acceptance handoff remain.

## Delivered and verified

PR #148 delivered Alpha.69: zone-owned Automationen, explicit presence/light/other
topics in the existing store, shared-use hints, deduplicated eight-rule inspections,
honest unavailable enablement and preserved drafts/focus. Legacy guide moved out
of basic setup. ADR-043 and UX_WORKSPACE.md document primary-source research.

PR #149 delivered Alpha.70: connected public HA sensor first, independent comparison
secondary, no unknown fallback to Boolean/calculation, strict calculated validity,
clear HA versus PilotSuite timing. Role-specific helper links reuse the existing
editor; own-package preview explains five components and recovery limits, and a
failed preview can be closed. No new executor, API, controller or persistence.

Exact candidate `ee5cb290f3d1d4a93e6778984f915ec37c25fe95` and release-main
`bf1846166738d90be71757f7d6d3c14075acc04f` passed all five CI jobs:
runs `36526970718` / `36527163624`, including all 11 browser suites.
Root tree `4194f957c66f3efcf9bfa51d68d766228d7650a4`;
app tree `ee72e06bc41fd45715dc54cefd5cc62f9bf4b4eb`.
Source preflight and own diff review passed. 640 Python / 78 JS / 62 contracts,
discovery and compilation pass; exact-main repeated resource audit: zero warnings.
New invalid-state and failed-preview regressions failed before their fixes.
Workspace, organization and zone browsers pass; synthetic 390/768/1440 light/dark
screenshots inspected. Synthetic tests do not establish household usability.

Fresh prepublication backup `b7c38f9d`, 29 Sep 05:20:31.450999 UTC, native list and
backup/details verified: only Alpha.69 PilotSuite app/data/options, 54,507,520 bytes,
no HA/database/folders/failures, local unprotected agent. No extraction/restore drill.

At 05:41 UTC: Alpha.70 installed/offered, started, all four options unchanged.
One Store refresh and one targeted update, no extra restart/rebuild/other-app update.
Startup remains presence_adoption_review; ready/stream/fresh snapshot/zone resolved.
Log times copied as emitted, not clock-attested. Receipt: docs/RELEASE_STATE.json;
PR #149 has exact delivery evidence. Do not repeat the Alpha.70 installation.

Closing documentation remains on the same feature branch for reviewed integration.
No follow-up PR is needed merely to record its own CI; final CI goes in its PR comment.

## Boundaries and actual gaps

All four saved zones, entity cleanup and untracked AGENTS.md remain preserved.
No schema/configuration migration. Ingress/auth/sandbox unchanged. General Apply
closed; existing bounded executors are not described as universal hard_read_only.

Concrete live household write scope remains unanswered. No household helper creation,
rename, automation edit/enable/disable, output activation, control transfer or new
learning consent. Reuse/adoption is an authorized direction, not permanently forbidden.

Still unimplemented: targeted single missing-helper creation in an existing chain,
active HA-parameter editing and automation-change execution. The full own-output
package is not a substitute for those paths. Do not reopen the legacy provisioner.

No authenticated HA browser session is connected. Actual Ingress/four-zone acceptance
is open. Previous read-only states and 18:00–21:00 UTC history showed no transition;
they do not prove vacancy, timer expiry, quiet occupancy, wiring or safe takeover.

## Next step

Read-only authenticated Ingress acceptance of Erdkellerbereich: verify the existing
Boolean/timer/public sensor/responsible automation bindings and actual HA timing,
then contrast an unlike saved zone. Preserve all four zones; no test switching.
List missing helper/parameter gaps before authorizing any concrete household edit.

## History

Alpha.69 receipt is retained at
`bf1846166738d90be71757f7d6d3c14075acc04f:docs/RELEASE_STATE.json`.
Alpha.68 receipt: `0b6c5fe798591f9a5ee6a437e85571d72386084b:docs/RELEASE_STATE.json`.
Previous timed runs remain closed. Alpha.64 measurements remain in ROADMAP.md.
