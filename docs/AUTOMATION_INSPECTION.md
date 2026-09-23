# Selected automation inspection

Alpha.21 extends the explicit reference review in AUTOMATION_REVIEW.md with three
linked review packages: structural detail, an open review plan, and change-aware
export. It does not execute, edit, enable or approve any HA automation.

## Explicit scope and API

First run **Bestehende Automationen prüfen** on a saved draft with current pattern
sources and confirmed targets. Then select **Details prüfen** for one match.
The service repeats search/related to validate current membership before reading
exactly that automation using WebSocket automation/config (entity_id). Contract
verified against [HA Core 2026.9.3](https://github.com/home-assistant/core/blob/2026.9.3/homeassistant/components/automation/__init__.py).
That handler requires admin capability. A denial is a controlled failure, never a
reason to change credentials, permissions or use an edit endpoint. Actual add-on
capability remains a separate live acceptance gate.

POST /api/v1/zones/{zone_id}/drafts/{draft_id}/automation-inspection accepts exactly
revision, zone_revision, automation_id and previous_fingerprint (null or 64 lowercase
hex characters). The automation must match the freshly queried saved scope.
Existing Ingress enforcement, single in-flight comparison, pre/post revision checks
and current-source checks apply. Network I/O does not hold the projection lock.
HTTP 400 rejects malformed inputs, 409 rejects stale scope, 503 rejects denied,
failed, malformed or over-limit upstream reads without raw error details.

## Structural detail and review plan

Known modern/legacy sections, direct entity references, service calls and nested
choose/if/repeat/parallel/sequence/condition/wait structures are summarized.
This is structure, not an evaluator: branch conditions, thresholds, timing values,
messages, scripts, scenes, blueprints and templates are not executed or expanded.
Disabled/dynamic steps and unsupported structures carry limitations. References
inside nested waits or conditional/disabled paths do not prove an initiating cause
or an action that actually runs.

Only draft source/target identifiers are returned as references; unrelated IDs are
counts. Aliases, descriptions, raw values and service payloads are discarded.
Direct script service names are masked as script.* because they can identify
unrelated entities. Known generic service identifiers may be displayed.

Alignment distinguishes source references in trigger structures from target
references in service-call structures. Missing sources/targets create open review
items. Further open checks cover intent, timing/conditions, manual override,
enabled status and risk/recovery. User-authored intent is not proof of behavior.
All checklist states remain open; there is no approval or execution control.

## Bounded and transient

The existing reference request has a 30-second deadline; the selected config read
has a 20-second deadline and 128 KiB WebSocket frame limit. Parsing rejects configs
over 120 KiB canonical JSON, depth 16, 2,000 values or 200 structural steps.
Nothing is silently truncated. Cancellation remains cancellation.

Raw config exists only during the request; it is not persisted, audited or exported.
The report contains a SHA-256 fingerprint of canonical sorted JSON, not the config.
It can identify a change in hidden values without revealing those values. It is a
momentary comparison, not a signature, permission or semantic equivalence check.
The browser sends a previous fingerprint only for the same automation and still
valid draft basis. Another read reports first_read, unchanged or changed.
Changing a label also changes the fingerprint; unchanged does not prove safety.

Results use no-store and the existing transient browser review. Failed retries,
zone navigation or changed draft/zone/source basis suppress stale display/export.
Explicit draft export includes a valid inspection and open checklist and labels
automation_check=structural_review; ordinary stored drafts remain not_checked.
No schema/migration, second semantic owner or new learning collection is added.
Statistics, confidence, rule strength, risk and preference remain separate;
risk=not_assessed and execution.allowed=false, actions=[] remain fixed.

## Acceptance and next slice

Seventeen new synthetic Python cases cover bounded parsing, privacy, partial
alignment, fingerprints, exact HA read command, denial/failure, membership,
revision races, no persistence and the closed apply boundary. Chromium regression
covers details, unchanged/changed recheck, checklist, export, failed retries and
mobile/desktop overflow. Real HA capability and authenticated Ingress are separate
and cannot be replaced by these fixtures or an internal HTTP 200.

Next bounded concept: persist only explicitly authored review notes/dispositions
in the canonical PlanStore, bound to draft revision and inspected fingerprint;
invalidate their current status on source/config change. This is user feedback,
not a safety verdict, evidence score, HA write or action approval. Live learning,
second-zone acceptance and any execution remain separately gated.
