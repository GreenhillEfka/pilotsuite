# Muster-Werkbank

Die Werkbank ergänzt die vorhandenen Musterkarten um Filter für offene, passende,
vertagte und abgelehnte Muster. Sie verwendet ausschließlich die aktuellen Kandidaten
und das bereits dauerhaft gespeicherte Musterfeedback. Abgelaufene Kandidaten
werden nicht als weiterhin aktuelle Vorschläge dargestellt.

„Belegkette und Prüfentwurf“ zeigt Quellen → Beobachtungszahlen → Algorithmus →
Prüfung. Der Graph wird aus vorhandenen Belegen abgeleitet und besitzt keinen
eigenen Speicher. Lichtkontext wird nur bei gleichem lokalen Zeitfenster und gleicher
Tagesgruppe ergänzt. Beobachtbarkeitswarnungen beziehen sich auf die gesamte Zone
im Aufbewahrungszeitraum, nicht auf eine geschätzte Genauigkeit des Einzelmusters.

Der JSON-Export enthält Zone, Revision, Musteridentität, Parameter, Quellen,
Beobachtungsstatistik, Regelstärke, unbekannte Konfidenz, Nutzerpräferenz, Belegkette
und offene Prüfschritte. Er ist ein datierter Zustand nur insofern die enthaltenen
Beobachtungstage dies belegen; kein laufend aktualisierter oder ausführbarer Plan.
Exports können private Sensorbezeichnungen und Routinen enthalten und gehören
nicht ins öffentliche Repository. Der Download erfolgt nur auf Nutzerklick.

Eine passende Routine erfordert anschließend ein Komfortziel, konkrete Zielgeräte,
Bestandsprüfung vorhandener Automationen, Bedingungen und einen Rückweg. Der Export
enthält keine HA-Serviceaktionen, keine erfundenen Zielwerte und keine Schaltfreigabe.
Eine künftige Ausführung benötigt einen eigenständigen, versionsgebundenen Plan mit
Freigabe, Sicherung und Verifikation. Die heutige Apply-Sperre bleibt bestehen.

## Zeitlich getrennte Prüfung (alpha.17)

Die Werkbank verwendet dieselbe Rückblickfunktion wie die Historienansicht. Für die
gespeicherten Aktivierungen wird das feste, rollende 14-Tage-Aufbewahrungsfenster
am Berichtszeitpunkt in frühere 70 % und spätere 30 % geteilt. Im früheren Teil
müssen Mindestaktivierungen und Mindesttage allein erfüllt sein. Erst dann bedeutet
mindestens eine spätere Aktivierung im gleichen lokalen Zwei-Stunden-Fenster und
derselben Tagesgruppe „Später erneut beobachtet“. Spätere Daten trainieren den
früheren Teil nicht. Unterschiedliche Zonen, Stunden und Tagesgruppen bleiben getrennt.

Auch ein insgesamt qualifiziertes aktuelles Muster kann im frühen Teil noch zu
wenige Belege haben. Keine späteren Belege sind keine Widerlegung: Ausfälle,
widerrufenes Lernen und fehlende Daten bleiben mögliche Ursachen. Ein einzelnes
erneutes Auftreten ist weder Genauigkeitsquote noch unabhängige Live-Validierung.
Die gewählten Schwellen können bereits anhand des gesamten Zeitraums angepasst
worden sein; daher wird keine unverzerrte Prognoseleistung behauptet.

API: `reobservation` in der bestehenden Kontextantwort, `temporal_check` im
abgeleiteten Prüfentwurf. Enthalten sind Zeitraum, Trennzeitpunkt, Zeitzone,
frühere/spätere Ereignis- und Tageszahlen und der Prüfstatus. Die vorhandenen
`checks` der Historienantwort enthalten weiterhin nur früh qualifizierte Fenster;
`windows` ergänzt alle geprüften Fenster. Quellen und historische Anteile bleiben
im bestehenden Statistikvertrag. Export erfolgt weiterhin nur auf Nutzerklick.

Keine Migration, neue Lernfreigabe oder zusätzliche Sammlung. Tests verwenden nur
synthetische Muster. Nutzerbestätigung vom 23.09.2026: alpha.16 Zonen-Assistent,
Zonenwechsel und Werkbank funktionieren. Dies ist Nutzerabnahme der Oberfläche,
keine unabhängige Netzwerkprüfung und kein Nachweis realer Lernqualität. Die neue
Zeitprüfung benötigt nach Installation ihre eigene Bedienabnahme.
