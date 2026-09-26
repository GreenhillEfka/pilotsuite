# PilotSuite AI context

Canonical GreenhillEfka/pilotsuite / app 0d79c5e8_pilotsuite / architecture v21.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first.

## Resume: Alpha.37 presence-lifecycle review delivered

The delivered package extends the existing explicit inventory analysis with
two conservative, transient questions: boundary close can clear a plausible derived
presence status, and an activity edge can be the only recognized timeout refresh.
Device classes and literal branches are required; stale, disabled, dynamic, ambiguous
or indirect structures cannot become findings. No authored trigger IDs, raw config,
new store, automatic scan, repair, learning or control. Contract:
docs/PRESENCE_LIFECYCLE_REVIEW.md / ADR-033. PR 82 release
93e6df76d23a3171edcecfa9130330f192aa5d5f; candidate CI 36277330306 and main
CI 36277424359 passed all four jobs. Local validation: 484 Python and 56 JavaScript
tests; the synthetic browser scenario and amd64 container passed in exact CI.

Fresh backup 0baa717d contains only Alpha.36 app/data/options. One native Store
refresh and one update delivered Alpha.37; installed/offered/started, options and
auto_update unchanged. Startup/readiness logs confirm presence_adoption_review,
connected stream, fresh snapshot and resolved zone. General Apply remains closed.

Authenticated Ingress acceptance remains open: the cloud browser endpoint returned
502 connection closed before the PilotSuite UI loaded, including one reload. Do not
retry alternate proxies, weaken access or infer UI acceptance from MCP/runtime health.

## Previous delivery: Alpha.36 inventory snapshot integrity

PR 80, release b8ebc1ba2a32450ceb35e71269399d2f62cabe54.
Candidate CI 36272344492 and main CI 36272461571 passed all four jobs.
475 Python / 56 JavaScript tests; seven new synthetic regressions and nine CI browser
suites. Conservative batch freshness, catalog metadata/availability conflict checks
and repair-preview persistence guards are implemented. Normal available value changes
remain allowed. No additional learner/store, automatic scan or repair execution.

Fresh backup 67fa033b contains only Alpha.35 app/data/options and was verified before
publication. One Store refresh/update delivered Alpha.36; installed/offered/started.
Options and auto_update unchanged. Ready, connected, fresh and zone-resolved logs
retain presence_adoption_review; do not mislabel it hard_read_only. General Apply
remains READ_ONLY_RELEASE=True. Full source/app-tree/backup receipt: RELEASE_STATE.json.

Real Alpha.36 Ingress is untested: browser runtime returned environment_offline.
Do not infer browser acceptance or app-principal rights from MCP or HTTP 200.
Do not retry the earlier denied app proxy, weaken Ingress or repeat installation.

## User scope and stable identities

The current case label is Erdkellerbereich; three further areas/zones already exist.
Do not recreate zones, derive IDs from names, rewrite HA areas or edit bootstrap
options. Read saved canonical identities when authenticated Ingress permits.
User permits development reads across HA entities/automations beyond productive
learning permissions. Keep household configurations/findings private, outside fixtures.
Read access does not grant app-principal rights, learning consent or execution.

Prior cumulative inventory, trigger integrity, context/plan isolation and explicitly
confirmed metadata cleanup/undo remain intact. Technical-ID migration and automation
repair execution remain unavailable. No household repair or cleanup was performed.

Next: run authenticated read-only Alpha.37 lifecycle acceptance in saved Erdkellerbereich, then one unlike existing zone; no HA automation or learning change.
