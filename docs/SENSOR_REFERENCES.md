# Hauptsensoren und automatische Zonenreferenzen

## Verbindliches Konzept

Eine Zone verwendet pro unterstützter Klasse eine Hauptsensorgruppe. Daraus entsteht
zur Laufzeit ein virtueller Referenzwert; keine zusätzliche manuelle Referenzauswahl
und keine neue HA-Entität. Relevanz bleibt die Zulassung zur Beobachtung. Hauptrollen
bestimmen, welche dieser bestätigten Quellen den Zonenwert bilden. Ungeprüfte und
ignorierte Entitäten sind in beiden Stufen ausgeschlossen.

| Klasse | Automatische Referenz | Aussagegrenze |
|---|---|---|
| Temperatur | Median, Min/Max und Spanne der gültigen Hauptsensoren | Bereichszusammenfassung, keine einzelne Raumtemperatur |
| Feuchte | Median, Min/Max und Spanne | Keine Lüftungsentscheidung allein aus relativer Feuchte |
| Helligkeit | Median, Min/Max und Spanne; lx/lux vereinheitlicht | Unterschiedliche Messorte bleiben sichtbar; keine automatische Schaltschwelle |
| Präsenz/Bewegung | Mindestens eine gültige aktive Hauptquelle | Aktivität, kein sicherer Nachweis dauerhafter Anwesenheit |
| Lichtzustand | Mindestens eine aktive Hauptquelle | Schaltzustand, unabhängig von gemessener Helligkeit |

Ausfälle werden nicht zu Nullwerten. Ohne aktive Meldung ergibt eine fehlende oder
ungültige Hauptquelle unbekannt statt Abwesenheit. Bewusst leere Gruppen bleiben
leer; keine Ersatzquellen. Keine unbemerkte Erweiterung um neue Sensoren.

Externe Vergleichssensoren sind fachlich etwas anderes: etwa Außentemperatur für
Innen/Außen-Vergleiche. Die bisherige gespeicherte Referenztemperatur bleibt als
**externe Vergleichstemperatur** erhalten und fließt nicht in den Zonenwert ein.
Andere externe Vergleichsklassen sind noch nicht implementiert.

Weitere HA-Klassen benötigen eigene fachliche Operatoren: Energiezähler werden
nicht blind gemittelt oder summiert, Sicherheitsalarme nicht durch Median verdeckt.
Das einheitliche Referenzformat ist erweiterbar, nicht die Behauptung, jede beliebige
HA-Klasse bereits fachgerecht zusammenzufassen.

## Präsenz: eine Quellenwahl

Anzeige und Lernen verwenden dieselbe gespeicherte Präsenzgruppe. Ohne Gruppe
bleibt die Anzeige bei „Keine Hauptsensoren ausgewählt“, statt alle relevanten
Sensoren ersatzweise zu verwenden. Lernen benötigt zusätzlich explizite Zustimmung.
Ein inaktiver Bewegungsmelder beweist keine Abwesenheit.

Beim Speichern werden auch leere Rollenlisten persistiert. Die bisherige Entfernung
leerer Listen konnte eine bewusste Abwahl in eine automatische Auswahl verwandeln.
Vorhandene Klimazonen mit genau einem relevanten Sensor behalten bis zur expliziten
Bearbeitung ihren bisherigen Standard. Der Editor zeigt diesen wirksamen Standard
angehakt, damit Öffnen und Speichern die Auswertung nicht unerwartet ändern.

## Umsetzung und Abnahme

Keine DB-Schemaänderung, keine Umschreibung vorhandener Rollen oder Lernfreigaben.
Export enthält gespeicherte und wirksame Rollen; Zonenübersichten enthalten den
virtuellen Referenzwert mit Quellen, Qualität und Aggregationsmethode.
Tests prüfen leere Auswahl, Präsenzgruppe nach erneutem Laden, Ausfalllogik,
Lux-Normalisierung, getrennte Vergleichswerte und Bedienung über den mobilen Editor.
Live-Ingress-Abnahme und Veröffentlichung sind getrennt zu dokumentieren.
