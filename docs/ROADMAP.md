# Roadmap — weniger Parallelität, vollständige Nutzerwege

Stand 28.09.2026. Kein Neustart und keine neue Versionsversprechung.
Release-Chronik: [CHANGELOG](../CHANGELOG.md). Tatsächliche Fähigkeiten:
[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). Installationsbelege:
[RELEASE_STATE.json](RELEASE_STATE.json).

## 1. Jetzt: Konzept und Alltagsansicht konsolidieren

PR #118 hat Zuständigkeiten, alte Read-only-/Versionsbehauptungen und doppelte
ADR-Nummern korrigiert. Alpha.55 setzt darauf die vereinfachte Navigation um.
Installation und Haushaltsabnahme bleiben getrennte Nachweise im Release-Receipt.

Mit Alpha.55 implementiert, getestet und installiert: **eine verständliche
Präsenzansicht je Zone** in den vorhandenen Workspace-Dateien. Die Haushaltsabnahme
bleibt offen. Die Zoneninstanz ist die primäre Live-Aussage;
Rollen-Zusammenfassung, Schattenvergleich und Replay sind keine Ersatzstatus.
Quellen, Nachlauf, Gültigkeit und Publikation werden im selben Nutzerweg erklärt.
Diagnose ist aufklappbar; keine zusätzliche „vereinfachte“ Paralleloberfläche.

Abnahme dieses Pakets:

- Von der Zonenliste zur aktuellen Präsenz, Begründung und verbleibenden Frist mit
  höchstens einem Öffnen; Quellen und Verlauf jeweils von dort erreichbar.
- Alle vier vorhandenen Zonen, IDs, Auswahlentscheidungen und Entwurfsdaten bleiben
  erhalten. Navigation, Speichern/Abbrechen und alte Deep Links funktionieren.
- Unverfügbare Werte, Kaltstart, optionale/erforderliche Quellen und nicht
  veröffentlichter Ausgang sind sichtbar unterscheidbar.
- Keine automatische HA-Konfigurationsprüfung und kein Write durch Navigation.
- Synthetische Desktop-/Mobil-/Tastaturtests einschließlich mindestens zweier
  passiver Refreshes erhalten Fokus, Scrollposition und ungespeicherte Eingaben.
- Reale angemeldete Ingress-Abnahme in Erdkellerbereich und einer andersartigen
  bestehenden Zone separat durchführen, sobald ein autorisierter Browser bereitsteht.
  Fehlender Browser blockiert nicht synthetische Entwicklung und wird nicht umgangen.

## 2. Danach: intern entkoppeln und doppelte Arbeit reduzieren

Nur nach einer gemessenen Ausgangsbasis für Tickdauer, SQLite-Schreibvorgänge,
Historienanfragen und Renderzyklen. Keine erfundenen Leistungsgewinne.

Zeit-/Frischeprüfung aus der Schattenabhängigkeit lösen; identische Checkpoints
nicht unnötig schreiben; benötigte Deadline- und Gültigkeitsaktualisierung erhalten.
Vorhandene Scheduler schrittweise vereinfachen, History-I/O getrennt halten.
Vergleichende Replay-/Restart-/Konflikt-/Ausfalltests müssen dasselbe fachliche
Ergebnis liefern. Bestehende API-Aufrufer und gespeicherte Konfigurationen erhalten.

Erster gemessener Schritt, Alpha.58 installiert: vorhandenen Bootstrap-Marker ohne
Schreibreservierung lesen, beim echten Erststart weiterhin unter Transaktion prüfen.
Je 60 synthetischen Tick-/Ansichtszyklen sinken IMMEDIATE-Transaktionen von 180 auf
60; alle 60 Checkpoints und 660 Verbindungen bleiben erhalten. Kein Zeitgewinn
belegt. Messbefehl: `PYTHONPATH=pilotsuite python scripts/benchmark_zone_presence.py`.
Checkpoint-Zeitstempel sind wegen Uhr-Rücksprungschutz nicht einfach entfernbar.
Schreibdeduplizierung und Scheduler-Vereinfachung sind weiterhin offen und benötigen
eigene Messungen und Regressionen; der kleine Lesepfad behebt keine dieser Aufgaben.

Alpha.59, implementiert/getestet/installiert, konsolidiert Zeitparser und Snapshot-Frischeprüfung in bestehenden
Besitzern. Rote Tests belegen falsche Bereitschaft und Legacy-Belege bei zukünftiger
Snapshot-Zeit sowie Fehler bei ungültigen Zeitangaben. Gültige Zeitgrenzen und die
gemessene Datenbankarbeit bleiben gleich; keine Scheduler- oder Datenmigration.

Legacy-Lernfelder und Shadow-Einstellungen nur mit expliziter Abbildung überführen:
Relevanz autorisiert Analyse bereits heute. Eine Migration darf weder alte Belege
löschen noch Quellen erweitern, Fristen erneuern oder Publikation einschalten.
Alte Felder erst nach getesteter Abwärtskompatibilität entfernen.

## 3. Präsenz im Haushalt beweisen

Synthetisch geprüft ist nicht im Haushalt abgenommen. Lesende Beobachtung muss
vorab vereinbarte Fälle abdecken: Betreten, ruhiger Aufenthalt, TV-Nutzung, Verlassen
und tatsächlich auftretende Datenlücken. Keine Geräte oder Sensoren für Tests schalten.
Nicht beobachtete Fälle bleiben offen; Restart-/Fault-Injection bleibt zunächst im
wegwerfbaren Testsystem. Jede beobachtete Entscheidung braucht Quelle, Grund und
Frist; falsche Freimeldungen haben Vorrang vor Komfortoptimierung.

Eigener öffentlicher Sensor: nur nach konkreter Paketprüfung und ausdrücklicher
Publikationsfreigabe. Vorhandener kanonischer Sensor ist eine Bestandsfrage, kein
Auftrag zum Überschreiben. Allgemeine Automationsübernahme und technische
Entity-ID-Migration bleiben gesondert offen.

## 4. Erst bei Nutzen: Licht, Medien und Lernen

Lichtvorschau und Bestandsprüfung existieren; nicht noch einmal bauen.
Ein späterer Pilot verwendet vorhandene passende HA-Logik oder genau einen
freigegebenen Ausführungspfad. Manuelle Bedienung hat Vorrang, Ziele/Parameter
bleiben begrenzt. Musik/TV-Arbitration erfordert belegte Session-/Gruppenhoheit.

Lernvorschläge zunächst mit festen Regeln auf späteren Zeitabschnitten vergleichen.
Fehlende Gegenreaktion ist kein positives Feedback. Keine selbstverstärkenden
Eigenaktionen, unkalibrierten Gewichte oder automatischen Grenzverschiebungen.
LLM, Sprache, HomeKit, RAG und zusätzliche Integration bleiben Optionen statt
Voraussetzungen; neue Komponenten brauchen einen konkret nicht anders erfüllbaren Nutzen.

## Lieferregel

Ein aktives Umsetzungspaket mit sichtbarem Ergebnis. Korrektheit, Datenschutz und
Wiederherstellbarkeit sind harte Grenzen; Bedienaufwand und Laufzeitkosten werden
innerhalb dieser Grenzen optimiert. Jeder Code-Release folgt dem
[Release-Runbook](RELEASE_RUNBOOK.md), einschließlich PilotSuite-only-Sicherung.
Implementiert, getestet, installiert und im Haushalt abgenommen separat ausweisen.
