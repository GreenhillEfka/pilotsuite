# PilotSuite current state

## 2026-09-26 — Alpha.28 installed and runtime-verified

Canonical GreenhillEfka/pilotsuite; app0d79c5e8_pilotsuite. PR63 release commit
8897bdf8b74a745bc0a60f2d7618723e2b035b87; root tree
72c4f12e222aaeee188cf7f12fd6972134cc10a8; app tree
d6fb8b2437dbb8185ada5ec968b080896e4331bf. Exact candidate CI36194932567 and
main CI36195056251 passed all four jobs: tests, browser, reproducible source and amd64
container. Candidate tests ran 394 Python and 48 JavaScript tests.

Before publication, native snapshot/list plus backup/details verified backup1122b3d9:
2026-09-25T22:06:09.564034+00:00, only PilotSuite Alpha.27, 54,251,520 bytes,
no HA/database/folders or failed components, unprotected local agent. No restore drill.

Exactly one native Store refresh and one PilotSuite update completed. Metadata confirms
installed/offered Alpha.28, started, no pending update, auto_update=true and all four
options unchanged. No extra restart/rebuild or unrelated app update. Startup confirms
architecture v21 and bounded_helper_provisioning; repeated readiness confirms ready,
stream connected, fresh snapshot and resolved zone. Existing partial capability states
are unchanged.

## Delivered capability

One real, deliberately bounded helper executor now exists in the canonical PlanStore
mutation path. Only one current planned presence-delay timer may be submitted per
explicit confirmation. Before-image collection read, exact existing-helper reuse,
revision recheck immediately before write, supported timer/create transport, independent
read-back, unknown-outcome no-retry rule, durable transaction journal and transaction-
owned rollback are implemented. Pre-existing/mismatching helpers are not renamed,
deleted or adopted. Generic plan apply remains denied.

The Zonenbasis UI exposes this single action and requires a second browser confirmation.
No household helper was created as part of development/release. No automation takeover,
presence runtime, light/music/climate action, role change or learning grant occurred.

## Next

Authenticated household Ingress acceptance of the Alpha.28 UI and app-principal timer
collection/write capability remains separate. Do not bypass Ingress or create a timer
outside the explicit PilotSuite UI approval. Once one zone's bounded helper path is
verified, implement presence timing/restart reconciliation in Issue56 while existing
HA automations remain authoritative. Then proceed to controlled adoption and lighting.
