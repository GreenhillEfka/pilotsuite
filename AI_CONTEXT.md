# PilotSuite AI context

Canonical GreenhillEfka/pilotsuite / app 0d79c5e8_pilotsuite / architecture v21.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first.

## Resume: API contract integrity after delivered Alpha.35

The repository now inventories all 48 registered `/api/v1` method/path contracts in
docs/API.md. A regression compares the human inventory directly with the `aiohttp`
router, including uniqueness, so future route additions/removals cannot leave it
silently partial. The update corrects the legacy `{id}`/`{plan_id}` mismatch and
separates inspection, preview, persistence, restore and apply semantics. No endpoint,
application code, version, option or installed state changed; see
docs/WORK_PACKAGE_API_INTEGRITY.md.

## Installed: Alpha.35 cumulative inventory overview delivered

The explicit global scan still reads no more than eight automation configurations per
click, but its browser-only view now accumulates same-zone/same-revision packages.
Progress and deterministic filters separate reference findings, trigger-ID findings,
unreadable configurations and all readable results. Replacement selections persist
across another package/filter; reload, zone/revision change and invalidation discard
the transient view. No new store, background scan, repair execution, HA write, learning
or authority.

PR 76 release faf36118402e817d42c4ba1919995c40c53e0cf4 is installed/offered/
started. Candidate CI 36267009996 and main CI 36267117823 passed all four jobs.
Fresh scoped backup c194bc96 contains only Alpha.34 app/data/options. One Store refresh
and one update; no explicit restart. Options/auto_update unchanged; startup reports
ready, connected stream, fresh snapshot and resolved zone in unchanged
presence_adoption_review mode. RELEASE_STATE is the canonical receipt.

The native Supervisor app proxy returns the expected `403 Ingress access required`;
do not weaken or bypass that guard. Authenticated Alpha.35 Ingress is not tested;
current browser has only about:blank.
Next: explicit read-only cumulative scan in saved Erdkellerbereich, then the other
three zones. Do not infer identities, repair automations or change household state.

## Previous delivery: Alpha.34, 2026-09-26

PR 74 release 20adb0e6ddf61ab899366b8a24f66f67468df569 installed/offered/started.
Exact candidate CI 36263679166 and release-main CI 36263809521 passed all four jobs
and nine browser suites; 468 Python / 56 JS. Fresh PilotSuite-only backup 09436e7c
verified before publication. One native Store refresh/update, no extra restart.
Options and auto_update unchanged; ready, connected, snapshot fresh, zone resolved.
Runtime mode remains presence_adoption_review; do not call it hard_read_only.
General Apply remains READ_ONLY_RELEASE=True; no household execution tested.

Inventory and routine detail reviews share core/trigger_integrity.py. Static ID
matches, missing/partial/disabled/inactive/unknown references are distinct. Paths
and counts only, no raw authored IDs; implicit indices/shared IDs supported.
Unreferenced-by-ID is not unused. No control-flow simulation or safety guarantee.
Explicit reviews preserve unsaved choices and do not write plans/configuration.
No new owner/store, learning, migration, control or automatic repair.

## User scope and stable identities

The current case label is Erdkellerbereich; three further areas/zones already exist.
Do not recreate zones, derive IDs from names, rewrite HA areas or edit bootstrap
options. Read the saved canonical zone identities when authenticated Ingress permits.
User explicitly allows development reads across all HA entities/automations beyond
PilotSuite productive learning permissions. Household configs/findings remain private,
not repository fixtures. This is not app-principal access proof or new learning consent.

Alpha.33 recovery/isolation behavior and Alpha.32 ContextStore/PlanStore inventory,
confirmed metadata cleanup/undo remain intact. Technical-ID migration and automation
repair execution remain unavailable. No household repair or cleanup was performed.

Next: read-only acceptance of integrity findings against the four existing saved
zones, starting with Erdkellerbereich. Canonical zone access, true Ingress UX,
app-principal config rights and independent data/image checks remain separate.
Do not repeat installation or bypass Ingress. Final doc CI evidence belongs in its PR.
