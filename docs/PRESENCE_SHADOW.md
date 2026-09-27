# Live presence comparison and light need — Alpha.48

## Delivered contract

An explicit, revision-bound session evaluates real confirmed HA observations using
`advance_presence` and `advance_lighting_preview`, not another presence controller.
The original HA status is comparison-only. This module contains no HA write client.
Its configuration and latest checkpoints belong to the existing ContextStore;
ordinary learner records and their consent/retention rules remain unchanged.

Settings: signal type per confirmed raw source; grace (1–86400 seconds); raw source
report age (30–86400 seconds); optional confirmed outdoor lux; atmosphere; bounded
brightness range; optional vacancy-off proposal. This last option extends the existing
lighting policy with a default-false flag; old synthetic scenarios are unchanged.

Sources must be independent registry-backed binary sensors. Ambiguous/unresolved
identities and derived template/group/helper sources do not silently become raw input.
A known group requires a future independently reviewed dependency mapping. Selection
uses explicit organization bindings or explicitly persisted roles, never UI defaults.
A changed identity or shared zone revision suspends the stored session. Reverting the
identity later does not undo a recorded suspension; confirmation is required again.

## Time and recovery

Only frames accepted by WorldModel can carry new pulse evidence. Pulse deadlines use
the event timestamp, not arrival time or a repeatedly read high level. A still-high
pulse sensor after its deadline cannot establish clear. Required missing/unknown/stale
sources prevent vacancy; cold all-clear starts do not fabricate a prior stay.
A local five-second task advances deadlines without extra HA/recorder reads. Disconnect
withholds current displays and preserves the deadline; reconnect never renews it.
Light stabilization is reset across gaps. Source-report age is not physical accuracy.

HA helper/actuator values are held states, not physical sample timestamps. They can
remain valid as current HA comparison/control-state observations without being recently
changed. Their unknown/unavailable states still block conclusions/proposals. Physical
presence and lux sources separately require bounded report age. References:
https://www.home-assistant.io/docs/configuration/state_object/
https://developers.home-assistant.io/blog/2024/03/20/state_reported_timestamp/
HA timer events are not assumed to replay on startup:
https://www.home-assistant.io/integrations/timer/

## Persistence and API

GET is side-effect free. Explicit start/stop advances the canonical zone revision and
preserves all unrelated config/evidence. Accepted latest-only checkpoints do not advance
user revision. Transaction checks bind each checkpoint to its session and revision.
No event timeline, new schema, external dependency or metadata cleanup is introduced.
Configuration savepoints exclude operational shadow state; restoring cannot activate it.
The small rendering cache is disposable and cannot confer authority. Stale responses
or missing freshness hide current settings. One zone's optional storage error must not
break the main HA stream or the other zones.

`GET/POST /api/v1/zones/{zone_id}/presence-shadow` remains Ingress guarded. The POST
allowlist accepts start/stop, revision, confirm and bounded settings. It cannot take
state observations, target devices, executable service names or arbitrary URLs from a
request. Light targets are existing explicitly selected light-role entries only.
Every response returns `execution.allowed=false`, `actions=[]` and no history collection.

## UX and tests

The module card shows HA/PilotSuite status, comparison, reason, last observation,
generation, grace deadline, source age, blockers and bounded light proposals. Form
edits and pending requests cannot be lost by workspace/zone navigation. Empty/missing
sources explain prerequisites. Local preferences do not contain operational data.

Tests cover real ContextStore/HTTP lifecycle, cold start, pulse/continuous states,
expiry, unknown inputs, age, disconnect/restart, held helper values, identity/revision
changes and durable suspension, savepoint exclusion, unchanged consent, regular local
worker execution, light provenance/stability, manual blockers and zero HA writes/scans.
The new actual-app browser suite uses disposable synthetic data and verifies start,
comparison, deadline, light proposals, themes, phone/desktop widths, reload, suspension
and stop. This is not household UI acceptance or proof of physical sensor correctness.
Local browser policy was respected; no Ingress or browser bypass is permitted.

## Remaining scope

No automation takeover, device actuation, technical-ID migration, media/TV controller,
or adaptive preference learner. Inspect unlike real zones before considering control.
Existing HA logic stays authoritative. This release never starts a household session
as an installation test; the user chooses its sources and settings in the UI.
