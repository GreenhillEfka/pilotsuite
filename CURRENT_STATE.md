# Current state — Alpha.72 candidate; Alpha.71 installed

## Active assignment through 30.09.2026 08:00 Europe/Berlin

Continue only this repository and the existing package. Preserve untracked AGENTS.md.
The user authorized Habitus zone setup from HA areas/manual tags, then presence,
helpers/autolabeling, then lighting. Climate, media and further learning come later.
The existing heartbeat is active; no new agents/tasks/checkouts. No new feature
package after 07:20 local, no new publication after 07:30, stop at 08:00 and pause
that heartbeat. See docs/HABITUS_SETUP_PLAN.md and the current release runbook.

Local branch: feat/habitus-zone-setup, based on e3e5dc2. Draft PR #153 is the only
active PR. Git CLI has no write credentials; use the connected GitHub git-object
API and a non-force ref update. Its candidate tree is fetched and compared exactly
to local HEAD. Preserve the original local commits; their SHAs differ from connector
commits although trees match. Check fresh PR head/CI rather than reusing an old SHA.

## Implemented and tested locally

- One zone editor combines physical areas, additional entities, existing device/
  entity labels or a planned new zone label. Stable identities, Habitus roles,
  membership and relevance save together in the existing SQLite transaction.
- HA label changes reuse ontology/PlanStore. New label and member metadata share
  one concrete reviewed plan. Actual returned IDs bind only after durable receipt
  and independent readback. No replay after unknown creation without identity proof.
  Metadata restore preserves the label itself and unrelated names/labels/locations.
- Own presence helper packages include readable names/autolabeling and atomically
  join the zone structure. Fresh device/registry, disabled anchors, shared roles,
  manual edits and cumulative partial receipts are checked. No HA-wide atomic
  compare-and-swap guarantee is claimed.
- Visible setup steps lead to the existing editors. Verified stable members can
  prefill empty existing bindings, never overwrite drafts. Explicit save replaces
  generic extra confirmation. Own publication effects/target are shown inline.
- Configurable live light comparison consumes the primary zone presence and the
  existing lighting policy in the same tick/operational store. Outdoor-lux origin,
  supported capabilities, brightness bounds and manual-change holds are explicit.
  Restart retains cooldown but reacquires stability. Identity conflicts remain
  suspended until explicit review. Pure color/effect changes also trigger holds.
- Group/member overlap, missing members and cycles are rejected. Known group members
  are observed for availability/manual holds without becoming independent presence
  inputs or output targets. Member identity/topology changes suspend only lighting.
- Legacy partial savepoints cannot silently erase newer zone/presence/light module
  settings or owned bindings. Preview and transactional restore reject unsupported
  scope. Native app backup is still the complete recovery path; no ownership replay.

Validation: 711 Python tests, 78 JS tests and 68 API contracts pass. All eleven
browser suites passed; the maintenance suite passed again after the restore guard.
Seven actual HA 2026.9.3 protocol scenarios pass in a disposable local instance.
Final Python resource audit: 711 tests, subsequent garbage collection, zero ResourceWarnings.
Red/green cases cover label/anchor races, helper metadata drift, disabled anchors,
restart cooldown, sticky identity conflicts, six color/effect forms and omitted
savepoint module scope. Actual mobile/desktop light/dark screenshots inspected;
selected synthetic images are in docs/screenshots/habitus-setup-alpha72/.
Skills home-assistant-struktur and pilotsuite-quality-release are maintained locally.
Candidate c8f37e4 passed all five CI jobs in run 36660672269, including the corrected
Habitus label filter. Current continuation adds the group safeguards above. Eight
group cases initially failed; full Python/JS and extended zone browser are green.
Screenshots and source diff are reviewed before updating the same PR. New exact-head
CI is required after this correction; previous receipts remain in PR #153.

## Release boundary and actual backup finding

Alpha.72 version markers and both changelogs are prepared. No merge to main, Store
refresh, update, household helper/label apply, binding or control change occurred.
The installed/offered app is Alpha.71, started, auto_update=true. Its four option
values compare unchanged after backup; fresh logs show ready, connected, fresh and
zone-resolved. Log timestamps are copied as emitted, not independently attested.

Fresh partial backup 63f11346 was created 30 Sep 02:05:15 UTC. Native list/details
confirm only PilotSuite Alpha.71, 54,528,000 bytes on hassio.local, unprotected,
no HA/database/folders, and no failed addons/agents/folders. However backup/details
also reports listing failures for two unrelated Synology agents. The runbook's
explicit empty-agent_errors gate is not met. No implicit waiver, repeated backup,
NAS reconfiguration or publication. Do not alter backup settings to hide the errors.
Native app recovery is available in principle; no extraction or restore drill done.

Next: finish group correction review and new exact latest PR CI; obtain clean
native backup confirmation or the pending explicit user decision on the narrow
local-backup exception. The question was asked; no answer has arrived yet.
Only then may release/main CI, Store/source matching and targeted installation
proceed within the authorized time window. Update the release receipt only after
actual verified delivery. Prior Alpha.71 receipt remains in RELEASE_STATE.json.

## Boundaries and remaining work

Active light actuation and automation takeover are not implemented by the new
comparison module. No second presence engine, new actor executor, learning grant,
auth/Ingress weakening or household test switching. Existing HA automations remain
responsible. Relevant means analysis, not control.

No authenticated household Ingress session is available. Four-zone preservation
and changed flows are synthetically tested, not household-accepted. Actual zone
assignments must be read and verified before live import/apply. Erdkellerbereich's
existing chain and an unlike zone are the concrete next acceptance cases; previously
observed off/idle states and transition-free history do not prove physical vacancy,
correct timer expiry or a safe control handover.

Historical release and performance evidence: RELEASE_STATE.json, IMPLEMENTATION_STATUS.md
and ROADMAP.md. Alpha.71 was delivered through PR #151; main e3e5dc2 includes the
subsequent receipt PR #152. Do not repeat that installation or revive older paused runs.
