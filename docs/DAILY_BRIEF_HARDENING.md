# Daily brief — full-source hardening integration

2026-09-25, same PR #54 / feat/zone-daily-brief. Canonical repository only.

## Source and scope

R2's pinned inputs matched full PR HEAD 6b1e9cbb4b02c4da86ae751e9772b95b07c1b9bd,
recovered from SHA256-verified source-only artifact 10823645624 of CI 36031998852.
R2's integrity manifest matched. Original files were backed up before application.
No HA data, secrets, local backups or browser profiles belong in the source commit.

R2 derives one retained review from existing inventory/ContextStore/review_brief.
Same-zone/revision/source checks, explicit learning/readiness, bounded counts and
coverage precede candidate selection. Duplicate identities and contradictory data
fail closed. Rejections/deferrals do not change statistics and are never promoted.
Chronological day partitions allow a split crossing a calendar day. Missing later
evidence is not evidence of inactivity. No new learner, store, route or collection.

UI invalidates on same-zone reload, zone change and failed current reads. Stale
responses cannot revive an invalid candidate. Equal data keeps focus/expanded
explanations while refreshing the activation-time basis. Unsaved selection and
routine text are neither saved nor discarded. All output is bounded text, including
Unicode code-point limits. The link opens the existing workbench, never an actuator.
This is not a daily forecast, a causal conclusion or a proven household benefit.

## Full repository checks

The previous CI failed: CollectionStateTests fabricated an inventory without
zone_id, and the stricter projector correctly rejected it. The same failure was
reproduced locally; the fixture now carries its real synthetic zone identity.
The five original daily-brief free test functions were ignored by unittest. The
replacement contains 41 unittest cases, actually collected by existing CI.

Six new tests exercise the real aiohttp application, actual World/Zone/Selection/
Context/Plan stores and synthetic inputs. GET, HEAD and export preserve the full
SQLite dump and perform no automation/config lookup. Preference, disconnect,
unavailable source, pause, revoked learning, unknown/other zone and denied Apply
are checked without changing real household state. Existing JS refresh tests now
supply the actual invalidation dependency rather than silently skipping that path.

A shared synthetic fixture also feeds the new full-application Chromium flow in
normal CI: responsive UI, navigation/focus, unsaved draft, reload race/error,
source availability, preference and zone isolation; unexpected HTTP writes,
external requests, page errors or automation/config reads fail the test.
No production ingress peer, port or authorization setting is changed by fixtures.

Local full-suite runtime: Python 3.13.5 / aiohttp 3.13.3, Node 22.16.0, not the
pinned CI Python 3.14 / aiohttp 3.13.5 / Playwright 1.62.1. The final local suite passed 298 Python tests (including
the four source-gate regressions) and 48 JavaScript tests. Existing SQLite ResourceWarnings are not a warning-free
claim. 35 isolated Chromium checks against exact integrated function text passed.
Full-app local browser navigation returned ERR_BLOCKED_BY_ADMINISTRATOR. That
route was stopped, not bypassed. The normal authorized CI is the full-app browser
acceptance gate. Neither kind of synthetic test is authenticated household UI.

CI additionally distinguishes last published source from historical installation
receipts. Same-version application-tree changes are rejected, while documentation-
only commits with identical app trees remain valid and confer no deployment rights.
Strict release_preflight still requires a newer version; CI's --allow-unchanged
path does not relax release gates. All five version markers and changelogs use
Alpha.24. No release or deployment is implied until the PR records actual receipts.

## Next

Exact PR CI, fresh PilotSuite-only prepublication backup, expected-head merge,
exact main CI and the established normal Store path. Preserve options/consents and
avoid another Alpha.23 install. Real Ingress, data/image attestation, config-read
capability and demonstrated usefulness remain independent acceptance items.
