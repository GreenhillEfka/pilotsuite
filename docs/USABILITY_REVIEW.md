# Bedienungsrevision — 2026-09-23

## Befunde und Änderungen

| Bereich | Befund | Umsetzung |
|---|---|---|
| Navigation | Lange Seite ohne Rückweg | Fixierte Links zu Übersicht, Einrichtung, Verläufen, Lernen und Mustern; Rücksprung im Fußbereich |
| Einrichtung | Reihenfolge und gesperrte Bedienung unklar | Drei Einrichtungsschritte und sichtbarer Bearbeitungshinweis; Abgleich während Bearbeitung gesperrt |
| Begriffe | Englische Fachbegriffe, alte Version im Fußtext | Deutsche Status-/Messwertbegriffe, feste Regeln getrennt von Lernmustern, Version nur aus Laufzeitstatus |
| Zonen | Alter Lerninhalt konnte unter neuem Zonennamen verbleiben | Sofort leeren, Rückmeldungen verzögerter Anfragen an Zone binden, alten Exportlink entfernen |
| Lernen | Module überladen den Einstieg | Module und Belegdetails aufklappbar; Lernaktionen oben; leere Lernfortschritte erklären den nächsten Schritt |
| Muster | Feedbackbestätigung fehlt | Gespeicherte Bewertung ausdrücklich bestätigen und aktuelle Auswahl markieren |
| Historie | Gesperrter Import ohne Erklärung, technische Datumsfehler | Grund anzeigen; fehlende, umgekehrte, zukünftige und zu alte Zeiträume lokal ablehnen |
| Darstellung | Unterschiedliche Eingaben; kleine Diagrammtexte | Einheitliche Zahlen-/Datumsfelder, responsive Karten, horizontal scrollbar lesbare Grafik |
| Tastatur | Fokus geht bei Aktualisierung verloren | Ein Tab-Einstieg pro Zonengruppe, Fokus erhalten; automatische Aktualisierung bei fokussierten Prüfdetails pausieren |
| Formulare | Mehrere Checkboxen unter einem äußeren Label | Sensorgruppen mit Fieldset/Legende, einzelne Quellen weiterhin beschriftet |

Die Referenzzone im Systemstatus ist eine globale Systemprüfung und nicht automatisch
die ausgewählte Zone. Regelstärke bleibt von statistischer Sicherheit und persönlichem
Feedback getrennt. Hauptsensoren, Freigaben, Algorithmen und Aufbewahrung unverändert.

## Abnahme

- Lokal: 123 Backendtests, vier JavaScript-Modelltests, Syntax- und Vertragsprüfung.
- Erweiterte Chromium-Prüfung: bestehende Speicher-/Konflikt-/Lern-/Exportpfade plus
  Navigation, Bearbeitungshinweis, fehlgeschlagenen Zonen-Kontext, Historiengrenzen und Überlauf bei 390/768/1440 px.
- Funktionsstand `4d3c8d3`: CI `35827201950` vollständig erfolgreich, einschließlich
  Chromium und amd64-Container. Synthetische Screenshots für 390/768/1440 px archiviert;
  Handy- und Desktopansicht visuell geprüft. Lokaler Chromium-Download fehlgeschlagen.
- Produktive Home-Assistant-Oberfläche und reale Sensordaten sind eine separate Abnahme.

## Offene Verbesserungen

Ein vollständiger Einrichtungsassistent, eine interaktive Diagramm-Zoomfunktion und
eine Aufteilung in echte Unterseiten bleiben weitere Arbeit. Diese Revision erhält
die vorhandenen API- und Speichermodelle. Sie behauptet keine neue Lernfähigkeit.
