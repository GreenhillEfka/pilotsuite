# Current state — Alpha.76 installed; Alpha.77 structural adoption support in development

Alpha.76 is installed after PR #160, exact candidate/main CI
37171634810/37172229997, fresh PilotSuite-only backup `4c016987` of
Alpha.75, and one targeted update. The authenticated Ingress editor now offers
populated light and Sound-Cloud selectors. Four app options stayed unchanged.
Runtime is ready, stream-connected and fresh. A current Supervisor log after
the zone mapping corrections reports `zone_resolved=True`; the earlier false
state is retained below as historical evidence. The source is main
`2941659e577700562202c2dea5c4a121ddd6703b`, tree
`00bc9af0ebbd2889fb7a161ce0d00884e86488f7`, app tree
`483191fc4b8e699c6f307885fe906ee5c6f8b992`. This is a
repository/version/app-tree association, not installed-image attestation.

## Six HA reference zones — actual PilotSuite status, 04.10.2026

Home Assistant currently has six public `habitus_zone` anchors. The count is
observed, not a PilotSuite limit. In authenticated PilotSuite Ingress, the
following **structural, non-actuating** work has been saved and read back:

| Zone | Saved PilotSuite structure and reference links | Fresh HA structure check |
| --- | --- | --- |
| Erdkellerbereich | Two areas, 67 selected stable members, label and three light/shutdown links | Deviations: 60 extra HA-label members, chiefly disabled/technical |
| Gangbereich | Gang and Speisekammer, 234 selected stable members, label and eight light/Sonos links | Deviations: 60 extra HA-label members, chiefly disabled/technical |
| Wohnbereich | Stale `wohnimmer` area removed; Wohnzimmer, 263 selected members, label and eight light/Sonos links | Deviations: three extra disabled HA-label members |
| Eingangsbereich | Flur, Hintereingang, Vordereingang and Vorraum, 64 selected members, label and two light/shutdown links | **Structure matches HA** |
| Kochbereich | Existing 419-member structure retained; link save blocked by renamed member identity | Not accepted; do not bulk replace members |
| Badbereich | Existing areas Bad and Toilette retained; its HA label has 858 members | Not accepted; full-label import exceeds the 500-member limit |

New Alpha.77 work uses the same store and revision checks to save only validated
read-only HA links without touching conflicting members, and offers a labelled
area subset when a label is too large for full import. Both routes remain
local/synthetic until exact CI, scoped backup, deployment and real Ingress
readback. The four saved zones above are structural records, not proof of
physical light/Sonos operation, active PilotSuite control or household acceptance.
No household device was switched or played for this check. The existing HA
light and native Sonos Sound-Cloud controllers remain authoritative; no second
engine has been added. More zones must be discovered from current HA/PilotSuite
records, never from a hard-coded six-zone list.

## Historical Alpha.75/Alpha.76 preparation checkpoint

### At that checkpoint, Alpha.76 was a local candidate

Alpha.75's source passed all five jobs in PR #159 (candidate CI 37170519075)
and on merged main `5a1fdcf6a693c399e8424c15a540f804ceb43421`
(CI 37170647256). A native PilotSuite-only Alpha.74 backup `71ba105e` was
completed and scope-checked before one update. HA reports Alpha.75 installed
and started with the four prior options unchanged. Authenticated Ingress shows
the new read-only documentation. Runtime is ready, stream-connected and fresh,
but `zone_resolved=False`, also present before the update. This is not a claim
of six-zone structural or control acceptance.

The real Ingress editor exposed a mixed-asset failure: fresh Alpha.75 markup and
documentation but old cached `app.js` left the eight light/Sound-Cloud selectors
empty. Alpha.76 versions the workspace assets and requires script revalidation;
it does not change HA control or saved zone assignments. The new regression,
all 737 Python tests, 77 JavaScript tests, 68 API contracts and structural
synthetic browser pass locally. Candidate CI, a new scoped backup, installation
and real browser confirmation remain open. Do not save zone drafts until the
updated selectors are visible and stable.

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
