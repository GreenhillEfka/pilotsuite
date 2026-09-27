# Architektur — vorhandenen Kern vereinfachen

Überprüfung vom 28.09.2026 auf Alpha.54 / Architekturkennung v23.
Diese Konsolidierung ändert weder App-Code noch Speicherformat. Ziel und Ist sind
getrennt; [ADR-042](../DECISIONS.md#adr-042--consolidate-the-product-around-the-existing-zone-instance)
begründet die Richtung.

## Datenweg und vorhandene Besitzer

`HA → WorldModel → relevante Zonenquellen → Präsenzkern → Erklärung / erlaubte Ausgabe`

Historie liefert begrenzte Analyse, niemals nachträgliche Live-Trigger.

| Verantwortung | Vorhandener Besitzer | Grenze |
|---|---|---|
| HA-Transport / aktuelle Projektion | `ha/client.py`, `ha/world.py` | Keine zweite Geräte- oder Recorder-Datenbank |
| Zone, Auswahl, gemeinsame Revision | `SelectionStore`, `ZoneStore` | Stabile IDs; Area und logische Zone unterscheiden |
| Rollen, Belege, Präsenzkonfiguration und Checkpoints | `ContextStore` mit vorhandenen Mixins | Eine SQLite-Datei, keine neue Konfigurationsquelle |
| Typisierte Präsenz / Zustandsübergang | `core/zone_presence.py` → `core/presence_kernel.py` | Kein HA-I/O im reinen Kern |
| Ablauf, Historienabfrage, Ausgang | `zone_presence_service.py` | Revision und Identität vor/nach I/O prüfen |
| Entwürfe, Notizen, Änderungsbelege | `PlanStore` und bestehende Organisationspläne | Allgemeines Apply bleibt geschlossen |
| Darstellung | `web/` und vorhandene APIs | Keine Entscheidung oder Berechtigung im Browser |

Pfade beziehen sich auf `pilotsuite/pilotsuite/`. Die gemeinsame Datenbank heißt
`selections.sqlite3`; es existieren außerdem begrenzte Audit-/Legacy-JSONL-Dateien.
„Ein Besitzer“ bedeutet klare fachliche Zuständigkeit, nicht eine riesige Klasse.
Insbesondere nutzt PlanStore für aktuelle Routinen und Notizen bereits SQLite;
die frühere Aussage „Pläne bleiben JSONL“ war zu pauschal.

Die vorhandenen `domain/neurons.py`, `moods.py` und `synapses.py` bleiben erhalten:
Sie normalisieren Beobachtungen, berechnen feste Kontext-/Klimabewertungen und
erzeugen Regelvorschläge. Die Metaphern belegen kein neuronales Lernen. Im Produkt
sind „Messwert“, „Bewertung“ und „Vorschlag“ verständlicher; eine spätere gewünschte
Lichtstimmung ist davon getrennt und keine erkannte menschliche Emotion. Diese
Begriffsklärung benennt weder API-Typen noch Haushaltsentitäten automatisch um.

## Tatsächliche Komplexität, nicht nur Dateianzahl

Der gemeinsame Kernel wird heute von mehreren Pfaden verwendet:
Zoneninstanz, ausdrücklich gestarteter Alpha.48-Schattenvergleich und älterer,
öffentlich gesperrter Presence-Runtime. Gleicher Algorithmus bedeutet noch nicht
gleiche Konfiguration oder denselben Checkpoint. Die UI zeigt zusätzlich eine
Rollen-Zusammenfassung und synthetische Replays. Diese Ergebnisse dürfen nicht als
mehrere gleichwertige aktuelle Anwesenheitszustände erscheinen.

Ziel: Die bestehende Zoneninstanz liefert den Alltagsstatus; Schattenvergleich und
Replay sind ausdrücklich benannte Diagnoseansichten. Legacy-Konfigurationen bleiben
lesbar, bis eine getestete Überführung Quellen, Fristen und Bedeutungsunterschiede
erhält. Keine automatische Zusammenführung allein nach Feld- oder Anzeigenamen.

`service.py` startet heute getrennte Refresh-, Shadow-, Presence- und History-Tasks.
`zone_presence.py` importiert einen Zeitparser aus dem Schattenmodul, und der
Zonenservice verwendet dessen Frischeprüfung. Das sind konkrete Kopplungen für einen
späteren kleinen Refactor, kein Grund für eine neue Service-Architektur.

## Umsetzungsentscheidung und Alternativen

| Option | Bewertung |
|---|---|
| Bestehende App konsolidieren | Gewählt: vorhandene Kernel-, Speicher-, HTTP- und Browserprüfungen weiterverwenden |
| Alles in neue HA-Automationen exportieren | Jetzt ungeeignet: Bestandsübernahme und vollständige Verbrauchermigration fehlen |
| Zusätzliche native HA-Integration | Später nur bei messbarem Nutzen; aktuell zweite Installation und zusätzliche Kompatibilitätslast |
| Framework-/Microservice-Neubau | Kein nachgewiesener Nutzen für diese Aufgaben; zusätzliche Betriebs- und Datenübergänge |

Das bestehende Ausgangspaket hat fünf Helfer: interner Zustand, Gültigkeit,
Gültigkeitsfrist, Timer und öffentlicher occupancy-Sensor. Sie dienen unterschiedlichen
Fehlerfällen. Sie allein zur Reduktion der Entitätszahl zu entfernen wäre keine
nachgewiesene Vereinfachung. Ein späterer dünner Adapter müsste dieselben
Ausfall-/Wiederanlaufgarantien und eine getestete Migration bieten.

## Kleine technische Schritte, keine neue Schicht

- Eine primäre Statusprojektion in der UI; vorhandene API-Verträge zunächst erhalten.
- Gemeinsame Zeit-/Frischefunktionen erst mit vergleichenden Tests aus der
  Shadow-Abhängigkeit lösen. Kein zusätzliches Repository oder Datenmodell.
- Unveränderte Checkpoints und identische Ansichten möglichst nicht neu schreiben
  beziehungsweise rendern. Zuerst Schreib-/Renderhäufigkeit messen; notwendige
  Gültigkeitsaktualisierung nicht wegoptimieren.
- Zustandsereignisse und Deadline-Prüfung koordinieren, ohne Historien-I/O unter
  den Projektionslock zu ziehen oder einen Broker einzuführen.
- Legacy-Pfade erst nach Aufruferinventar, Migrations-/Rollbacktests und eigener
  Freigabe entfernen. Das gilt auch für gespeicherte Lernschalter.

## Quellenkritik und wiederverwendete Erkenntnisse

Erneut gelesen wurden die
[alte HA-Konzept-Richtlinie](https://github.com/GreenhillEfka/pilotsuite-styx-ha/blob/4f78be5/docs/HA_CONCEPT_DIRECTIVE.md),
[Konzeptprüfung vom April](https://github.com/GreenhillEfka/pilotsuite-styx-ha/blob/4f78be5/team/shared/handoffs/2026-04-22_PILOTSUITE_STATE_OF_THE_ART_AND_CONCEPT_REVIEW.md),
[Core-Präsenzabschluss](https://github.com/GreenhillEfka/pilotsuite-styx-core/blob/d4e3a7b7/docs/analysis/PS_CORE_SLICE_307_CORE_HABITUS_202_CLOSEOUT_2026-04-21.md)
und [Core-Architekturabschluss](https://github.com/GreenhillEfka/pilotsuite-styx-core/blob/d4e3a7b7/docs/analysis/PS_CORE_P3_011M_HEXAGONAL_ARCHITECTURE_CLOSEOUT_2026-04-19.md).

Behalten: eindeutige Besitzer, deterministische Abläufe, bestätigte Wiederanlaufbelege
und ein vollständiger Nutzerweg. Nicht übernehmen: zwei koordinierte Produkt-Repos,
HA-eigener zweiter PilotSuite-Zonenspeicher, alte Arbeitswarteschlangen oder
„abgeschlossen“ allein wegen grüner Endpointtests. ADR-009 hat die frühere
HA-Zonenhoheit ausdrücklich durch den bestehenden App-Speicher ersetzt.
PRs #103, #105, #107 und #116 erklären den heutigen Vergleichs-, Zonen-, Recovery-
und Unknown-Pfad; deren Funktionen werden nicht neu implementiert.

HA bestätigt die Notwendigkeit expliziter Deadline-/Gültigkeitssemantik:
[Timer](https://www.home-assistant.io/integrations/timer/) unterscheidet Ablauf und
Abbruch; verpasste Ablaufereignisse werden beim Start nicht nachgeliefert.
[Template-Verfügbarkeit](https://www.home-assistant.io/integrations/template/)
erlaubt eine unbekannte Ausgabe statt eines falschen Boolean-Werts.
Das begründet Schutzmaßnahmen, beweist aber keine PilotSuite-Haushaltsabnahme.
