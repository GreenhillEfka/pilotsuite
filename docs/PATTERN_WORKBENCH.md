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

Keine Migration, neue Lernfreigabe oder zusätzliche Sammlung. Tests verwenden nur
synthetische Muster. Nutzerbestätigung vom 23.09.2026: Das bisherige Diagramm wird
angezeigt. Dies bestätigt weder vollständige Recorder-Abdeckung noch die neue Werkbank.
