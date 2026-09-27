# PilotSuite — Entwicklungsmandat

Konsolidiert am 28.09.2026 aus dem bestehenden Fortsetzungsauftrag und der
ausdrücklichen Bitte um konzeptionelle Vereinfachung. Dieses Dokument beschreibt
den Arbeitsumfang, keine zusätzliche Haussteuerungsfreigabe.

## Ziel und Arbeitsweise

Ausschließlich `GreenhillEfka/pilotsuite` weiterentwickeln. Bestehende Funktionen,
Zonen, Entitätsbereinigung und uncommittete Arbeit erhalten. Keine neue Engine,
kein neues Repository, keine Schattenkonfiguration. Vor jeder Fortsetzung
Git-/Main-Stand, offene PRs und bei verbundenem HA-MCP die tatsächliche App
`0d79c5e8_pilotsuite` prüfen.

Ein zusammenhängendes Nutzerpaket gleichzeitig: erst Problem und vorhandenen
Besitzer belegen, dann Regression, Änderung, Prüfung und überprüfbarer Branch/PR.
Eine grüne Endpointprüfung ist kein fertiger Nutzerweg. Die
[ROADMAP](ROADMAP.md) legt die Reihenfolge fest, nicht die historische Zahl
abgeschlossener Teilpakete. Veraltete Aussagen dürfen mit Begründung korrigiert
werden; Belege bleiben über Git und Changelog erhalten.

Keine dauerhaft gültigen Aussagen über Zeitpläne, laufende Agenten oder Freigaben
aus alten Arbeitsnotizen ableiten. Ein offener PR ist keine Sperre und kein Beweis
aktiver Arbeit. Bei konkurrierenden Änderungen Revision/Basis erneut prüfen,
keine Force-Writes. Aktuelle Nutzeranweisungen gehen historischen Mandaten vor.

## Datenzugriff und Schreibgrenzen

Lesende Entwicklungsanalyse der HA-Entitäten und Automationskonfigurationen ist
autorisiert. Im Produkt autorisiert `relevant` Live- und verfügbare historische
Auswertung ohne zusätzliche Datenfreigabe. Aufbewahrung, Export, Reset und Pause
bleiben kontrollierbar. Legacy-Lernfelder nicht stillschweigend umschreiben.

Hauszustände, vorhandene Automationen, Helfer, Metadaten und technische IDs werden
nicht zur Abnahme verändert. Keine Testschaltungen und keine ungeprüften
Umbenennungen. Das Habituszonen-Dashboard ist Referenz; seine Konfiguration bleibt
unverändert. Alle vier gespeicherten Zonen sind zu erhalten.

Die bereits genehmigte PilotSuite-only-Backup-/Update-Routine bleibt auf diese App
beschränkt. `presence_adoption_review` ist nicht hard_read_only; begrenzte vorhandene
Writer werden weder geleugnet noch durch diesen Auftrag neu aktiviert. Allgemeines
Apply bleibt geschlossen. Ingress, Authentifizierung und Sandbox bleiben bestehen.

## Nachweise und Übergabe

Implementiert, getestet, installiert und im Haushalt abgenommen getrennt ausweisen.
[RELEASE_STATE.json](RELEASE_STATE.json) dokumentiert tatsächliche Lieferung,
[CURRENT_STATE.md](../CURRENT_STATE.md) nur aktuellen Arbeitsstand und nächsten Schritt.
Ältere Release-Chroniken nicht in jede Übergabe kopieren.

Vor Veröffentlichung einer neuen App-Version gilt
[RELEASE_RUNBOOK.md](RELEASE_RUNBOOK.md), einschließlich verifizierter
PilotSuite-only-Sicherung bei aktivem auto_update. Eine reine Konzeptänderung
rechtfertigt keinen Neustart, kein Store-Update und keinen neuen Release-Receipt.

Angemeldete Ingress-Abnahme zunächst ausschließlich lesend. Fehlender Browser ist
kein Anlass, Berechtigungen zu erweitern, und kein Hindernis für synthetische
Weiterentwicklung. Ein nicht beobachteter Haushaltzustand bleibt ausdrücklich offen.
