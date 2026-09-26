# Roadmap — continue, do not restart

## 0.1 alpha — reliable observation (current)
- CURRENT_STATE.md and RELEASE_STATE.json own current delivery/acceptance facts;
  do not repeat old installations or reimplement completed compass/daily-brief work.
- Existing inventory and routine reviews now include bounded trigger-ID integrity.
  Actual source, CI, backup, runtime and household UI remain separate evidence.
- Alpha.35 closes the package-overwrite gap in the explicit global scan with
  a transient cumulative view, progress, integrity filters and conservative invalidation.
- The complete 48-route `/api/v1` inventory is now checked against the explicit
  registration source; route/documentation drift fails validation instead of accumulating.
- Next: authenticated read-only acceptance against the four existing saved zones,
  starting with Erdkellerbereich. Read canonical IDs; do not infer membership.
- Development may read HA-wide entities/automations under explicit user authority.
  Productive learning still requires its own source/zone consent. No new collection.
- Existing HA rules can contain errors; review references and desired behavior before
  proposing repairs. Missing IDs never justify guessed replacements or broad writes.
- Preserve canonical ownership; transport freshness, physical validity and domain
  completeness differ. Demonstrated comfort benefit precedes new algorithms.

## 0.2 — consented read-only learning
- Compose Habitus zones and sensor roles from HA identifiers.
- SQLite schema/migrations for own definitions, bounded evidence and feedback.
- Attribute manual/existing-automation/own actions where possible.
- Separate observed statistics, confidence, severity and preference.
- One traceable habit -> proposal -> durable feedback loop.
- Consent, retention, export, delete/reset and replay regression fixtures.
- Test a second unlike zone; no execution.

Implemented bounded slice: correlate HA service/state contexts only with active consent,
store no identifiers, and expose uncertainty. Exact automation identity is not
available from generic context alone. Own-action exclusion remains blocked until a
governed execution owner exists; the read-only alpha cannot generate own actions.

## 0.3 — governed action pilot

Preparation: pattern workbench with review briefs and evidence chains (ADR-025).
Alpha.16 has historical user acceptance of its guide/workbench. Current installation and authenticated UI acceptance are recorded separately in
RELEASE_STATE.json. Temporal review remains
a read-only preparation and never grants action permission.
Real learning and second-zone acceptance remain prerequisites for actuation.
- Typed allowlisted actions, scope/expiry, conflict and idempotency handling.
- Review existing HA automations before proposing duplicates.
- Backup as required, precondition recheck, verify, action-specific recovery.
- One reversible low-risk action only after explicit approval.
- Disposable-HA fault tests before real actuation.

## 0.4 — useful native surfaces
- Thin optional HA adapter for entities and Conversation.
- Reuse HA Assist and existing device integrations.
- Module/automation review, explanation graph, Dev/Wiki views.
- HomeKit candidate review; optional LLM/RAG, never mandatory.

## 1.0 — demonstrated reliability
- Golden Zone plus second-zone acceptance over an agreed observation period.
- Stable contracts, tested migrations, signed multi-architecture images.
- Recovery drills, privacy controls, operational documentation.
- Broader autonomy remains separately authorized and bounded.

No version number or green unit suite substitutes for live acceptance.
