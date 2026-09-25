# PilotSuite AI context

Canonical: GreenhillEfka/pilotsuite, HA app 0d79c5e8_pilotsuite. No new repository.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first.

## Alpha.31 workspace candidate — 2026-09-26

User asked to implement the UX redesign: overview, configuration, visualization,
modern responsive appearance and modular workspaces. A completed Deep Research report
was not available in this session; this implementation uses the actual Alpha30 source
and primary UX references listed in docs/UX_WORKSPACE.md, not a claimed report.

Baseline main f79cf5ddd01cf222880da6d432d279d1837e8821 (PR66) and installed/offered
Alpha30 were read directly. A checksum-verified full source bundle was cloned locally.
Application services, roles, selection persistence, consent and execution capabilities
are unchanged. Root HTML is enhanced by workspace_api.py, which reuses the original
index document. workspace-model.js is a pure presentation model; workspace.js adapts
existing renderers and moves existing forms, without another canonical data store.
workspace.css holds local light/dark/compact display tokens. Settings cache has only
four presentation fields. No runtime enable control or actuator action is added.

The source/reference/state diagrams are structural views, NOT a live runtime acceptance
or timer correctness claim. Alpha28 helper transport and Alpha29 runtime behavior have
not been functionally revalidated by this UX task. Do not interpret readiness as authority.

Local Python/JS and exact remote CI must pass. Keep all existing regression flows and
add actual-app workspace navigation, filtered forms, diff, save/cancel, error, mobile,
theme and no-write checks. Full-page #ps-all remains a supported view. Local browser
navigation was blocked by administrator policy; no bypass. Use normal CI browser evidence.

Release is only after exact candidate CI and fresh completed PilotSuite-only native backup
before merge/publication (auto_update=true). Verify main CI, one native Store refresh if
needed and one scoped update; reread metadata/logs. Do not edit HA config/consents or
bypass Ingress. Record completed deployment in one handoff, final doc CI in PR comments.
