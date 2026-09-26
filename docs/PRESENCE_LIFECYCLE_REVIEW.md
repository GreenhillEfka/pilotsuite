# Presence lifecycle review

Alpha.37 extends the existing explicit inventory analysis; it does not add a second
review engine or persistence owner. The projection reads one selected current HA
automation configuration, the current bounded entity catalogue and its device-class
metadata. It emits review questions only when literal structure supports them.

## Recognized questions

1. **Boundary close can clear presence.** A state trigger for a door, window, opening
   or garage door becoming closed selects a direct `input_boolean.turn_off` call. The
   same boolean is also directly turned on elsewhere in the automation, making it a
   plausible derived room status. Closing a boundary is not proof that the area is
   empty, so the desired exit semantics remain a user decision.
2. **Activity edge alone refreshes a timeout.** A motion, occupancy or presence source
   becoming active selects a direct `timer.start`. A state trigger fires on the edge;
   continuous active state supplies no further edge. Whether the source normally
   resets soon enough and whether another event refreshes the timer remain open.

The response contains structural paths, never authored trigger IDs, raw configuration,
aliases or private payload values. Shared trigger IDs preserve every matching path.

## Conservative boundaries

- Device classes, not entity names, establish source meaning.
- Disabled and dynamically enabled branches do not become active findings.
- Dynamic IDs, indirect service targets, ambiguous boolean selector logic and stale
  transport snapshots cannot become findings.
- A finding is neither a runtime trace nor proof of a defect. It does not establish
  occupancy, automation equivalence, safety, preference, risk or execution permission.
- The existing explicit read remains bounded to at most eight configurations per
  request. GET/reload does not start this analysis.

The UI adds one derived filter and explains exactly one next step: review the intended
presence/timeout behavior in the existing HA automation. There is no automation write,
repair plan, autosave, new learning source, consent change or actor call.

## Synthetic acceptance

Tests cover the two questions independently, no-status false positives, device-class
semantics, disabled/dynamic branches, ambiguous selectors, stale snapshots, legacy
sections, duplicate trigger IDs, private-ID removal and unchanged ContextStore,
PlanStore, HA configuration and control-call counts. Real household acceptance remains
separate and read-only.
