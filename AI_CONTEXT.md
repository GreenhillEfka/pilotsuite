# PilotSuite AI context

Canonical: GreenhillEfka/pilotsuite / app 0d79c5e8_pilotsuite / architecture v21.
Read CURRENT_STATE.md, docs/RELEASE_STATE.json and docs/RELEASE_RUNBOOK.md first.

## Resume - Alpha.31 UX delivered, 2026-09-26

PR67 is merged as 75caa39df10a7eb25a0a3c85c0a526475d18b03b. Exact candidate
CI36201287332 and release-main CI36201656060 passed all four jobs, including eight
browser suites. Local complete checkout: 405 Python and 53 JavaScript tests passed.
Final root d651049d4afbae883f642c5786930ac9cb6e7772; application tree
05557cea66e5a9ca99489331f6f39f05839b1bcf, reread from the remote tree and local Git.

Fresh completed PilotSuite-only backup319e9e3b was checked with snapshot/list and
backup/details BEFORE publication. One normal Store refresh and one scoped update
completed. Installed/offered Alpha31, started, no update pending; all four options
and auto_update=true preserved. Startup identifies Alpha31 / presence_adoption_review.
Repeated post-start logs show ready, stream connected, fresh snapshot and zone resolved.
No explicit restart/rebuild or other-app update. Do not repeat deployment to resume.

## Implemented workspace

Cockpit, Zonenmodule, Konfiguration, Verlaeufe, Werkbank and System; measured zone
cards and filters; four module source/reference/implementation diagrams; searchable
canonical role forms and before/after roles/consent/detector preview; local light/dark/
system theme, density and technical IDs; sidebar/mobile navigation with dirty guards.
The original document/forms/listeners and canonical stores remain authoritative.
workspace-model.js is pure presentation; workspace.js adapts existing renderers;
workspace_api.py injects assets into the one HTML document; rescue remains minimal.
No new permission, data migration, collector, runtime activation or household edit.

## Acceptance boundaries and next work

Checksum-verified CI screenshot artifact10891478892 was visually reviewed at desktop,
tablet and phone sizes in both themes. Actual-app tests use synthetic data, not an
authenticated household session. Local browser navigation was denied by administrator
policy and not bypassed. No Ingress header/peer/port change or new proxy probe.
No completed Deep Research report was available; docs/UX_WORKSPACE.md records the
actual source/reference basis, not an invented report or blanket WCAG certification.

State/dependency diagrams are models, NOT verified live presence/timer operation.
This UX release does not certify Alpha28-30 helper transport or runtime correctness.
Do not activate or take over household automations based on ready-looking cards.
Continue with household usability feedback and a separate fault-tested backend package;
keep existing HA automation authority and manual overrides until scoped verified takeover.
Unknown results never justify blind retry, inferred ownership, false absence or deletion.

Final documentation CI receipts belong in the PR discussion, not another status-only
commit/release loop. This handoff does not change any application file or version.
