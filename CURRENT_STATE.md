# Current state — Alpha.74 installed

## Device-based display defaults delivered, 30.09.2026

Newly imported, untagged zone members now get an explained, editable default under
“Darstellung im Habitus-Dashboard”. Each device function is classified individually:
HA registry category first, then device class and entity type. Controls → Bedienung,
ambient values → Übersicht, other measurements/states → Status, settings →
Konfiguration, battery/connectivity/maintenance → Diagnose. Existing entity/device
tags and every saved/manual choice (including empty roles) take precedence.
The collapsed section shows the selected roles. Untagged saved entries offer
explicit reuse of the type default. Unknown/disabled identities stay undecided;
no automatic Habitus Zone anchor, analysis consent or control grant.

PR #157: exact candidate `998f00b6972d01cb0f8e6f6566587259376fc890`, release main
`43b4a8e2bd798a7b03a628a3f0c80b9f142a801d`; all five CI jobs passed for each
(36765700922 / 36766189903). App tree `78572a69c0849179f50c4c4212f3dc15dfdd2ad8`.
Local: 735 Python, 77 JS, 68 API contracts and extended structural browser passed.
CI also passed all five browser suites, amd64 build, reproducible source checkout
and seven native scenarios against disposable HA 2026.9.3. Missing preselection
was reproduced before the fix. Desktop/mobile screenshots were actually inspected;
manual empty choices, reimport/reopen and no-write suggestion are covered.

Fresh native backup `bc61e76f`, 19:25:07 UTC: only previous Alpha.73 app/data,
54,609,920 bytes local, unprotected, no HA/database/folders or failed components.
Two additional Synology agents still report only “Failed to list backups”. The
user's standing “ja immer” exception applies; all local checks remain required.
No NAS settings change, archive extraction, restore drill or off-device claim.

One Store refresh and one targeted update installed Alpha.74. Native metadata at
19:33:27 UTC confirms started, all four options unchanged. Startup/readiness shows
presence_adoption_review unchanged, ready, connected, fresh and zone-resolved.
No separate restart, rebuild, other-app update or household metadata/control call.
Source association is repository/version/app-tree, not independent image attestation.
Reload an already-open PilotSuite page to load the new frontend.

## Structural adoption remains the next household task

The product remains limited to zone overview, structure editor and documentation.
Existing stores/runtime/analysis decisions are preserved. Hiding deferred modules
does not stop existing backend behavior. The user's target remains actual matching
HA/PilotSuite areas, stable members and Habitus role tags, reconciled through the
existing concrete metadata preview/apply/readback path.

The available browser still shows HA authentication URLs. Login/opening PilotSuite
was requested and remains pending. The prior direct proxy returned Ingress-required
403; that route stays stopped. No auth workaround or guessed zone mapping.
Read-only HA inspection confirms the Erdkellerbereich dashboard and its inherited
device/entity labels; this does not reveal the actual four saved PilotSuite zones.
Real structural synchronization is not claimed by installed code or synthetic tests.

Next: once authenticated, inspect all four saved zones, starting with Erdkellerbereich
and one unlike zone; compare actual areas/tags, stable members and roles. Reconcile
only confirmed structural differences, retaining physical areas, foreign labels and
runtime choices. Independently reread and document before claiming acceptance.
Presence/helpers, active lighting, climate/media and learning remain later phases.

Full source/backup/runtime evidence: docs/RELEASE_STATE.json. Earlier receipts and
implementation history remain in Git and docs/IMPLEMENTATION_STATUS.md. Private
household inputs stay in ignored pilot_data/reviews. Heartbeat remains PAUSED;
no new agents/tasks/timed run. Preserve untracked AGENTS.md.
