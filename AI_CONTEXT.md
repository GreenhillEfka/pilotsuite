# PilotSuite AI context

Canonical GreenhillEfka/pilotsuite / app 0d79c5e8_pilotsuite / architecture v21.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first.

## Alpha.37 candidate: presence evidence before adaptive control

Base cbf43ccebdfb6244a73ed379335d80eca4c5db3e; installed Alpha.36 at resume.
The user is organizing household entities. Continue software development without
renaming/rebinding household entities, editing automations, or changing consent.
Prioritize presence -> daylight/mood light -> optional music/TV -> bounded adaptation.
Full design and acceptance sequence: docs/PRESENCE_FIRST_INTELLIGENCE.md.

Implemented: explicit WorldModel frame acceptance, rejection propagated into learning,
per-channel event-time light/lux checks, coherent effective-role cards with derived
provenance, and optional external comparison temperature with guarded difference.
Existing data/consent/retention owners and action capabilities are unchanged. No new
controller, learner, database, migration or productive collection. Old context records
are retained, not retroactively certified. Keep legacy presence activation closed.

Local 485 Python / 58 JS tests and contracts pass. Added actual-app browser checks use
synthetic data only. Local browser navigation is blocked by administrator policy; no
bypass. Exact remote CI, screenshots, scoped backup and installation remain gates.
Do not describe this candidate as installed until fresh native verification exists.

Next implementation: persistent presence kernel with source-type/dependency handling
and integrated explanation/replay UI, then one explicitly approved zone after fault
tests. Never ship a disconnected contract as completed control. Mood denotes intended
ambience, not inferred human emotion. TV playback must not be interrupted by music.
Maintain existing identities and manual overrides. No Ingress bypass or proxy retry.
