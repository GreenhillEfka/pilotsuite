# PilotSuite: Review der Zonenansicht und Aktualisierung

## Befund

Die Hauptansicht fragt alle 15 Sekunden Status, Zonen und Kontext ab. Bisher wurde
der Alltagsbrief bereits vor jeder Antwort entwertet und die Zonenansicht auch bei
identischen Antworten vollständig neu gezeichnet. Präsenzinstanz und
Schattenvergleich zeichneten zusätzlich alle fünf Sekunden Bedienelemente und
Inhalt neu. Das erklärt verlorene aufgeklappte Details und kann auf einer langen
Seite die Leseposition verschieben. Eine authentifizierte Ingress-Reproduktion
im Haushalt steht noch aus; der Befund ergibt sich aus dem aktuellen Quellpfad.

## Vereinfachung

- Identische Kontext- und Zonenantworten behalten den bestehenden DOM und Fokus.
- Bei geänderten Daten bleibt die vertikale Leseposition bei passiven Updates
  erhalten. Automatische Antworten überschreiben keine offenen Bearbeitungen.
- Die Live-Bedienelemente bleiben bestehen; geöffnete Quelldetails und Musterbelege
  behalten ihren Zustand. Aktuelle Quellen und der Sitzungsverlauf der
  Präsenzinstanz sind einklappbar; der Kernstatus bleibt unmittelbar sichtbar.
- Der explizite Abgleich und die bestehenden fachlichen Freigaben bleiben
  getrennt. Die drei Poller werden nicht durch eine weitere Datenquelle ersetzt.

## Prüfstand und Grenze

70 JavaScript-Verträge und die bestehende Python-Suite bestanden lokal; Syntax und
`git diff --check` sind sauber. Chromium war in der lokalen Laufzeit nicht vorhanden.
Vor Auslieferung sind die vollständigen Browser-CI-Jobs und eine visuelle Prüfung
im authentifizierten Ingress offen. Die Prüfung sollte im gespeicherten
`Erdkellerbereich` und in einer andersartigen vorhandenen Zone nach mehr als 15
Sekunden Verweildauer stattfinden: Scrollposition, Fokus, geöffnete Abschnitte,
sichtbare aktuelle Werte und alle vier gespeicherten Zonen kontrollieren.

Dieses Paket verändert keine HA-Konfiguration, Automation, Lernfreigabe oder Geräte.
