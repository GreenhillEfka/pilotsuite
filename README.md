# PilotSuite

PilotSuite ergänzt Home Assistant um verständliche Habitus-Zonen: relevante
Quellen kombinieren, Präsenz mit begrenztem Nachlauf erklären und verfügbare
Verläufe auswerten. Home Assistant bleibt Eigentümer von Geräten, Zuständen und
Ausführung. Dieses Repository ist die einzige weitergeführte Implementierung.

## Stand und Grenzen

Die Quellversion steht in [VERSION](VERSION), die zuletzt verifizierte Installation
in [docs/RELEASE_STATE.json](docs/RELEASE_STATE.json). Ein Release-Receipt ersetzt
keine aktuelle Live-Prüfung. [CURRENT_STATE.md](CURRENT_STATE.md) nennt den nächsten
Schritt; [IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) trennt vorhandene
Funktionen von offenen Abnahmen.

Die App ist **nicht pauschal schreibgeschützt**: explizit bestätigte, begrenzte
Metadaten-/Helferpläne und die Veröffentlichung eigener Präsenzausgänge sind
implementiert. Allgemeines Apply bleibt geschlossen. Relevanz erlaubt Analyse,
niemals automatisch Haussteuerung. Eine Installation aktiviert keine neuen
Ausgänge und übernimmt keine vorhandene Automation.

## Konzept in Kürze

Eine bestehende Zoneninstanz verbindet relevante HA-Quellen, eine deterministische
Präsenzentscheidung und eine nachvollziehbare Anzeige. Optional kommt ein geprüftes
eigenes HA-Ausgangspaket hinzu. Unklar oder unavailable bedeutet nicht frei.
TV-/Nutzungsindizien dürfen Anwesenheit nur begrenzt stützen.

Die aktuelle Konzeptkonsolidierung priorisiert eine einfache Zonenansicht statt
mehrerer konkurrierender Statuskarten. Sie ist ein Umsetzungsplan, keine bereits
ausgelieferte neue Oberfläche. Die vier gespeicherten Zonen bleiben erhalten;
`golden_zone_area_ids` ist nur Erststart-Bootstrap, kein zweiter Zoneneditor.

## Installation und Entwicklung

Home Assistant → Einstellungen → Apps → App-Store → Repository
`https://github.com/GreenhillEfka/pilotsuite` hinzufügen. Für bestehende Installationen
zuerst den Iststand prüfen; keine Neuinstallation oder Wiederholung alter ZIP-Releases.

- [Installation](docs/INSTALLATION.md): Einrichtung und lesende Abnahme.
- [Entwicklung](docs/DEVELOPMENT.md): Abhängigkeiten, Tests und Containerbuild.
- [Release-Runbook](docs/RELEASE_RUNBOOK.md): überprüfbarer PR, CI und PilotSuite-only-Sicherung.

## Dokumentationsweg

| Frage | Zuständiges Dokument |
|---|---|
| Was soll das Produkt leisten? | [VISION](docs/VISION.md) |
| Wer besitzt welche Logik/Daten? | [ARCHITECTURE](docs/ARCHITECTURE.md) |
| Was wird als Nächstes umgesetzt? | [ROADMAP](docs/ROADMAP.md) |
| Wie soll die Bedienung einfacher werden? | [UX_WORKSPACE](docs/UX_WORKSPACE.md) |
| Welche Präsenz-/Ausgangsregeln gelten? | [ZONE_INSTANCE_V2](docs/ZONE_INSTANCE_V2.md) |
| Warum wurden Entscheidungen getroffen? | [DECISIONS](DECISIONS.md) |
| Welche Grenzen gelten für Zugriffe? | [SECURITY](docs/SECURITY.md) |

Ältere Paketdokumente beschreiben ihren historischen oder Legacy-Funktionsumfang,
nicht automatisch den aktuellen Gesamtzustand. Einstieg für Fortsetzungen:
[AI_CONTEXT.md](AI_CONTEXT.md). Kein zweites Repository, keine zweite Lernengine.
