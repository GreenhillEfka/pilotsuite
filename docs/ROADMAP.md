# Roadmap — weniger Parallelität, vollständige Nutzerwege

Stand 28.09.2026. Kein Neustart und keine neue Versionsversprechung.
Release-Chronik: [CHANGELOG](../CHANGELOG.md). Tatsächliche Fähigkeiten:
[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). Installationsbelege:
[RELEASE_STATE.json](RELEASE_STATE.json).

## 1. Jetzt: Konzept und Alltagsansicht konsolidieren

Die vorliegende Dokumentationsänderung korrigiert Zuständigkeiten, alte
Read-only-/Versionsbehauptungen und doppelte ADR-Nummern. Sie verändert die
installierte App nicht.

Nächstes Implementierungspaket: **eine verständliche Präsenzansicht je Zone** in
den vorhandenen Workspace-Dateien. Die Zoneninstanz ist die primäre Live-Aussage;
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
