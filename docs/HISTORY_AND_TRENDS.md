# Historie, Verläufe und rückwirkendes Lernen

Seit alpha.12 enthalten und auf Home Assistant installiert. Authentifizierte
Ingress-Bedienung und tatsächliche Recorder-Abdeckung bleiben separat abzunehmen.

## Bedienung

Im Zonenreiter „Verläufe und historische Muster“ öffnen. Gespeicherte Hauptgruppen
und als relevant bestätigte, aktuell vorhandene Entitäten liefern die Quellen.
Nicht gespeicherte automatische Rollen werden nicht stillschweigend importiert.
Zeitraum wählen: 24 Stunden, 7/14/30 Tage oder explizite Start-/Endzeit innerhalb
der letzten 30 Tage. Freie Eingaben verwenden die Browser-Ortszeit; Anzeige und
Muster verwenden die gespeicherte Zonenzeitzone, die ausdrücklich angezeigt wird.

„Genaue Zustandsverläufe“ liest ausgewählte HA-Zustände, „Langzeitstatistik“ liest
Stundenmittel geeigneter Temperatur-/Feuchte-/Helligkeitssensoren. Die tatsächlich
vorhandene Historie kann kürzer sein. Keine Daten bedeutet nicht kein Verhalten.
HA-Aufbewahrung oder Recorder-Konfiguration werden nicht geändert.

Temperatur, Feuchte und Lux zeigen die Zonenreferenz mit Min/Max der Hauptquellen.
Einzelquellen können zusätzlich eingeblendet werden. Präsenz und Licht lassen sich
auf derselben Zeitachse darstellen. Grafiken bieten Messpunkte mit Zeit/Wert sowie
eine aufklappbare Tabelle. Stundenmittel bleiben Quellenwerte: keine künstliche
Zonenreferenz aus Mittelwerten und keine Schaltfolgen daraus ableiten.

## Zwei verschiedene Freigaben

1. Historie anzeigen: expliziter Abruf, nur flüchtig verarbeitet. Kein Rohdatenarchiv.
2. Aktivierungen für Lernen übernehmen: bestehende Lernfreigabe, aktive Zone und
   zusätzlicher einmaliger Haken für exakt diesen Zeitraum erforderlich. Höchstens
   14 Tage zurück, nur vollständig relevante gespeicherte Präsenzgruppe.

Historische Licht-/Lux-Kontextbelege werden in diesem Paket **nicht** gespeichert.
Die Live-Kontextfreigabe wird nicht als rückwirkende Erlaubnis interpretiert.
Rollen, Zeitzone und Freigaben werden durch Abruf/Import nicht geändert.

## Datenvertrag und Grenzen

- HA bleibt Datenquelle: unterstützte WebSocket-Kommandos
  `history/history_during_period`, `recorder/get_statistics_metadata` und
  `recorder/statistics_during_period`. Kein SQL gegen die HA-Datenbank.
- Maximal 100 Quellen und 30 Tage pro Abruf, tageweise Anfragen, maximal 50.000
  Antwortdatensätze, 90 Sekunden Gesamtlimit und nur ein Historienauftrag zugleich.
  Fehlgeschlagene, ungültig strukturierte oder zu große Antworten importieren nichts;
  Zeitraum verkürzen und HA-Recorder prüfen.
- Rohdaten bleiben flüchtig. Diagramme haben maximal 481 Abtastzeitpunkte pro Quelle;
  Stundenstatistiken maximal etwa 720. Der Lernpfad nutzt unverdichtete Zustände.
- Auf Grafiken werden letzte Zustände höchstens eine Stunde fortgeschrieben.
  Danach unbekannt; das ist eine konservative Darstellungsgrenze, kein Defektbeweis
  eines unveränderten Sensors. Stundenstatistiken werden nicht über Lücken verbunden.
- Temperatur C/F/K normalisiert, Feuchte 0–100 %, Lux nichtnegativ; ungültige Werte
  bleiben null. Präsenz-OR: eine aktive Quelle reicht; alle aus nur bei vollständigen
  gültigen Quellen. Partieller numerischer Median zeigt vorhandene Werte; Messpunkte
  des API enthalten zusätzlich gültige/gesamte Quellenzahl.
- Recorder-Zustände und Importfenster beweisen keine durchgängige Sensorabdeckung.
  Historische Abrufe erzeugen keine künstlichen Live-Beobachtbarkeitsstichproben.
- Aktuelle Sensorgruppen werden rückwirkend angewendet. Frühere Raumnutzung,
  Geräteumbauten und Rollen sind unbekannt. Keine historische Zuordnung erfinden.
