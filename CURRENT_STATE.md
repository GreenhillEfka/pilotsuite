# PilotSuite current state

## 2026-09-26 — Alpha.31 workspace candidate

Implemented a progressive UX redesign over the exact Alpha30 baseline
f79cf5ddd01cf222880da6d432d279d1837e8821. At resume HA installed/offered Alpha30,
started, no pending update; original options and auto_update=true. Alpha31 is not
claimed installed by this candidate document. Read the final PR delivery comment or
completed RELEASE_STATE receipt for later acceptance.

Features: Cockpit, Zonenmodule, Konfiguration, Verläufe, Werkbank and System;
searchable measured zone cards; source/reference/implementation diagrams; module
role filters and source search; before/after role/consent/detector preview;
light/dark/system appearance, density and technical-ID preferences; mobile navigation;
explicit existing read-only structural adoption review, with stale/error invalidation.

The original forms, endpoint write contracts and canonical owners are reused. No
household mutation, role/grant change, new data collector, new runtime capability,
config migration or app permission change. Do not claim presence execution works from
UX tests: the state graph is deliberately a model, not a live state indicator.

Implementation/design/test matrix: docs/UX_WORKSPACE.md. Existing browser flows retain
the full-page supported view; the added actual-app test exercises default workspaces.
Local administrator browser restriction is not bypassed. Exact remote screenshots are
synthetic fixture data; household Ingress acceptance remains separate.

Next after delivery: assess real navigation and configuration usability. Keep backend
helper/provisioning/presence correctness as a separate fault-tested behavior package;
no automatic ownership transfer or learning consent based on a visually ready card.
