# PilotSuite AI context

Canonical GreenhillEfka/pilotsuite / app 0d79c5e8_pilotsuite / architecture v23.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first.

## Resume: Alpha.43 numeric integrity installed

The current branch closes one observation-integrity defect found by a fresh review:
a directly supplied good-quality NaN/infinite numeric observation could survive the
zone summary, claim availability and make the response non-standard JSON. The shared
summary boundary now rejects non-finite and physically impossible temperature,
humidity and illuminance values, preserves them as invalid/unknown, and sanitizes
individual/reference projections. The current lighting brief independently requires
finite non-negative lux for both source usability and displayed aggregation.

Local repository/API validation, 525 Python and 59 JavaScript tests pass. PR 94
release `92f5e8e36823e885d5456c9a9a3b12b51968f32b`; candidate CI 36295107488
and release-main CI 36295203741 passed all four jobs. Fresh backup `ed0fb9a7`
contains only Alpha.42 app/data/options, with no HA, database, folders or failed
parts. One Store refresh and one normal update installed Alpha.43; it is offered,
started, ready, stream-connected, snapshot-fresh and zone-resolved with options and
auto_update unchanged. General Apply remains closed and no household state changed.

Authenticated Ingress remains open: the available cloud browser returned 502 Bad
Gateway / connection closed before HA loaded, including the single allowed reload.
Next: run the explicit current-light check in authenticated read-only Ingress for the
saved Erdkellerbereich and verify source and automation explanations.

## Installed baseline: Alpha.42 current lighting decision

The current branch adds a transient, explicit lighting decision brief to the existing
lighting workspace. It reads canonical roles/current observations and freshly reads
related HA automation structures, while separating configured/usable sources,
transport freshness, physical measurement freshness and outdoor-light provenance.
Indoor lux never becomes outdoor proof. Related automation structure is not a
duplicate or safety verdict. Exactly one allowlisted internal next step is returned.

The endpoint is POST-only, zone/revision bound and rechecks roles after HA reads.
Reload and GET do not trigger review; stale/malformed/concurrent responses are
rejected. Nothing is stored or executed. Source-rich zones use bounded lookup
batches, invalid lux is not usable and background refresh cannot discard an active
check.

PR 92 release `be537ceaffffeb0bf88b5ac3ad04e3402aa47f58`; candidate CI
36292600442 and release-main CI 36292681509 passed all four jobs. Fresh backup
`a90ec2d3` contains only Alpha.41 app/data/options. One Store refresh and one normal
update installed Alpha.42 with options and auto_update unchanged. Logs confirm v23,
ready, connected stream, fresh snapshot and resolved saved zone.

Next: run the explicit Alpha.42 current-light check in authenticated read-only
Ingress for Erdkellerbereich and verify source/automation explanations; runtime and
synthetic Chromium health are not household UI acceptance.

## Previous delivery: Alpha.41 lighting-source integrity installed

Alpha.41 continues the same lighting policy owner. It separates configured/currently
usable light targets, indoor lux and binary brightness in the synthetic preview,
never certifies those signals as outdoor daylight provenance, holds when current
brightness is unavailable and rejects incoherent/future checkpoints. Backup
`bc501582` is the verified Alpha.40 app/data/options rollback point. PR 90 release
`e0bfc778f930accf7b4b4899e38eff8558fade24`; candidate CI 36289439619 and
release-main CI 36289511093 passed all four jobs. Alpha.41 is installed, offered and
started with options and auto_update unchanged. Authenticated Ingress acceptance
remains independent.

The current branch extends the existing pure lighting policy instead of adding a
controller or second owner. A deterministic preview separates presence state,
daylight lux, brightness percentage, chosen atmosphere, manual override, target
capabilities and execution authority. It requires a stable daylight band, applies a
deadband and minimum proposal interval, and bounds each brightness step. Missing lux
is unknown, not darkness; unknown presence and manual operation hold the proposal.

Seven allowlisted synthetic scenarios run only after explicit POST/click. They read no
household measurement or history, persist nothing and return execution.allowed=false.
Responses are bound to the current zone/revision/generation; only fixed `on`,
`brightness_pct` and `color_temp_kelvin` setting keys can be displayed. No service
name, URL or target is accepted from data. Reload performs no preview or mutation.

Local validation passes repository/API contracts, 515 Python and 59 JavaScript tests.
Exact Alpha.41 source, candidate and release-main CI passed Chromium, amd64, test and
reproducible-source jobs. Fresh backup bc501582 contains only Alpha.40 app/data/options.
One Store refresh and one update installed Alpha.41 with options and auto_update
unchanged. Logs confirm v23, ready, connected stream, fresh snapshot and resolved
saved zone.