- Lernbelege: nur nachweisbare off→on-Wechsel, kein Startzustand und kein unknown→on.
  Pro Zone fünf Minuten Abstand, wie activity-v1. Transitionsherkunft bleibt unknown;
  „historisch“ ist Datenherkunft, nicht menschliche Bedienung.
- Import mit Transaktion und Revision: Quellen/Freigabe/Zone nach dem Netzabruf erneut
  prüfen. Konflikte brechen ab. Deduplizieren gegen frühere **und** spätere vorhandene
  Belege, einschließlich Live-Daten. Wiederholter Import zählt nichts doppelt.
- Ein Speicherbesitzer: bestehende activity_evidence und activity-v1, kein zweiter
  Lerner. Historische Herkunft und Importfreigabe separat protokolliert. Unverändert:
  14 Tage und 5.000 Belege global. Importausgabe trennt neu angenommen und nach
  Kapazitätsbegrenzung tatsächlich erhalten. Feedback verändert keine Zähler.
- Export enthält Importnachweise, Quellen und Zeiträume. Reset/Präsenzgruppenwechsel
  löscht Belege, Herkunft und Nachweise. Widerruf verhindert neue Importe; bestehende
  Belege laufen aus. Backups werden durch Reset nicht nachträglich geändert.

## Musterprüfung

Nur bei vorhandener Lernfreigabe und Rohzuständen. Wochenraster zählt deduplizierte
Aktivierungen pro lokalem Wochentag/Zwei-Stunden-Fenster. Strich heißt keine Belege,
nicht bestätigte Nullnutzung. DST/Zeitzonen verwenden dieselbe time_bucket-Funktion
wie activity-v1. Keine neue konfigurierbare Parallelengine.

Zeitlich getrennte Prüfung: erste 70 % des angefragten Zeitraums zur Musterbildung
mit den vorhandenen Mindestereignissen/Mindesttagen, letzte 30 % ausschließlich zur
Anzeige späterer Wiederholungen. Spätere Belege können die Trainingsschwelle nicht
nachträglich erfüllen. „Erneut beobachtet“ bedeutet keine statistische Validierung,
keine Genauigkeit oder Schaltfreigabe. Ohne spätere Daten bleibt das Ergebnis offen.
Der Split ist derzeit fest; Algorithmus-/Zeitzoneneinstellungen bleiben je Zone.

## API und Migration

POST `/api/v1/zones/{id}/history`: start/end (ISO-Zeit mit Offset oder Epochsekunden),
mode (`states` / `statistics`), revision. Liefert begrenzte Verläufe und, bei
Lernfreigabe, retrospektive Prüfungen. POST `.../history/import` zusätzlich
`consent: true`; nur states. Invalid 400, Versionskonflikt 409; Ingress-Schutz bleibt.

Schema 6 ergänzt history_imports und history_provenance im bestehenden Store.
Vor Migration eine SQLite-Sicherung; Rollen und bisherige Freigaben bleiben erhalten.
Vor Release zusätzlich App-und-Daten-Backup erstellen (Auto-Updates berücksichtigen).
Rückweg: passende App-und-Daten-Sicherung wiederherstellen; kein alpha.11-Code auf
Schema 6. Noch kein Release, kein Live-Historienimport, keine HA-Konfigurationsänderung.

## Prüfungen und offene Live-Abnahme

Regressionen: Rohzustände/HA-Kompressionsformat, Statistik-Millisekunden, Einheiten,
Startzustände, unbekannte Zustände, Multi-Sensor-Entprellung, zeitliche Holdout-Trennung,
Migration 5→6 mit Sicherung, Neustart, doppelte/überlappende Importe, Quellenabwahl,
Widerruf, Pause, Reset, Netzfehler, HTTP-Routen und geschützte JS-Auslieferung.
Browser prüft Diagramme, Importhaken, Statistik-Importsperre und freie Zeitraumwahl.
CI umfasst Container und wirklichen Modulstart. Echte HA-Datenqualität, vorhandener
Recorder-Zeitraum und individuelle Ingress-Bedienung bleiben separate Abnahmen.

Quellen: https://www.home-assistant.io/integrations/recorder/
https://www.home-assistant.io/dashboards/statistics-graph/
https://github.com/home-assistant/core/blob/dev/homeassistant/components/history/websocket_api.py
https://github.com/home-assistant/core/blob/dev/homeassistant/components/recorder/websocket_api.py
