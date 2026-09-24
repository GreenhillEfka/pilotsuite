# PilotSuite – Entwicklungsmandat

Bestätigt vom Nutzer am 24.09.2026. Dieses Mandat ergänzt VISION.md und
ROADMAP.md; es ist kein Installations- oder Ausführungsnachweis.

## Auftrag und Ziel

Ausschließlich GreenhillEfka/pilotsuite eigenständig in zusammenhängenden
Nutzerpaketen fortsetzen. Vorhandene Home-Assistant-Geräte und Automationen
sollen verständlich unterstützt und der Bedienaufwand reduziert werden:
Beobachten -> Zusammenhänge und Grenzen erklären -> vorhandene Automationen
berücksichtigen -> Nutzerentscheidung unterstützen -> später gesondert
freigegeben ausführen -> Wirkung prüfen. Keine Neuimplementierung, keine
zweite Lernengine, kein weiterer PlanStore und keine Schattenkonfiguration.

## Fortsetzung und Arbeitskoordination

Der bestehende Auftrag „PilotSuite: Pakete entwickeln“ wurde vom Nutzer
wieder aufgenommen und ist stündlich eingerichtet. Dies ersetzt die historische
Pause, aber keine Grenze für HA-Zugriffe oder Geräteausführung. Es gibt keinen
Zehn-Minuten-Takt und keinen sofortigen Abschluss-Webhook. Ein laufender Aufruf
darf ein zusammenhängendes Paket in mehreren geprüften Teilschritten bearbeiten.
Vor jeder Fortsetzung aktuellen App-Stand, main, offene PRs/Branches, CI und
dokumentierte Bearbeitung prüfen. Vorhandene Arbeit fortsetzen; keine konkurrierende
Implementierung. Ein offener PR allein beweist keinen aktiven Agenten. Unklare
Exklusivität oder geänderte Revisionen stoppen konkurrierende Schreibaktionen.
Nur konfliktgeschützte Writes, kein Force. PR-Kommentare und Statusdateien
halten Bearbeitungsumfang, tatsächliche Ergebnisse und genau einen nächsten
Schritt fest. Eine Arbeitsnotiz ist keine atomare globale Agentensperre.

## Nächstes zusammenhängendes Paket

Prüfkompass in der vorhandenen Muster-/Routinewerkbank, nach aktuellem Quellabgleich.
Die fünf getrennten Bereiche Quellen, Beobachtungsgrundlage, Nutzerziel/Ziele,
Automationsbezüge und Notizaktualität werden aus bestehenden Besitzern abgeleitet.
Verständliche Gründe, Herkunft und genau ein priorisierter nächster Schritt je
Entwurf; eine gefilterte Zonenübersicht ohne neuen Queue-Speicher. Fehlende,
veraltete oder nicht prüfbare Daten sind weder unbedenklich noch freigegeben.
Keine globale Sicherheitsquote, keine automatische Prüfung oder Neubewertung
beim GET/Reload und kein Autosave. Eigene Texte und Konfliktinformationen erhalten.
Mobile/Desktop-/Tastaturbedienung, sichere Ausgabe, Leer-/Fehlerzustände und
synthetische Regressionsprüfungen gehören zum Paket. Vorhandene Module verwenden;
eine Chat-Referenz ist kein integrierter Quellstand.

Danach den realen Nutzen im bereits genehmigten Erdkeller-Umfang und später in
einer andersartigen, bereits genehmigten Zone nachweisen. Fehlende Einwilligung
wird nicht abgeleitet. Lerntransparenz und Gegenbeispiele vor weiteren Algorithmen.
Ein Aktionspilot, native HA-/Assist-Oberflächen und optionale LLM/RAG-Funktionen
bauen auf diesem gemeinsamen Weg auf und bleiben an ihre eigenen Gates gebunden.

## Unveränderte Grenzen

Autonome Entwicklung, Tests, Dokumentation und die bereits genehmigte
PilotSuite-only-Backup-/Store-Routine sind erlaubt. Haussteuerung ist es nicht:
hard_read_only und Apply bleiben unverändert geschlossen. Keine Änderungen an
HA-Konfiguration, Automationen, Aktoren, Lernfreigaben, anderen Apps, Core,
Supervisor oder Host. Keine zusätzlichen Rechte, Geheimnisse, Haushaltsscans,
Datenimporte oder Lernquellen. LLMs erhalten keinen unmittelbaren Steuerpfad.
RELEASE_RUNBOOK.md gilt vor jedem Release, einschließlich frischer abgeschlossener
PilotSuite-only-Sicherung vor Veröffentlichung bei aktivem auto_update. Genau eine
passende Installation, keine spekulativen Neustarts/Rebuilds. Reale UI-Abnahme,
App-Leserechte, Datenerhalt und Image-Attestierung werden separat ausgewiesen.
RELEASE_STATE.json dokumentiert nur tatsächliche Auslieferungen.

## Nachweisstufen

Quelländerung, lokale Tests, exakte Kandidaten-CI, Main-CI, Store-Angebot,
Installation und echte Live-Abnahme bleiben unterschiedliche Nachweise. Fehlende
Werkzeuge sind keine fehlende Nutzerfreigabe. Keine erfundenen Commits, erneuten
Projekte oder wiederholten unverbundenen Prototypen. Eine neue ausdrückliche Pause
oder Einschränkung des Nutzers gilt unmittelbar.
