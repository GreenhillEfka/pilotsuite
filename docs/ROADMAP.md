# Roadmap — continue, do not restart

## 0.1 alpha — reliable observation (current)
- Alpha.21 is published (PR #47, main CI 35914643847 green: 192 Python, nine JS,
  Chromium, amd64). Three read-only packages: selected automation structure, an
  open review plan, and change-aware combined export (ADR-029).
  HA remains alpha.18 installed/offered; scoped backup 697876b6 is verified.
  Next delivery: matching Store offer, source/backup recheck, update once and real
  runtime/Ingress/config-read capability acceptance. Next concept: explicit authored
  review notes/dispositions in PlanStore, tied to draft revision/config fingerprint
  and stale after changes. No action approval. Live learning/second-zone gates stay
  separate.
- Preserve canonical repository and read-only boundary.
- Normalize units, explicit missing evidence, stable suggestion identity.
- Guard Ingress peer; test actual proxy path and browser assets.
- Distinguish snapshot freshness, stream health and sensor validity.
- Ship foundation fixes before claiming live acceptance.
- Follow RELEASE_RUNBOOK.md for every release; alpha.16 adds the requested zone
  guide to existing setup and optional learning, without another state owner.
  Alpha.16 is installed and user UI acceptance is confirmed. Alpha.17 extends
  retained-evidence review with the shared chronological split; PR #37/main CI
  35874744954 are green. Alpha.17 is installed; runtime/read-only checks passed after
  scoped backup fcbbc115. Next is authenticated temporal-view/export acceptance,
  then review of already-consented evidence. No actuation.

## 0.2 — consented read-only learning
- Compose Habitus zones and sensor roles from HA identifiers.
- SQLite schema/migrations for own definitions, bounded evidence and feedback.
- Attribute manual/existing-automation/own actions where possible.
- Separate observed statistics, confidence, severity and preference.
- One traceable habit -> proposal -> durable feedback loop.
- Consent, retention, export, delete/reset and replay regression fixtures.
- Test a second unlike zone; no execution.

Current bounded slice: correlate HA service/state contexts only with active consent,
store no identifiers, and expose uncertainty. Exact automation identity is not
available from generic context alone. Own-action exclusion remains blocked until a
governed execution owner exists; the read-only alpha cannot generate own actions.

## 0.3 — governed action pilot

Preparation: pattern workbench with review briefs and evidence chains (ADR-025).
Alpha.16 packages the workbench, UI fixes and zone guide and is installed.
User UI review of alpha.16 guide/workbench is confirmed. Temporal review remains
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
