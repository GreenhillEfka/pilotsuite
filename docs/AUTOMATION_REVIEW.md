# Existing-automation reference review

Alpha.20 adds the first bounded comparison slice to saved routine drafts. Click
**Bestehende Automationen prüfen** to see existing HA automations referencing the
draft's confirmed targets or current pattern sources. Results separate target
references from source references and prioritize target matches. This is a review
aid: sharing an entity is neither semantic equivalence nor proof of a conflict.

## Exact scope

The existing HA client issues only WebSocket search/related with item_type=entity
for the union of saved targets and current pattern sources. Contract verified
against [HA Core 2026.9.3 search implementation](https://github.com/home-assistant/core/blob/2026.9.3/homeassistant/components/search/__init__.py).
The automation response key contains automation entity IDs; other response keys
are discarded. No automation config, trace, state history or person relation is
stored or forwarded. No write/service/configuration request exists in this path.

Entity lookup does not fully cover device/area/label targets, dynamic templates or
indirect calls via scripts, groups and scenes. Trigger/condition/action semantics,
timing, enabled status, risk and manual override are unassessed. No match therefore
means only no direct entity references found, never safe, duplicate-free or approved.
This limitation is shown even after an otherwise successful empty result.

## Boundaries and freshness

POST /api/v1/zones/{zone_id}/drafts/{draft_id}/automation-review accepts exactly
revision and zone_revision, not caller-provided HA IDs. It inherits Ingress access
control. The service retrieves the canonical PlanStore draft and requires a current
pattern basis and at least one confirmed available target. Learning need not be on.
Draft/zone revisions and source membership are rechecked after network I/O. A changed
or reset basis cannot return a valid result. The projection lock is released while
HA is queried; only one comparison runs at a time, without a growing request queue.

Limits: 40 entity references, 200 related automations total, 1 MiB per WS frame and
30 seconds total. Over-limit, denied, malformed or failed requests return controlled
503 with no partial matches or private upstream details. Bad input is 400; stale
revision is 409. Cancellation remains cancellation. Nothing is silently truncated.

Results live only in the current HTTP response/browser view (Cache-Control no-store).
No schema change, second owner, automatic polling or new learning collection.
Zone navigation clears them; changed revisions/sources/targets suppress display and
export. A failed retry clears the previous result. Timestamp labels a momentary
view: later HA automation changes require another explicit check. Ordinary stored
drafts retain automation_check=not_checked. Explicit JSON export adds only a valid
current-session reference review and labels it limited_reference_review.

## Meaning and acceptance

duplicate_assessment=not_determined, risk=not_assessed and execution.allowed=false
remain fixed. Observation counts, confidence, rule strength, preference and authored
intent are untouched. The PlanStore apply boundary remains closed.

Twelve new synthetic regressions cover read-only commands/scope, validation/limits,
partial failures, denied access, timeout/cancellation, transient results, revision
races and reset during lookup. Chromium covers positive/empty/error results, stale
result suppression, export and responsive layout. No household scan is performed
for development; authenticated live UI/HA capability acceptance stays separate.

Next bounded concept slice: inspect explicitly selected matching automation
definitions read-only, distinguish trigger/condition/action references and mark
unsupported/template behavior unknown. Never infer causality from an entity match
or create/modify an automation as part of comparison.
