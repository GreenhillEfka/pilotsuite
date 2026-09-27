# PilotSuite AI context

Canonical GreenhillEfka/pilotsuite / app 0d79c5e8_pilotsuite / architecture v23.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first.

## Alpha.48 live shadow candidate

The user approved presence live comparison and light need on confirmed real sources,
while independently cleaning their HA entities. This package implements that functional
step, not another isolated integrity-only release. Preserve PR102's reviewed historical
provenance fix (cc9039377824b4702a1c2e2b39fee090f1bdf97e) and tests; they are integrated,
not overwritten. Original installed baseline was Alpha46 at 51a86351492b591f64c57a703d06fcb1137edaf7.
Re-read live main and app metadata before publishing: other development may progress.

The existing presence and lighting kernels now have an explicit per-zone start/stop
shadow service and UI. It uses accepted real observations, a local 5-second deadline
check and only latest checkpoints in ContextStore. No new history, learner, schema,
HA writes or ordinary Apply capability. The HA room status is comparison-only; it
never feeds itself into PilotSuite's presence evidence. Independent raw sensors only;
unresolved/group/template dependencies do not become counted independent evidence.

Settings and session identity share the existing zone revision. Changed membership,
identity or configuration suspends the durable session until explicit confirmation.
Deadlines survive reconnect/restart without renewal. Source report age is bounded;
held helper/actuator states are not incorrectly treated as freshly measured sensors.
Unknown sources do not become vacancy. Missing/manual/unsupported light inputs hold.
Outdoor lux is explicitly confirmed, never inferred from indoor measurements. Atmosphere
is a chosen profile, not emotional inference. All settings are proposals, not HA calls.

GET never starts a session. Start/stop changes only shadow settings and latest state,
not roles, evidence or learning consent. Configuration savepoints exclude the session.
An optional shadow-storage error cannot break the shared event stream or other zones.
See docs/PRESENCE_SHADOW.md and the actual-app tests/fixture for the full contract.

## Acceptance and release

Local browser navigation was blocked by administrator policy; do not bypass it.
The new tenth CI browser suite must pass in addition to all existing suites. Synthetic
UI evidence is not authenticated household acceptance. No household shadow session
is started as a release test. Do not change names, roles, user cleanup or consent.

Before publication: exact candidate CI, fresh verified PilotSuite-only native backup
(auto_update remains true), expected-SHA merge, exact main CI, native Store refresh
only if needed and one update. No other app or separate restart/rebuild. Complete the
four-file receipt only after actual delivery; final doc CI belongs in PR comments.
The existing RELEASE_STATE remains the last completed delivery, not this candidate.

## Stable user scope

Erdkellerbereich is a semantic label; existing saved IDs and the three further zones
must be read, never guessed/recreated. Development reads may cover all HA entities
and automations, not implicit productive learning or execution. No .storage edits,
Ingress header/peer/port bypass or private household findings in the public repo.

Next after acceptance: observe a user-started shadow session in one saved zone and
one unlike zone, then build bounded control with explicit ownership. Music/TV and
adaptive preferences follow separately; general Apply and legacy activation stay shut.
