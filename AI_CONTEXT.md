# PilotSuite AI Context

Canonical: GreenhillEfka/pilotsuite / HA app 0d79c5e8_pilotsuite / architecture v21.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first.

## Resume — Alpha.28 delivered, 2026-09-26

PR63 squash-merged as 8897bdf8b74a745bc0a60f2d7618723e2b035b87; root tree
72c4f12e222aaeee188cf7f12fd6972134cc10a8; app tree
d6fb8b2437dbb8185ada5ec968b080896e4331bf. Candidate CI36194932567 and main
CI36195056251 passed all four jobs. Fresh PilotSuite-only backup1122b3d9 completed
and backup/details verified BEFORE publication: only Alpha.27, 54,251,520 bytes,
no HA/database/folders or reported failures. One native Store refresh and one
PilotSuite update. Alpha.28 installed/offered/started, update_available=false,
auto_update=true and options unchanged. Startup says mode=bounded_helper_provisioning;
readiness is ready/stream/fresh/zone-resolved. No extra restart/rebuild, other-app
update, household helper creation, automation edit, actuator call or learning change.
Do not repeat this delivery to resume.

## New bounded capability

Alpha.28 opens exactly one HA write: the current zone foundation's planned
PilotSuite presence-delay timer. It requires exact zone revision and a second explicit
in-app confirmation. The executor reads the timer collection before writing, exactly
reuses a matching existing helper without adoption, rejects mismatches, creates only
through timer/create, then independently reads the collection again. A lost/timeout
response is never blindly replayed. Rollback deletes only an identity whose creation
response was positively confirmed by this same transaction and whose pre-image proved
absence. PlanStore durably journals approval/outcome. HA and local journal are not an
atomic transaction. Generic PlanStore apply, automations, actuators and learning writes
remain closed. No real household timer was created during release.

## Next implementation

First perform authenticated household UI/app-principal acceptance of the new helper
path without bypassing Ingress. Actual helper creation remains an explicit user action
inside PilotSuite. After the bounded timer executor is proven on one zone, continue
Issue56 with presence timing semantics: confirmed/pending/free/unknown, restart/deadline
reconciliation and no timer-finished-alone absence claim. Existing HA automations remain
responsible until a separate backed-up takeover is reviewed. Then lighting; media and
climate later. Preserve manual overrides, identities, unknown fields and no implicit
learning/ownership. No direct .storage edits, guessed replacements or blind retries.
