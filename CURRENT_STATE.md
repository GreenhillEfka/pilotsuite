# Current state — Alpha.72 installed

## New product direction after delivery, 30.09.2026

The user explicitly requests development through **real structural zone adoption**:
HA and PilotSuite synchronized with matching manual zone/role labels. This supersedes
the temporary deferral of structural acceptance. Presence, helpers, light control
and later modules remain hidden/deferred. No authority to change household control.

The Alpha.73 candidate on `docs/habitus-foundation-reset` implements the reduced
zone overview/editor/documentation, preserved runtime/analysis choices, fresh
registry verification, plan receipts/restore and dated export using existing owners.
727 Python and 77 JS tests plus all five current browser suites passed locally;
all seven native HA 2026.9.3 protocol scenarios also passed, including fresh
structure verification. Exact CI remains recorded in the candidate PR.
The current UI contract replaces seven old full-product navigation suites; their
backend/model coverage and selected isolated component tests remain. Screenshots
from the actual local fixture reviewed at 390/820/1440 in light/dark.

Two external gates remain. The available HA browser still shows the login page;
the user has been asked to log in and open PilotSuite. Native direct app proxy
returns 403 Ingress required; that route is stopped, with no auth workaround.
Fresh backup `e57999fb` (30 Sep 09:29:25 UTC) confirms only Alpha.72 app/data,
54,558,720 bytes local, no failed components or HA/database/folders. Two Synology
agents again fail to list backups. Runbook's empty-agent-errors gate is not met;
the previous Alpha.72 exception is not silently extended. No merge/publication,
installation or real structural acceptance is claimed for Alpha.73.

## Delivery completed, 30.09.2026

PR #153 is merged. Exact release main: `04c47bb0b99ccf34872e938bd0029b6cdac6e325`.
Candidate `4306a924679f397d6e3c7ca9f511ade7ce1aed61` and release main passed all five
CI jobs (36687732779 / 36690038477). Repository/app trees matched the tested local
candidate. Receipt: docs/RELEASE_STATE.json; development ledger:
docs/IMPLEMENTATION_STATUS.md and docs/HABITUS_SETUP_PLAN.md.

The user requested “Bitte abschließen” after the stated backup exception blocker.
This was treated as approval for that disclosed narrow exception, announced before
release. Fresh native backup `e636bd76`, 30 Sep 08:28:34 UTC: only PilotSuite Alpha.71
and data/options, 54,538,240 bytes on hassio.local, unprotected, no HA/database/
folders and no failed components. Two additional Synology agents still failed to
list backups. Their errors are retained in the receipt, not claimed resolved.
No NAS/settings change, archive extraction or restore drill.

One Store refresh offered Alpha.72 from the canonical repository. One targeted
update completed; no separate restart/rebuild or other-app update. Native app
metadata confirms Alpha.72 started, all four options unchanged. Startup mode is
still presence_adoption_review; ready/stream/fresh/resolved confirmed. General
Apply remains closed in the exact source; existing bounded paths are preserved.
No independent installed-image attestation is claimed.

## Installed capability

- One zone editor combines physical HA areas, additional entities and existing
  device/entity labels or a planned new label. Membership, stable identities,
  roles and analysis relevance save together in the existing store.
- New labels and member metadata use one concrete existing plan with fresh conflict
  checks, durable receipts, independent readback and bounded rollback. Physical
  locations and foreign metadata remain protected.
- Own presence output packages include readable names/autolabeling and join the
  zone structure. Existing anchors, disabled identities and competing roles are
  checked. Failed readback does not authorize duplicate creation.
- Setup steps lead to existing editors; verified suggestions fill only empty
  bindings. Whole-zone/module pause and publication effects are explicit.
  Missing saved sources remain visible until deliberate correction; cancel
  preserves them. Empty/support-only source sets explain missing direct coverage.
- Light comparison uses the primary presence and existing policy/store. It has
  explicit outdoor-lux provenance, bounded proposals, group coverage checks,
  durable manual holds and restart cooldown. Named blockers and daylight validity
  are explained. Identity conflicts require review.
- Older partial savepoints cannot erase newer zone/presence/light settings or
  owned bindings. Native app backup remains the complete recovery path.

Validation: 719 Python tests, 78 JS tests, 68 API contracts, eleven browser suites,
seven native HA 2026.9.3 protocol scenarios and amd64 build. Relevant errors were
reproduced before fixes; actual mobile/desktop light/dark screenshots inspected.
Local final Python garbage collection had zero ResourceWarnings. Both project
skills are maintained and validated. Exact completion receipts are in PR #153.

## Deferred acceptance from the delivered package

No authenticated household Ingress session was available. Real saved bindings
and preservation of all four household zones remain to be observed there; runtime
readiness and synthetic UI tests do not prove that acceptance. Existing HA-chain
inspection found coupled status/timer/light logic and unevaluated template limits.
Private evidence is in ignored pilot_data/reviews, not public documentation.

When accepting the reduced structure, inspect Erdkellerbereich and one unlike zone
read-only in authenticated Ingress: areas/tags, members, roles and stable identities.
Independent sources, status/timer/automation bindings and genuinely missing helpers
belong to the later presence phase, before any household connection/apply.
No household helpers/labels/bindings, automations or learning grants were changed.
Active light actuation and automation takeover remain unimplemented. Climate,
media and pattern recognition follow a household-accepted foundation.

The overnight deadline ended. Its heartbeat is confirmed PAUSED; no new timed
loop or task. Preserve untracked AGENTS.md and the original local feature commits.
The completed documentation receipt is PR #154. The new direction is prepared on
docs/habitus-foundation-reset; the current code changes are local. No household
labels, helpers, control bindings or learning grants have been changed.