Read-only HA inspection confirmed area `erdkeller` / `Erdkeller Innen`, the user's
semantic Erdkellerbereich label, two indoor lux sources and existing automation
context. These indoor signals are not outdoor daylight proof. No HA state or
configuration changed.

Next: run the explicit Alpha.41 lighting preview in authenticated read-only Ingress
for Erdkellerbereich and verify that source distinction, then one unlike existing
zone, without changing household configuration, consent or devices. CI/runtime health
are not Ingress acceptance.

## Previous delivery: Alpha.39 presence kernel

The current branch implements the next accepted presence-first reliability package.
A pure kernel separates continuous presence, activity pulses, grace, vacancy and
unknown. It persists only a bounded checkpoint in the existing ContextStore; source
changes/reset clear it and savepoints exclude it. Reconnect keeps the original
deadline instead of silently renewing it. Unknown sources/dependencies and manual
cancel never become vacancy. A non-activation learning event no longer returns before
the dormant runtime reconciliation step.

The existing presence workspace adds five allowlisted synthetic scenario replays.
They require an explicit POST/click, use no household observation/history, persist
nothing and return execution.allowed=false. Zone/revision/generation checks discard
late answers. Public runtime enable and general Apply remain closed; no HA config,
automation, actor, role, consent or productive-learning change is part of this slice.

Local validation: repository/API contracts, 506 Python and 59 JavaScript tests pass.
PR 86 release 892cbab950c5442a944d6edf0d23b2b4cc8e0d6f; tree
489010812b7f31fd0d86e62d018c6dd8a9d289e4 and app tree
331ad1efafc495f17cc55240e45539ead7ffd772. Candidate CI 36283655159 and
release-main CI 36283761672 passed all four jobs, including Chromium, amd64 and
reproducible source.

Fresh backup 618bc607 contains only Alpha.38 app/data/options, with no HA, database,
folders or failed parts. One native Store refresh exposed Alpha.39 and one update
installed it; no explicit restart, rebuild or other app update. It is
installed/offered/started with options and auto_update unchanged. Logs report
presence_adoption_review, ready, connected stream, fresh snapshot and resolved zone.
Public presence activation and general Apply remain closed.

Authenticated real Ingress acceptance remains open: after installation the available
cloud browser still returned 502 Bad Gateway / connection closed after the single
allowed reload. Do not retry alternate proxies, weaken access or infer UI acceptance
from runtime health.

## Previous delivery: Alpha.38 presence evidence and source clarity

Alpha.38 makes the existing event-to-learning handoff conservative: only frames
accepted by WorldModel can become new evidence. Older/equal/duplicate, malformed or
misaddressed frames and stale removals cannot leak into the learner. A valid delayed
activity edge remains usable, but light/lux context is unknown unless every source
timestamp exists and is no later than that activation. This is event-time consistency,
not history reconstruction, simultaneity or causality.

Workspace modules now use the same effective roles as the server. Derived single-source
defaults are visibly derived and an unrelated save no longer persists them as manually
confirmed; only an explicit group edit does. Optional independent comparison temperature
is separate from the zone median and shows a difference only for complete, same-unit,
independent values. Presence-first light/mood/media and bounded adaptation are documented
as future stages, not installed control. Contract: docs/PRESENCE_FIRST_INTELLIGENCE.md.

PR 84 release fcdebaebc1844b592914ecc2f2460ca5779e70fb; candidate tree
67073b190cd9083ac6f3b43ad96427a6cd89367d and app tree
1af77d9c800f1ec2ea98c63bf0edb75ec68c4e66. Candidate CI 36280638136 and
release-main CI 36280792938 passed all four jobs. Local validation: 494 Python and
59 JavaScript tests; all synthetic Chromium suites and amd64 container passed in CI.

Fresh backup d4f477c9 contains only Alpha.37 app/data/options. Alpha.38 was already
offered, so no Store refresh was made; one normal update installed it. It is
installed/offered/started with options and auto_update unchanged. Startup/readiness
logs report presence_adoption_review, connected stream, fresh snapshot and resolved
zone. General Apply remains closed.

Authenticated real Ingress acceptance remains open: the available cloud browser ended
at 502 Bad Gateway / connection closed before HA loaded, including the single allowed
reload. Do not retry alternate proxies, weaken access or infer UI acceptance from
MCP/runtime health.

## Previous delivery: Alpha.37 presence-lifecycle review

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

Historical Alpha.38 acceptance remained open for the saved Erdkellerbereich and one
unlike existing zone; no HA automation, learning or device change was authorized.
