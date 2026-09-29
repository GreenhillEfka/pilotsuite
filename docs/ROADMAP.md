# Roadmap — weniger Parallelität, vollständige Nutzerwege

Stand 29.09.2026. Kein Neustart und keine neue Versionsversprechung.
Release-Chronik: [CHANGELOG](../CHANGELOG.md). Tatsächliche Fähigkeiten:
[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). Installationsbelege:
[RELEASE_STATE.json](RELEASE_STATE.json).

## 1. Jetzt: Konzept und Alltagsansicht konsolidieren

### Habituszonen vollständig einrichten

Nachtlauf und zusätzliche Stunde sind abgeschlossen; der Heartbeat bleibt pausiert.
Der Nutzer hat anschließend ausdrücklich die direkte Fortsetzung von PR #151
beauftragt. Kein neuer Zeitlauf und keine automatische Wiederaufnahme alter Fenster.
Ein aktiver Branch/PR; keine neue Intelligenz, Engine oder Konfigurationsquelle.
ADR-043 und UX_WORKSPACE.md präzisieren die Richtung anhand von Habituszonen und
Primärquellen. Die Reihenfolge ist ein Arbeitsplan, keine Fertigstellungszusage:

1. **Zonenstruktur und Automationen:** eigener Zonenbereich, ausdrücklich zugeordnete
   Themen Anwesenheit/Licht/Weitere, vorhandener Organization-Speicher und Inspector.
   Zuordnung, aktuelle Aktivierung und fachliche Prüfung getrennt darstellen.
2. **Einrichtung und Helfer:** vorhandene Kette zusammenhängend zeigen; Helfer
   wiederverwenden und fehlende gezielt planen. Vorhandene Funktionen nicht duplizieren.
   Tatsächliche HA-Nachlaufparameter von PilotSuite-Vergleichseinstellungen trennen.
3. **Alltagsklarheit und Abnahme:** vorhandener öffentlicher Sensor als ausdrücklich
   gekennzeichneter Bestandsstatus; Vergleich, Lernrelikte und Diagnose nachgeordnet.
   Tastatur, Mobilansicht, Entwurfserhalt, widersprüchliche/unbekannte Daten prüfen.
4. **Auslieferung:** eigener Diff-Review, vollständige lokale und exakte Remote-Gates,
   frische PilotSuite-only-Sicherung, sicheres Test-Release; offene Punkte ehrlich.

Primärquellen-Recherche wird in konkrete Entscheidungen und Regressionen übersetzt,
nicht als isolierter Bericht betrieben. Haushaltsänderungen bleiben bis zur Klärung
des Live-Schreibumfangs aus; Browser-Abnahme ohne autorisierten Zugang offen.

Abschlussstand: Alpha.69 nach PR #148 installiert, Themenbereich ausgeliefert.
Alpha.70 nach PR #149 installiert und verbindet die Status-/Helfereinstiege; ungültige
Berechnungen bleiben unklar. Alpha.71 nach PR #151 installiert: einzelne fehlende
Booleans/Timer im bestehenden Paket-/Identitäts-/Planweg, ohne automatischen Anschluss.
Regressionen für stale Revision, deaktivierte Identität, verlorene Antwort und
Wiederanlauf sowie synthetischer Bedienweg sind grün. Alle fünf exakten Kandidaten-/
Main-CI-Jobs einschließlich echter isolierter HA-Prüfung bestanden; Sicherung,
Installation und unveränderte Optionen sind im Release-Receipt belegt.
Offen bleiben tatsächlich HA-eigene Parameter und Automationsanschluss/-übernahme.
Keinen Legacy-Executor öffnen. Nächster Schritt ist die angemeldete lesende
Erdkeller-Abnahme der vollständigen Bestandskette, nicht eine neue Intelligenzschicht.

### Vorheriger Stand

Der UI-Stundenlauf am 28.09., 19:33:18–20:33:18 UTC endete mit Draft PR #146.
Nach ausdrücklicher Zustimmung zum anschließenden Abschluss ist Alpha.68 installiert:
vier Aufgaben-Einstiege, sichtbarer Feldfokus und korrigierter Hauptsensor-Link,
keine zusätzliche Oberfläche oder Konfiguration. Rot/grün-Regressionsnachweis,
alle fünf exakten Kandidaten-/Main-CI-Jobs und frische PilotSuite-only-Sicherung
sind im historischen Release-Receipt belegt. Damals blieb der Heartbeat pausiert;
der später ausdrücklich beauftragte Nachtlauf oben ist eine neue Freigabe.
Angemeldete Ingress-/Vier-Zonen-Abnahme bleibt offen. Lesende Erdkeller-Zustände
und drei Stunden Historie zeigen keinen Übergang und beweisen daher weder Nachlauf
noch sicheres Übernahmeverhalten; keine Testschaltung oder Haushaltsänderung.

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

Manueller Folgeauftrag nach dem abgeschlossenen Dreistundenlauf: zuerst bestehende
Anwesenheitssteuerung durchgängig verbinden und vergleichen. Alpha.61 nutzt
den vorhandenen Organization-Editor/-Speicher für Boolean, Timer, öffentlichen
Präsenzsensor und Automationen. HA bleibt zuständig; kein Takeover, keine Aktivierung.
Implementiert, getestet und nach PR #132 sowie exakter Kandidaten-/Main-CI installiert.
Haushaltszuordnung und echte Ingress-Abnahme bleiben offen; keine Bestandsautomation
wurde geändert. Belege im Release-Receipt. Dieser frühere Lauf ist abgeschlossen;
das neue Zweistundenfenster ist unten getrennt definiert.

