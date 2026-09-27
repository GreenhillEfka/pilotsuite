# Current state — Alpha.48 installed, 2026-09-27

The approved real presence-shadow and light-need package is delivered. PR103 release
c33462e5f302565ea61c29fc8127b9883e906bb3 has the exact tested root
b1e89277c12843079f33361d49a05411d1c39642 and app tree
4a87e2273bd985668889123c46e11c3ccedcb79d. Candidate d6ebcd172b305bc8f54b9575ed848b4286a40a34,
CI36313074583 and release-main CI36319498063 passed all four jobs and ten browser suites.
A fresh checksum-verified local checkout passed 555 Python / 60 JS tests, compilation,
53 API contracts and release-preflight. PR102's provenance correction was included
through ancestry; its PR is merged without a separate Alpha47 deployment.

## Delivered user capability

Zonenmodule > Anwesenheit > Präsenz-Livevergleich & Lichtbedarf now offers explicit
shadow configuration/start/stop on confirmed real sources. HA status and independently
computed PilotSuite status are shown together, with reasons, disagreement, source report
age, generation and grace deadline. Pulse/continuous modes, grace, age limit, atmosphere,
explicit outdoor-lux provenance and bounded brightness proposals are configurable.

Accepted events and a local five-second worker advance the existing kernels. Only the
latest operational checkpoint is retained in the existing ContextStore; no new history,
learner or consent is created. Identity/shared revision changes durably suspend the
session. Deadlines survive reconnect/restart. Unknown data and manual holds suppress
unsafe conclusions/proposals. Groups/templates are not implicitly independent sources.

This is shadow evaluation, not actuation. Existing HA automation ownership, entity IDs,
roles, learning grants, legacy activation and general Apply remain unchanged. No real
household shadow session, metadata cleanup or actor action was invoked during delivery.
Contract and limits: docs/PRESENCE_SHADOW.md.

## Native deployment evidence

Fresh backup a7c65d26, 2026-09-27T12:33:27.162716+00:00, contains only PilotSuite
Alpha46 app/data/options, 54,374,400 bytes. Native snapshot/list and backup/details
verified no HA/database/folders, no failed parts/agents or errors, and unprotected local
agent. Verification preceded publication at 12:35:26Z. No extraction or restore drill.

One Store refresh exposed Alpha48; one normal update installed it. Fresh metadata:
installed/offered 0.1.0-alpha.48, started, update_available=false, options and auto_update
unchanged. Exact startup log: 2026-09-27T14:39:46Z, Alpha48/v23/presence_adoption_review;
readiness at 14:39:47Z reports ready, connected stream, fresh snapshot and resolved zone.
Log timestamps are copied as emitted, not independently clock-validated. Existing
partial source capabilities are not transport failures. No additional restart/rebuild
or unrelated app update.

## Acceptance boundary and next step

Synthetic source artifact10928804129 and UI artifact10929985628 were checksum-verified;
phone/dark and desktop/light shadow screenshots were viewed. Real household rendering,
physical-source correctness and independent installed-image/data attestation remain
separate. No Ingress bypass or new household test session was attempted.

Next: a user explicitly confirms sources/settings for one saved-zone shadow session,
then compare against the existing HA status through actual occupancy and grace events.
Repeat with one unlike saved zone before any proposed control/ownership handover.

Previous completed receipt remains at
c33462e5f302565ea61c29fc8127b9883e906bb3:docs/RELEASE_STATE.json.
This four-file closure changes no application code/version; final doc CI goes in comments.
