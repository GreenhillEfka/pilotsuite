# Current state — Alpha.77 installed, currently stopped

## Fresh check, 3 November 2026

The user asked for autonomous work without household testing. Fresh HA metadata
at 20:04:56 UTC reports Alpha.77 installed/offered and **stopped**. The four app
options match the beginning of this check. No start, restart, update, backup or
household write was performed. The reason for stopping is not established.
Do not describe the October ready/running receipt as a current runtime observation.

Current main at entry: `503793b994ee9c5c3b0238429139e5b6fa494d10`; no open PRs.
Only the original untracked AGENTS.md was present and remains unchanged.
One package: `test/structure-offline-reliability`. No app-code or version change;
the published Alpha.77 app tree remains `af4932391a58d77bb8b94d75025ec9ecbf040d64`.
The old heartbeat remains paused; no new agents, chats or scheduled work.

## Autonomous verification

A fresh disposable Python 3.14 environment passed 739 Python tests, 77 JavaScript
tests, 68 API contracts and test discovery. Repeated Python audit after garbage
collection: zero ResourceWarnings. All five current browser suites passed locally.

The existing structural browser now additionally covers missing, disabled and
renamed saved light references, replacement under the same entity ID, and a genuine
competing revision. Missing links remain selected and visibly unresolved; unchanged
save retains the original identity. Replacement and stale saves preserve the open
draft and make no persistent change. Structure, members, roles, analysis choices
and mocked HA-write counters are asserted, not inferred from a successful click.
These checks passed the existing application; this is new regression coverage,
not a claim of a newly fixed production defect.

Mobile dark missing-link and desktop editor screenshots were inspected; current
responsive/theme checks pass. Test screenshots stay in ignored output/playwright.
The fixture never connects to household HA. Actual app startup, current saved-zone
readback and physical household acceptance were not performed. Exact branch/main
CI evidence belongs in the PR, not another documentation-only receipt chain.

## Product scope and historical acceptance

The active product remains zone overview → structure editor → zone documentation
(ADR-044/045). Deferred presence/helpers, light, media and comparison tools stay
hidden. Existing runtime/analysis settings remain preserved; UI hiding is not a
claim that backend tasks stop. HA remains responsible for its existing controls.

On 4 October, authenticated Alpha.77 Ingress readback showed six saved zones:
Erdkellerbereich, Gangbereich, Wohnbereich, Eingangsbereich, Kochbereich and Badbereich.
The count was observed, not a fixed product limit. All six had checked light/shutdown
references; Bad/Gang/Koch/Wohn also had native Sonos Sound-Cloud references.
Only Eingangsbereich matched the HA structure fully. This is dated evidence,
not a fresh November inventory or acceptance of physical presence/light/audio.

Known October residuals:
- Kochbereich: 419 old members retained; eight links saved separately despite a
  replaced member identity. No silent rename or migration.
- Badbereich: 145 enabled members from 281 area candidates; the broad 858-member
  HA label was deliberately not fully imported.
- Erdkeller/Gang/Wohn: additional HA-label members remained visible as deviations.

Alpha.77 release: PR #161, commit `1946d5b8941689fce18574c05adf0f4e3b3adaf7`;
exact candidate/main CI `37173914432`/`37174021635`, scoped backup `51227e96`
and one update were verified then. The historical delivery receipt remains in
RELEASE_STATE.json, with a separate latest observation for today's stopped state.
Previous detailed handoff: `503793b994ee9c5c3b0238429139e5b6fa494d10:CURRENT_STATE.md`.

## Next step and boundaries

When a running, authorized PilotSuite session is available, freshly read the saved
Kochbereich identities and HA labels, prepare only evidence-backed structural
corrections, and verify their exact scope before applying. No household test switching
or active presence/light/Sonos takeover. Do not start the currently stopped app just
to satisfy a browser check. No Ingress/authentication/sandbox bypass.