Alpha.62 behebt den am 28.09.2026 rot reproduzierten Bedienfehler: Nach
blockiertem Bereichswechsel und anschließendem Speichern/Verwerfen verschwindet
genau der veraltete Navigationshinweis. Offene Anfragen, andere Entwürfe und Fehler
bleiben geschützt. Nach PR #134 und exakter Kandidaten-/Main-CI installiert;
Haushaltsabnahme offen. Keine neue UI-Schicht, kein Poller, keine automatische
Navigation. Nächster fachlicher Schritt bleibt die
lesende Haushaltsabnahme; Laufzeitkonsolidierung separat mit Ausgangsmessung.

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
Der Bootstrap-Lesepfad allein behebt weder Checkpoint-Sperren noch Scheduler-Dopplung.

Alpha.64 ergänzt einen gemessenen, engen Checkpoint-Lesepfad: exakt identischer
Inhalt und passende Zone/Revision benötigen keine Schreibreservierung. Bei Änderungen
werden Revision und Wert nach Sperrerwerb erneut geprüft. Kein Prozess-Cache, keine
entfernten Zeitstempel oder verzögerten Pflichtschreibvorgänge. Lieferung und
Haushaltsabnahme separat im Release-Receipt.

Vergleich desselben erweiterten Messskripts vor/nach dem Fix, je 60 Ein-Zonen-Zyklen:

| Szenario | IMMEDIATE vorher → nachher | Checkpoint-Writes | SELECT vorher → nachher |
|---|---:|---:|---:|
| Belegt | 60 → 60 | 60 → 60 | 1140 → 1200 |
| Frei | 60 → 60 | 60 → 60 | 1140 → 1200 |
| Unklar | 60 → 60 | 60 → 60 | 1140 → 1200 |
| Quellenbasis dauerhaft ausgesetzt | 60 → 0 | 0 → 0 | 1140 → 900 |

Alle vier Entscheidungsverlauf-Hashes stimmen überein; je Szenario weiterhin 660
Verbindungen, keine Historien-/HA-Ausgabeaufrufe. Instrumentierte Medianzeiten liegen
vorher bei 2,269–2,542 ms und nachher bei 2,281–2,611 ms: kein belegter Zeitgewinn.
Die zusätzliche Abfrage im normalen Schreibfall ist ein ausdrücklicher Tradeoff
für den sperrfreien identischen Fall. Keine Aussage über Haushaltslast oder
Renderzyklen; Frontend, Historienplaner und Scheduler bleiben unverändert.
Weitergehende Schreibbündelung und Scheduler-Vereinfachung bleiben offen und
benötigen eigene Messungen und Regressionen.

Alpha.59, implementiert/getestet/installiert, konsolidiert Zeitparser und Snapshot-Frischeprüfung in bestehenden
Besitzern. Rote Tests belegen falsche Bereitschaft und Legacy-Belege bei zukünftiger
Snapshot-Zeit sowie Fehler bei ungültigen Zeitangaben. Gültige Zeitgrenzen und die
gemessene Datenbankarbeit bleiben gleich; keine Scheduler- oder Datenmigration.

Alpha.60, implementiert/getestet/installiert, erhält den datierten Rücklesenachweis
über unveränderte Ticks innerhalb der bestehenden 20-Sekunden-Drosselung. GET erneuert
ihn nicht; geänderte oder ungültige Grundlagen entziehen die Bestätigung. Drei solche
Ticks benötigen keine zusätzlichen HA-Aufrufe. Keine neue Lease oder Leistungszusage.

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

Abgeschlossener Zweistundenlauf am 28.09.2026, vorgesehen 17:05:52–19:05:52 UTC:
Verwaltung, Konfiguration und Licht im bestehenden System verbessern. Nach der
Veröffentlichungsgrenze 18:45:52 UTC blieb PR #144 zunächst Entwurf; der Heartbeat
wurde pausiert. Der anschließende ausdrückliche Auftrag autorisiert dessen Abschluss
als Alpha.67 nach Runbook, keine Verlängerung des Zeitlaufs oder neue Funktionspakete.
Alpha.65 korrigiert die reine Lichtvorschau: Unterbrechungen beenden
eine Stabilitätsbeobachtung, ohne den Mindestabstand zu löschen. Lokale Regressionen
und Browserablauf bestehen; PR #140 und alle exakten Kandidaten-/Main-CI-Jobs bestanden,
installiert nach geprüfter PilotSuite-only-Sicherung. Haushaltsabnahme bleibt offen.
Alpha.67 ist nach PR #144, exakter Kandidaten-/Main-CI und geprüfter Sicherung
installiert. Es korrigiert ungültige Binärbeobachtungen und vereinheitlicht die
Quellen-Gültigkeitsprüfung im bestehenden Lichtweg. Fehlende/abgeleitete gegenüber
bewusst leeren Rollen bleiben ein gesonderter nächster Prüfpunkt, keine neue Steuerung.

Neu priorisierte Nutzerkorrektur: bestehende Automationen dürfen übernommen werden.
Alpha.66 implementiert, getestet und nach PR #142/exakter Kandidaten-/Main-CI
installiert: Die vorhandene revisionsgebundene Bestandsprüfung zeigt klare
Weiterverwendungsstrategie, direkte Bezüge und offene Verhaltens-/Rückwegprüfungen.
Falsche Übernahmebereitschaft bei leerem/ungeklärtem Befund ist behoben; auch
ungeklärte Konfigurationen nehmen am Prüffingerabdruck teil. Haushaltsabnahme offen.
Keine neue Engine, kein Speicher und noch kein ausführbarer Automationsänderungsplan.
Die alte reine Vergleichspräferenz ist keine dauerhafte Produktgrenze. Live-Änderungs-
umfang bleibt bis zur Nutzerantwort offen; vorhandene HA-Steuerung unverändert lassen.

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
