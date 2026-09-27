# Presence-first intelligence: decisions, stages and acceptance

Status: design accepted; Alpha.39 implements the deterministic presence kernel and
Alpha.40 delivers the synthetic lighting preview described below. Neither
activates productive control.
Canonical project remains GreenhillEfka/pilotsuite; no alternative runtime or store.

## Product contract

Presence is the common context for light and optional media, not just a motion bit.
The user is organizing HA entities independently. Development must preserve those
edits: no household renames, role changes, learning grants or automation takeover
as a side effect of this package. Resolve stable identities at use time; a genuinely
replaced source needs review, not inherited confidence. No blanket read access is
interpreted as productive learning or execution consent.

The shared decision chain is:

`validated observations -> presence/situation -> desired comfort -> authority check -> bounded HA action -> independent verification`

One canonical projection supplies every module. Source quality, presence, activity,
chosen ambience, learned preference and action authority are separate dimensions.
A green input card must not turn an unavailable execution capability into a button.

## Delivered in Alpha.38

The existing WorldModel now returns whether a state frame was accepted. Rejected
older/equal/duplicate or malformed frames cannot be consumed as new learning events.
Valid delayed activity remains bounded by the existing consent/retention/dedup rules.
For each light/lux context channel, all source timestamps must exist and be no later
than the activation. Otherwise its value is unknown, not the latest snapshot value.
This is a consistency guard, not reconstruction of history or physical simultaneity.
Previous records are not changed; a future learner must distinguish legacy unverified
context from new timestamp-qualified context, and must not call either causal proof.

Workspace cards use the same effective roles as the server projection. Derived
single-source defaults are labelled, not auto-saved. Comparison temperature is an
optional independent context measurement, never a thermostat setpoint or median input.
Difference display requires good values, matching units, an independent source and
an available zone aggregate. Failed/disconnected reads do not retain the difference.

## Implemented in Alpha.39 source: presence kernel and scenario replay

The corrected kernel uses the existing service and ContextStore, not a second
independent learner. The workspace exposes explanation and replay before activation.
The functional state is occupied, grace, vacant or unknown; manual override is a
separate authority flag, not another kind of sensor truth.

| Observation | Required behavior |
|---|---|
| Fresh valid continuous presence on | Occupied, cancel pending vacancy |
| Motion pulse | Renew recent-presence evidence; no claim of continuous occupancy |
| All configured required sources valid and clear | Start/continue the approved grace interval |
| Grace expires | Recheck sources and generation/deadline before declaring vacancy |
| Required source missing, disconnected or ambiguous | Unknown; never false vacancy from missing data |
| Reconnect/restart | Rebuild from fresh sources and durable deadline; no blind command replay |
| TV playing | Activity hint with bounded policy; not proof that a person is present |
| Own light/music is on | Never a self-sustaining occupancy vote |

PIR off means no new movement, not necessarily an empty room. Continuous occupancy
and pulses therefore require different handling. Group/template sources and their
members must not count as independent votes. Missing dependency information remains
explicit; user confirmation may choose the authoritative existing group/status.

HA timer idle can mean finished, cancelled or never started. An explicit finish event
or approved durable deadline must disambiguate it. Timer restore does not emit a
missed finish event after downtime. Alpha.39 persists lifecycle state, generation and
deadline inside the existing zone context and does not renew it on reconnect. Source
changes/reset discard that operational basis; configuration savepoints omit it.
Manual cancellation remains unknown, not absence. The public runtime enable path and
general Apply remain closed until real sequences, dependencies and action failures
receive separate approval and tests.

Replay accepts exactly five fixed synthetic scenarios. It performs no HA read, write
or persistence and returns an explicit non-execution receipt. Browser GET/reload does
not run it. Results are bound to zone revision and invalidated on zone/revision change,
so a late response cannot overwrite a newer basis.

## Implemented in Alpha.40 source: light policy preview

Presence permits a desired light state; ambient light decides whether/how much light
is needed. Keep outdoor/daylight reference, indoor measured illuminance and actuator
brightness percentage distinct. Lux is not a dimmer percentage. Where indoor lux
includes the lamp itself, avoid the naive on -> bright -> off -> dark oscillation:
use a suitable daylight reference or a separately validated closed-loop policy.

Per zone/profile configure daylight thresholds, hysteresis, stable-signal duration,
minimum command interval, brightness bounds, transition and fallback on lux failure.
A fixture-independent simulation should show the target curve before activation.
Each light must declare supported color modes and Kelvin range. White-only targets
receive no RGB request; Kelvin and color are not sent as conflicting alternatives.
An unavailable lamp does not justify raising all other lights without an approved rule.

Mood means the desired ambience: e.g. focus, relaxed, social or movie. It is selected
by the user or suggested from an explicit activity policy, not guessed human emotion.
Use layered profiles: base daylight compensation + time/activity + chosen ambience
+ limited learned preference. An explicit scene wins until released/expired according
to policy. Do not create a full new scene for every possible combination.

Priority: safety/blockers -> explicit user action/manual lease -> explicit scene or
activity request -> verified presence/daylight policy -> bounded learned correction
-> conservative fallback. Priority changes never enlarge the target allowlist.

