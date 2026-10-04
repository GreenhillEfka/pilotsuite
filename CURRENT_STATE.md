# Current state — Alpha.74 installed

## Alpha.75 local candidate — not yet published or installed

The current working branch adds registry-identity-backed references for the
existing HA light group, light opt-in, shutdown action and, where confirmed,
native Sonos Sound-Cloud player, presence opt-in, user-facing `switch`, favorite
selector and daytime-volume opt-in. PilotSuite shows them in setup and zone
documentation with fresh identity readback. It neither issues HA control calls
nor claims accepted presence, light or media behavior. The actual six-zone HA
mapping is recorded in [docs/HA_ZONE_REFERENCES.md](docs/HA_ZONE_REFERENCES.md).
When importing an existing HA-tagged zone, the editor can explicitly replace
untouched type-based role suggestions with observed HA roles. Saved and manually
edited choices remain untouched.

Local evidence so far: 68 API contracts, 737 Python tests, 77 JavaScript tests,
and the structural synthetic browser passed. The latter produced responsive
screenshots inspected in dark and light themes. A candidate CI, container build,
disposable HA protocol, scoped backup, installation and real six-zone readback
remain pending. The installed app still reports Alpha.74. No household mutation
was performed by this development work.

## New HA structure evidence, 04.10.2026 — not a PilotSuite adoption receipt

A fresh, read-only Home Assistant label and structure-register check found six
public Habitus zone anchors: Erdkellerbereich, Badbereich, Gangbereich,
Kochbereich, Wohnbereich and Eingangsbereich. `habitus_zone` belonged to exactly
those six occupancy entities and no devices. This is a snapshot of **HA**, not a
new fixed product limit: future zones must be enumerated from current registries
and saved PilotSuite structure instead of hard-coding this count.

HA currently owns one light group per zone and its existing light automation
opt-ins. Badbereich, Gangbereich, Kochbereich and Wohnbereich also have separate
presence opt-ins to the existing Sonos Sound-Cloud; no Sound-Cloud player was
confirmed for Erdkellerbereich or Eingangsbereich. This only establishes the
current HA wiring and enabled configuration, not a physical switching/listening
test, a cross-zone Light-Cloud, or PilotSuite ownership of either function.

| HA zone | Existing light group | Presence-bound Sound-Cloud option |
| --- | --- | --- |
| Erdkellerbereich | `light.beleuchtung_erdkeller` | No confirmed zone player |
| Badbereich | `light.bad_beleuchtung_badbereich` | `input_boolean.badbereich_sound_cloud_bei_prasenz` |
| Gangbereich | `light.beleuchtung_gangbereich` | `input_boolean.gangbereich_sound_cloud_bei_prasenz` |
| Kochbereich | `light.kuche_beleuchtung_kuche` | `input_boolean.kochbereich_sound_cloud_bei_prasenz` |
| Wohnbereich | `light.wohnzimmer_beleuchtung_wohnzimmer` | `input_boolean.wohnbereich_sound_cloud_bei_prasenz` |
| Eingangsbereich | `light.beleuchtung_eingangsbereich` | No confirmed zone player |

These IDs are an observed snapshot, not a fixed schema for future zones. New HA
zones need one public occupancy anchor, a deliberate zonal light relationship and
an independently confirmed player before an optional Sound-Cloud relationship.
An authenticated Ingress UI check on 04 October confirmed that the installed
PilotSuite currently lists four saved zones: Erdkellerbereich, Kochbereich,
Wohnbereich and Badbereich. Gangbereich and Eingangsbereich are present in HA
but absent from this PilotSuite list. This is a real count, not a product limit.
The Kochbereich card reports 419 saved members and a connected label; the other
three report open membership. Wohnbereich lists both `wohnimmer` and Wohnzimmer
as areas, so that saved mapping needs a targeted identity check. Reading the
Gangbereich HA label in a discarded editor draft proposed 294 members, including
configuration entities and automations. No zone, label, member or HA metadata was
saved or changed by this inspection. Do not bulk-accept that proposal without a
curated review. Structural synchronization and household acceptance remain open.

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

At the 30 September release check, the available browser showed HA authentication
URLs and an authenticated PilotSuite session was unavailable. The prior direct proxy
returned Ingress-required 403; that route stays stopped. An HA login alone is not a
fresh PilotSuite session or a saved-zone readback. No auth workaround or guessed zone mapping.
The 30 September read-only HA inspection confirmed the Erdkellerbereich dashboard
and inherited device/entity labels; it did not reveal PilotSuite's then-documented
four saved zones. The authenticated 04 October read described above establishes
the current PilotSuite list but does not establish matching areas, members or roles.
Real structural synchronization is not claimed by installed code or synthetic tests.

Next: compare the four saved zones' actual areas/tags, stable members and roles
against the current HA index, including the unexpected `wohnimmer` area and the
broad Kochbereich membership. Then plan Gangbereich and Eingangsbereich using
confirmed physical areas and curated members, rather than all label matches.
Reconcile
only confirmed structural differences, retaining physical areas, foreign labels and
runtime choices. Independently reread and document before claiming acceptance.
Presence/helpers, active lighting, climate/media and learning remain later phases.

Full source/backup/runtime evidence: docs/RELEASE_STATE.json. Earlier receipts and
implementation history remain in Git and docs/IMPLEMENTATION_STATUS.md. Private
household inputs stay in ignored pilot_data/reviews. Heartbeat remains PAUSED;
no new agents/tasks/timed run. Preserve untracked AGENTS.md.
