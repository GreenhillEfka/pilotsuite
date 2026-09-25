# PilotSuite current state

## 2026-09-25 — Alpha.27 installed and runtime-verified

Canonical GreenhillEfka/pilotsuite; app0d79c5e8_pilotsuite. Existing PR61 release
commit f7b3267a3f2785433c1ca5048a180a8a24f45d3b; root tree
c0fc13a5d13502ba2ec60db4288174b75fb13153; app tree
13645b666be8279ac7252b1dbbfe4f3f5346872c. Exact candidate
249d1ea354a9987ded774a919132574bfa814196 CI36184691444 and main CI36193063595 passed
all four jobs: Python/JavaScript tests, seven browser steps, reproducible source and
amd64 build. Full checksum-verified checkout manually reviewed; local rerun passed
386 Python and 48 JavaScript tests. No candidate code change was needed this turn.

Before publication, native snapshot/list and backup/details verified backup74c7be8d:
2026-09-25T21:42:31.584660+00:00, only PilotSuite Alpha.26, 54,220,800 bytes, no
HA/database/folders or reported failures, unprotected local agent. This verifies
completed backup metadata/scope, not archive extraction, off-device resilience or a
live restore drill. Publication followed at2026-09-25T21:43:14Z.

Exactly one native Store refresh and one PilotSuite update completed. Fresh metadata
confirms installed/offered Alpha.27, started, no pending update, auto_update=true and
all four options unchanged. No separate restart/rebuild, other-app update, household
configuration/role/consent change or actuator call. Startup and repeated readiness
logs confirm hard_read_only, ready, connected stream, fresh snapshot and resolved
zone. Temperature/illuminance are available; humidity/motion/presence/light remain
partial as before, not a transport regression.

## Newly delivered maintenance slice

Integrated versions/maintenance page, three bundled release notes, exact-identity
cached HA update state and native installation handoff; not installation history,
self-update or arbitrary downgrade. PlanStore owns private checksummed local
zone-configuration savepoints, explicit preview/hash-bound paused restore,
before-point, stale guard, durable idempotency and SQLite rollback. Restored zones'
learning consents are cleared; newer additional zones and existing evidence/review
text survive. Detected database bootstrap failure serves guarded rescue UI without
overwriting the original file or starting HA processing.

Explicit existing-helper storage inspection maps immutable registry/collection IDs,
including renamed helpers, and exposes safe fields and timer restore warnings.
Groups/templates are not falsely marked configuration-verified. No helper is created,
adopted or assigned ownership. Historical Golden Zone option is relabelled
first-start-only without changing options or real zones. Details:
docs/MAINTENANCE_AND_RECOVERY.md.

## Acceptance boundaries and remaining work

Candidate remote maintenance screenshots at390/1440 were checksum-verified and
visually reviewed; no maintenance-page overflow observed. CI exercises the actual
app with synthetic data, including stale/confirmed restore and corrupt-DB rescue.
Local full-shell browser navigation remains blocked by administrator policy and was
not bypassed. One supported native GET /api/v1/maintenance after installation
returned403, Ingress access required. That route was stopped, not retried or weakened.
Authenticated household Ingress and helper-collection reads by the app's own principal
remain unverified. No household savepoint restore was invoked. Store source/version/
app-tree association is not independent image or database attestation.

No running presence timer, helper executor, autonomous light/music/climate controller,
persisted adoption journal or actual HA automation takeover. Existing planning,
role/zone/evidence views and transient automation-read facilities remain the baseline.
The prior foundation-card narrow German wrapping follow-up remains separate.

Next, Issue56: ONE real bounded helper executor through existing PlanStore, including
full UI/application integration and disposable-HA timeout/lost-response/restart/
conflict tests before household writes. Keep existing HA automations responsible
until separately backed-up, reviewed and verified takeover. No disconnected
contract-only modules and no repeated Alpha.27 deployment.

RELEASE_STATE.json is the completed Alpha.27 receipt. The corrected Alpha.26 receipt
is retained at f7b3267a3f2785433c1ca5048a180a8a24f45d3b:docs/RELEASE_STATE.json.
This handoff changes no application files or version. Final documentation PR/main CI
status belongs in its discussion, not another status-only release loop.
