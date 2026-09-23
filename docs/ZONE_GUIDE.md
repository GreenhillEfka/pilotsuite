# Zonen-Assistent

Der Assistent beantwortet für die ausgewählte Zone: Was fehlt, und wo prüfe ich es?
Er liest bestehende Auswahl, Rollen, Zonenstatus und Lernbelege. Er speichert keinen
zweiten Einrichtungszustand und aktiviert weder Lernen noch Geräteaktionen.

Priorität: Quellenauflösung, bewusste Auswahl, aktive Auswertung, Datenverbindung,
Präsenzgruppe, freiwillige Lernfreigabe, vorhandene Muster. Fehlende oder pausierte
Voraussetzungen werden zuerst gezeigt. Ausgeschaltetes Lernen bleibt eine gültige
Entscheidung. Links öffnen nur bestehende Bereiche; Änderungen benötigen weiterhin
deren ausdrückliche Bedienung. Ungeprüfte Quellen zählen nicht als bestätigt.

Fehlende Aktivierungen und Tage beziehen sich auf ein einzelnes Zeitfenster; Auswahl
nach fehlenden Tagen, Ereignissen und Startstunde. Unterschiedliche Fenster werden
nicht addiert. Es gibt kein vorhergesagtes Fertigdatum. Aufbewahrte Muster bleiben
von aktueller Sammlung getrennt. Status ist kein Beweis physischer Sensorfrische,
keine Live-Abnahme und keine Ausführungserlaubnis.

API: `guide` in der bestehenden zonengebundenen Kontextprojektion, Schema
`pilotsuite-zone-guide-v1`. Kein neuer Endpoint oder Speicher. Die Projektion ist
kopiert und verändert weder Konfiguration noch Belege. UI verwendet Textknoten und
eine feste Liste von Navigationszielen. Zonenwechsel/Fehler entfernen alte Hinweise.

Regressionen verwenden ausschließlich synthetische Daten: acht neue Backendtests,
Browsernavigation ohne Schreibaufruf und Fehlerzustand ohne veraltete Hinweise.
Authentifizierte HA-Ingress-Abnahme bleibt gesondert erforderlich.