## Planned media policy

Music is optional per zone, not the default consequence of any motion. Activation
requires an explicit playlist/source permission, allowed hours, volume ceiling,
minimum dwell and confirmed presence. TV playback on shared audio equipment blocks
music takeover; unknown TV status must not be treated as safely off. Pause/buffering
needs a grace policy rather than immediate switching. TV power-on is not authorized
merely because someone enters a zone.

A controller may stop/restore only the playback session it demonstrably owns and
only while its origin, target/group membership and session token still match.
Manual source selection, queue edits, grouping or volume changes cancel its claim.
Do not automatically ungroup Sonos rooms or overwrite a household queue. If an
integration cannot verify session ownership, stop/resume stays a user-confirmed
proposal. Presence returning after TV ends must not launch an unwanted playlist.

## Dynamic intelligence: local inference first, bounded learning second

A large language model is not required in the realtime loop. Start with a deterministic
presence kernel, transparent activity features and small contextual preference models.
Possible situations include transit, seated stay and confirmed media use; only declare
what the configured sources support. No camera/person identification is necessary.

Learn only from separately permitted evidence: explicit scene/profile choices and
attributable manual brightness/color/media adjustments under comparable conditions.
The existing coarse HA context attribution is not proof of a human action. Unknown
origin is not a positive training label; own actions are excluded to prevent self-
reinforcement. No correction is not automatically approval. A learning proposal must
identify its source/time/profile basis, support, uncertainty and competing explanation.

Candidate algorithms: robust grouped quantiles for preferred brightness; bounded
contextual regression when sufficient diverse samples exist; empirical dwell-time
quantiles for grace suggestions; frequency estimates for explicitly chosen profiles.
These are design options, not installed models. Start with understandable models;
no random exploration, abrupt parameter jumps or opaque reinforcement loop in the house.
Bayesian fusion is another option only with defensible calibrated priors/likelihoods
and dependency handling. Arbitrary weights labelled '98% confidence' are forbidden.

Evaluate chronologically: derive on an earlier interval and test on a later one,
compare against the unchanged baseline, track source coverage and manual corrections,
and separate prediction quality from safe execution. Use time decay for old preferences,
freeze on changed devices/bindings and expose reset/disable per model. Sparse evidence
keeps defaults or recommendations, not manufactured certainty.

Runtime modes:
1. Observe/explain: no new actuator writes; productive collection only with consent.
2. Shadow/replay: show what would have happened, with missed data and conflicts.
3. Suggest: user approves a bounded reusable policy, not every ordinary trigger.
4. Bounded autonomy: only the approved zone/module/targets/parameter envelope; hard
   manual override, rate limits, quiet hours, execution receipts and readback.

Permission and learning remain orthogonal. Changing target identity, expanding
scope or rewriting automations requires a new approval. The model cannot grant its
own permissions or edit its safety envelope. Capability metadata must keep each mode
unavailable until its full UI-to-runtime path is implemented and fault-tested.

An optional LLM can explain findings and compile natural-language preferences into
schema-validated proposals. It cannot send arbitrary HA services, bypass the policy
gate or hot-edit its own production code. Treat entity names, templates and retrieved
notes as data, not instructions. Deterministic operation survives LLM/internet failure.
Local statistical processing reuses PilotSuite's existing compute first; no extra
hardware/model service is assumed. Benchmark latency/memory before adding a model.

## Acceptance and implementation sequence

| Step | Deliverable | Required proof |
|---|---|---|
| 38 | Event/context consistency and coherent role/reference UI | Synthetic regression, full CI, no new actions/consent |
| 39 | Persistent presence kernel + explanation/replay UI | Pulse vs continuous, restart deadline, expiry, unknown sensors/dependencies, no replay mutation |
| 40 | Daylight/mood policy + preview | No oscillation; capabilities, manual override, night exit, bounded transitions |
| Then | Scoped HA executor and one zone rollout | Before-state, per-action authority, readback, lost response and conflict handling; explicit zone approval |
| Then | Optional music/TV arbitration | User playback/queues preserved; real group/session capabilities verified |
| Then | Adaptive preferences | Permitted training evidence, chronological validation, bounded changes, visible freeze/reset |

Learning can run in shadow alongside the stable kernel after consent, without waiting
for every actuator module. Each step must connect existing UI/API/store/runtime paths,
not merely ship another unused contract file. No claim of comfort improvement until
real acceptance demonstrates it. Version numbers beyond the current slice are not
promised. Source cleanup by the user does not block synthetic development or change
productive permissions.

## Primary semantics checked 2026-09-27

- HA timer states, restore and missed events: https://www.home-assistant.io/integrations/timer/
- HA light capability/color contract: https://developers.home-assistant.io/docs/core/entity/light/
- HA playback states and services: https://www.home-assistant.io/integrations/media_player/
- HA Bayesian helper and explicit likelihood configuration: https://www.home-assistant.io/integrations/bayesian/

Architecture above is a PilotSuite proposal. These sources document platform semantics,
not evidence that adaptive PilotSuite control already exists or performs well.
