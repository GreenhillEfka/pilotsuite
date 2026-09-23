# Persistent routine drafts

Alpha.20 adds an explicit transient reference review; see AUTOMATION_REVIEW.md.
Semantic duplicate assessment and execution remain unapproved.

Alpha.19 implements the user-approved first proposal-authoring slice. A pattern
card offers **Routine entwerfen**. It creates one explicit user-authored draft per
zone/pattern, never an automation. Repeating the request returns that same draft.

## Ownership and data

Existing PlanStore is the semantic owner. SelectionStore owns migration of the
shared SQLite database to schema 7, backing up the previous database before DDL.
The new routine_drafts table stores ID, zone/pattern reference, source revision,
draft revision, timestamps and user fields. Legacy denied dry-run plans remain in
plans.jsonl under the same PlanStore, unchanged; they are not copied or migrated.

Fields: title, comfort goal, target entity IDs, trigger, conditions, exceptions and
manual-override policy. Text is declarative, never evaluated or interpreted as HA
service calls. New targets must be currently available and explicitly relevant in
the selected zone, in light/switch/fan/climate/cover/media_player domains. No target
is preselected. Title is limited to 120 characters, other texts to 1,000, targets
to 20; at most 100 drafts globally. The cap rejects creation rather than discarding
user work. Existing drafts can still be retrieved/edited at the cap.

No observation, household state, inferred time window, pattern title or evidence
snapshot is stored in the draft. Current patterns come from the canonical
ContextStore projection on read. User text may contain personal information and
stays in local app data, not audit messages or repository fixtures. Only an explicit
JSON download exports the user draft and its currently derived pattern view.

## Revisions, expiry and deletion

POST creates from a currently qualifying pattern with the current zone revision.
PATCH checks both draft and zone revisions under BEGIN IMMEDIATE. Concurrent saves
cannot silently overwrite each other. Explicit refresh_source acknowledges the
current zone basis only while the original pattern still exists; it grants no
execution approval. Merely editing text does not acknowledge changed sources.

Zone changes produce zone_changed, expired/reset patterns produce pattern_missing.
Removed or no-longer-confirmed targets remain visible as unavailable until the user
removes them. Drafts remain editable even if evidence expires or learning is off.
Learning reset deletes learning evidence/feedback, not these authored notes. The UI
states this. DELETE removes only the selected draft, with a revision guard.

Incomplete required fields produce incomplete. A changed/missing basis or missing
targets produce needs_review. Complete fields with a current basis produce
ready_for_review: this means only structural completeness, never risk approval.
Rolling evidence changes within the same pattern/zone revision are shown through
the fresh projection, not as immutable evidence that has been accepted.

## HTTP/UI contract and boundary

- GET/POST /api/v1/zones/{zone_id}/drafts
- PATCH/DELETE /api/v1/zones/{zone_id}/drafts/{draft_id}
- Context responses include drafts and confirmed target candidates.
- Conflict is HTTP 409; malformed/unknown/foreign inputs are HTTP 400.
- All routes inherit the existing Ingress guard and projection lock.

While editing, normal zone/configuration changes and background reload are locked.
Failed/conflicting saves retain entered fields; explicit reload asks before
discarding edits. DOM text uses textContent; user text is never HTML. Export is
review JSON only. automation_check=not_checked and risk=not_assessed are explicit.
execution.allowed=false and actions=[]; existing PlanStore.apply still always
rejects. Pattern statistics, confidence, rule strength and preference stay separate
from user intent, structural completeness and unassessed draft risk.

## Acceptance and next slice

Synthetic regressions cover persistence/restart, idempotency, writer conflicts,
zone/source changes, reset/expiry, target validation, deletion, migration backup,
capacity and the closed apply boundary. Chromium covers create/edit/reload/export,
preserved conflict inputs, escaped text, zone isolation and responsive layout.
CI is separate from authenticated real HA Ingress acceptance. Do not enable real
learning or edit household roles/automations to create acceptance fixtures.

Next: a read-only comparison with existing HA automations, identifying overlap and
unknowns without claiming causality, creating automations or mutating them. Real
learning quality, second-zone acceptance and governed actuation stay separate gates.
