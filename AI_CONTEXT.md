# PilotSuite AI context

Canonical GreenhillEfka/pilotsuite / app 0d79c5e8_pilotsuite / architecture v23.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first.

## Resume: Alpha.48 live shadow delivered, 2026-09-27

PR103 merged without source changes as c33462e5f302565ea61c29fc8127b9883e906bb3.
Root b1e89277c12843079f33361d49a05411d1c39642; app tree
4a87e2273bd985668889123c46e11c3ccedcb79d. Candidate CI36313074583 and release-main
CI36319498063 passed all four jobs and ten browser suites. Fresh complete-checkout
rerun passed 555 Python / 60 JavaScript tests and 53 API contracts. PR102's historical
provenance fix is preserved as an ancestor and its PR is merged; no separate Alpha47
installation was required.

Fresh native backup a7c65d26 completed BEFORE publication: only Alpha46 app/data,
54,374,400 bytes, no HA/database/folders or failed parts. Snapshot list and backup/details
verified. One native Store refresh and one scoped update installed Alpha48. Metadata
confirms installed/offered/started, no pending update, all options and auto_update=true
unchanged. Startup identifies Alpha48/v23/presence_adoption_review; readiness confirms
connected stream, fresh snapshot and resolved zone. No extra restart/rebuild or other
app update. Do not repeat this delivery to resume.

## Functional contract

The existing presence and lighting kernels consume confirmed real observations in an
explicitly started per-zone shadow session. HA room status is comparison-only; it never
feeds itself back as evidence. Raw pulse/continuous modes, grace, report age, chosen
atmosphere, optional explicitly confirmed outdoor lux and brightness bounds are editable.
UI: Zonenmodule > Anwesenheit > Praesenz-Livevergleich & Lichtbedarf. Existing labels
in the UI use the original German spelling. Start/stop uses the shared zone revision.

Accepted events and a local five-second worker update only the latest checkpoint in
ContextStore. No new learner/history/schema. Deadlines survive reconnect/restart;
unknown sources block false vacancy. Identity/configuration/revision changes durably
suspend the session until explicit reconfirmation. A held HA helper state is not a
physical measurement. No device action or automation takeover is authorized; responses
keep execution.allowed=false and actions=[]. Contract: docs/PRESENCE_SHADOW.md.

## Acceptance and next step

Exact checksum-verified synthetic desktop/mobile screenshots were visually reviewed.
Real authenticated household UI and physical-source behavior remain unverified. No
household session was started, role/consent changed or entity renamed during delivery.
No old denied proxy/header/port route was retried; Ingress protection remains unchanged.
General Apply and legacy presence activation stay closed. Existing authorized metadata
name-cleanup capability is unchanged; do not mislabel the whole app hard_read_only.

Next: inspect a user-confirmed shadow session in the saved Erdkellerbereich and then
one unlike saved zone. Compare HA/PilotSuite states, actual source report ages, grace,
manual holds and light-need reasons before considering bounded control. Do not infer
outdoor lux or independent raw evidence from a name. User entity cleanup continues
independently; saved zone IDs and the three additional zones must never be recreated.
Final documentation CI receipts belong in PR comments, not another release/doc loop.
