# PilotSuite configuration

## Options

| Option | Default | Meaning |
|---|---:|---|
| `log_level` | `info` | Runtime log level; secrets are redacted regardless |
| `golden_zone_area_ids` | `[erdkeller]` | Exact Home Assistant area IDs included in the first proving scope |
| `refresh_interval_seconds` | `30` | Full snapshot reconciliation interval |
| `audit_retention` | `5000` | Maximum retained PilotSuite audit events |

This release is always read-only. There is intentionally no option that can enable Home Assistant mutations.

## First start

After starting, open the Web UI and confirm:

- Home Assistant connector: connected
- World snapshot: areas, entities, and states present
- Golden Zone: resolves the Erdkeller area ID
- Policy mode: hard read-only
- Release: `0.1.0-alpha.23`

## Habitus zones and entity selection

Each Habitus zone has a visible tab. Select a tab to see only that zone's entity
choices, evaluation, suggestions and observations. Use **Name / Bereiche bearbeiten**
to rename it or tick HA-area sources (e.g. Bad and Toilette).

For a new zone: **+ Neue Zone** → name and area checkboxes → **Zone speichern** →
select relevant entities → **Auswahl speichern** → **Auswertung starten**.
The same button pauses an active zone without losing its choices. Save or discard
pending entity edits before switching tabs or starting/pausing. Only confirmed relevant entities are evaluated. There is no automatic selection bypass. An active zone with
no suitable selected observations is explicitly shown as having no observations.
Neutral zones report observation/data quality; they do not claim learned habits.

Existing `golden_zone_area_ids` are imported once into persistent zones. After that,
use the zone editor for source changes; changing bootstrap options does not replace
stored definitions. Missing sources and temporarily absent entities preserve saved
choices. Export provides a reviewable JSON copy; import is not implemented.

Before updating, create a PilotSuite-only backup. SQLite schema migrations back up
older databases automatically. For downgrade recovery restore the previous App and
its data from the pre-update backup; do not open a newer schema with older code.


## Roles and opt-in activity learning (alpha.7)

Open a zone tab. Candidate/relevant/unreviewed/ignored/evaluated counts are separate.
Entity choices and raw neurons are collapsible. Under **Rollen / Lernfreigabe
bearbeiten**, check one or more confirmed sensors per role (maximum 20): temperature,
humidity, presence/motion or reference temperature. Role membership is not HA topology.
Climate groups show a median with min/max; references never enter the primary median.
Missing sources stay visible. Without an explicit group, multiple climate sources are
ambiguous. A multi-room group is a zone summary, not an individual room temperature.

Learning defaults off. Select a presence group and explicitly grant consent to record
fresh off-to-on events. At most one event per zone per five minutes is counted, so
several sensors seeing the same activity do not inflate the count. Evidence expires
after 14 days; the database holds at most 5,000 events across all zones. Candidates
require five events on three UTC dates in one two-hour UTC bucket. These are activity
patterns to review, not occupancy probability, person identification or automation.

Feedback **Passt / Nicht hilfreich / Später prüfen** persists independently of counts.
Revoke by unchecking consent and saving; existing evidence expires. **Lerndaten
löschen** removes evidence and pattern feedback and revokes consent while preserving
entity choices. Changing the presence group also clears its old evidence/feedback.
Export provides a per-zone JSON report including evidence. Backups remain separate.
No learning history is reconstructed from HA snapshots or after disconnects.

## Prüfnotizen (alpha.22)

Im Routineentwurf **Bestehende Automationen prüfen**, einen Treffer im Detail prüfen
und **Bewertung festhalten** wählen. Bewertungen und Notizen werden zum konkreten
Entwurfs-/Quellen-/Automationsstand gespeichert. Bei Änderungen bleiben sie erhalten,
werden aber als veraltet angezeigt; nach dem Neuladen ist der Automationsstand
zunächst nicht erneut geprüft. Beim Speichern erfolgt eine neue lesende Prüfung.

Der Editor behält deinen Text bei Konflikten und beim Neuladen des Prüfstands.
Eine Bewertung ist keine Ausführungsfreigabe; HA-Automationen bleiben unverändert.
Notizen bleiben beim Lernreset erhalten und lassen sich gezielt löschen/exportieren.
Schema 8 ergänzt die bestehende Datenbank nach einer automatischen SQLite-Sicherung.
Das ersetzt nicht die vollständige PilotSuite-App-/Datensicherung vor dem Update.

## Prüfkompass (alpha.23)

Unter **Routinen-Entwürfe** zeigt jeder vorhandene Entwurf einen nächsten Schritt
und **Fünf Prüfbereiche und ihre Belege**. Dort stehen Quellen, Beobachtungsgrundlage,
dein gewünschtes Ergebnis, vorhandene Automationen und eigene Bewertungen getrennt.
Mit **Nächster Arbeitsschritt** filterst du die Entwürfe; **Sortierung** ändert nur
die Ansicht. Filter, Neuladen und Aufklappen speichern nichts und starten keinen
Automationsvergleich. Eine fehlende Grundlage ist keine Freigabe oder Entwarnung.

Die Schaltfläche führt zur passenden bestehenden Funktion. Automationsbezüge und
Details werden erst durch deinen ausdrücklichen Prüfaufruf gelesen. Ein Lesestand
wird für die Navigation höchstens fünf Minuten verwendet; danach ist eine neue
Prüfung nötig. Ändert sich die Grundlage, bleibt dein Text erhalten. Die Rangfolge
ist eine Arbeitshilfe, keine Risiko- oder Sicherheitsbewertung. Apply bleibt gesperrt.
