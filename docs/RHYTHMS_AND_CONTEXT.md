# Paket: lokale Rhythmen, Beobachtbarkeit und Lichtkontext

Entwicklungsstand in PR #9. Noch kein auf Home Assistant abgenommenes Release.

## Lokale Rhythmen

Unter „Rollen / Lernfreigabe bearbeiten → Lernalgorithmus einstellen“ lässt sich
je Zone eine IANA-Zeitzone (beispielsweise Europe/Berlin) speichern. Der Standard
bleibt UTC; Bestandszonen werden nicht unbemerkt umgestellt. Optional trennt die
Analyse Montag–Freitag von Samstag–Sonntag. Feiertage sind nicht berücksichtigt.

UTC-Ereigniszeitpunkte bleiben unverändert gespeichert. Für die Bewertung werden
lokale Kalendertage und Zwei-Stunden-Fenster gebildet. Bei der Herbstumstellung
zählen wiederholte lokale Stunden zum selben Tag/Fenster, im Frühjahr werden keine
Belege für nicht existierende Stunden erzeugt. Mindesttage gelten pro Tagesgruppe
und Fenster, nicht über zusammengeworfene Werktage/Wochenenden hinweg.

Zeitzone und Tagesgruppierung gehören zur Musteridentität. Parameteränderungen
bewerten vorhandene Belege neu; Feedback auf anders definierte Muster wird nicht
übertragen. Unveränderte UTC-Standardeinstellungen erhalten die alte Identität.
Die Containerprüfung stellt die Verfügbarkeit der IANA-Zeitzonendaten sicher.

## Beobachtbarkeit ist keine Anwesenheit

Bei freigegebenem Lernen erfasst PilotSuite während Zustands-/Snapshot-Abgleichen
Stichproben in Fünf-Minuten-Abschnitten: bereit, Verbindung fehlt, keine geeignete
Quelle, nur teilweise geeignete Quellen oder Zone pausiert. Mehrere Zustände im
selben Abschnitt bleiben erhalten; ein Abschnitt mit gemeldeter Einschränkung wird
nicht als uneingeschränkt dargestellt.

Angezeigt werden geprüfte Abschnitte, Abschnitte mit Einschränkungen und Abschnitte
zwischen erster/letzter Stichprobe ohne Prüfung. Zeit vor der ersten und nach der
letzten Stichprobe ist damit nicht beurteilt. Es gibt weder einen Uptime-Prozentwert
noch die Behauptung durchgängiger physischer Sensorüberwachung. Ein App-Ausfall
liefert keine Stichproben; nach Wiederanlauf bleiben die Zwischenräume ungeprüft.
Widerruf beendet neue Stichproben. Aufbewahrung 14 Tage, maximal 50.000 Prüfeinträge
global. Bei Kapazitätsgrenzen fallen ältere Einträge heraus; daraus wird keine
Nichtbenutzung oder Abwesenheit abgeleitet.

## Zusätzlich freizugebender Lichtkontext

Das Modul activation-context-v1 ist standardmäßig aus. Seine Checkbox erlaubt,
bei einer bereits akzeptierten Aktivierung zusätzlich Lichtzustand und Luxwert
festzuhalten. Voraussetzung ist die allgemeine Lernfreigabe. Verwendet werden
nur ausdrücklich gespeicherte relevante Hauptgruppen. Unvollständige/ungültige
Gruppen bleiben unbekannt; nicht ausgewählte Quellen werden nicht eingesetzt.

Gespeichert wird der Zustand aus der aktuellen HA-Projektion bei Verarbeitung des
Ereignisses, inklusive Quellen und Erfassungszeit. Das ist keine Garantie exakter
physischer Gleichzeitigkeit: Ereignisse können bis zu zwei Minuten verzögert
ankommen, Snapshot-/Ereignisfolgen sind keine atomare HA-Transaktion. Licht kann
bereits eingeschaltet sein; die Daten belegen nicht „Präsenz hat Licht geschaltet“.
Ein Lux-Median über mehrere Räume bleibt eine Zonen-Zusammenfassung.

Die Übersicht zeigt pro Zeitfenster/Tagesgruppe: Aktivierungen, Tage, Licht an/aus/
unbekannt sowie Anzahl und Median bekannter Luxwerte. Ein Prüfhinweis erscheint
erst mit genug bekannten Lichtzuständen an genug verschiedenen lokalen Tagen.
Unbekannte Lichttage können diese Mindesttage nicht erfüllen. Ein Hinweis fragt
nach gewünschtem Lichtbedarf und vorhandenen Automationen; er enthält keinen
Serviceaufruf, keine Zielhelligkeit und keine Schaltfreigabe.

Kontextbelege hängen an den deduplizierten Aktivierungen (maximal 5.000 global,
14 Tage). Ein Wechsel der Licht-/Luxgruppe löscht nur deren Kontextbelege; ein
Wechsel der Präsenzgruppe löscht wie bisher Aktivitätsbelege/Feedback und zusätzlich
Kontextbelege/Prüfstichproben. Die Oberfläche weist vor Gruppenwechseln darauf hin.
Widerruf stoppt neue Daten; vorhandene laufen aus. Reset entfernt sämtliche
Lernbelege der Zone und beide Freigaben. JSON-Export enthält UTC-Rohzeitpunkte,
Kontextbelege und Stichproben; die normale Dashboard-API nur Zusammenfassungen.

## Migration und Rückweg

SQLite-Schema 5 ergänzt zwei Tabellen im bestehenden Speicher. Vor Migration aus
Schema 1–4 wird eine eigene Datenbankkopie erstellt. Auswahl, Rollen, Feedback und
bisherige Lernfreigabe bleiben erhalten; Kontextfreigabe wird nicht abgeleitet.
Vor einem Release muss zusätzlich die PilotSuite-App mit Daten gesichert werden.
Ein Rückwechsel auf Schema-4-Code erfordert die passende App-und-Daten-Sicherung;
ein einfaches Downgrade mit Schema 5 wird vom älteren Code abgewiesen.

## Abnahme

- Lokale Mitternacht, Werktag/Wochenende und beide Zeitumstellungen geprüft.
- Bekannte/fehlende Gruppen, zusätzliche Freigabe, Widerruf und Reset geprüft.
- Kontextbelege am tatsächlichen Service-Ereignispfad mit API/Export geprüft.
- Datenbankmigration sichert Schema 4 und erhält gespeicherte Entscheidungen.
- UI speichert Zeitzone, Gruppierung und Kontextfreigabe; Tests öffnen erneut.
- Browser-/Container-CI erforderlich; echte Mehrtagesmuster und die individuelle
  HA-Bedienung werden dadurch nicht als live abgenommen behauptet.

Später: zeitliche Licht-Schaltfolgen, Schattenbetrieb und konkrete HA-Entwürfe.
Diese sind nicht Bestandteil dieses Pakets; die Ausführungsgrenze bleibt gesperrt.
