# Workspace — Alltag zuerst, Diagnose bei Bedarf

Seit Alpha.55 (PR #119) sind die drei Hauptzugänge und die zentrale Präsenzkarte
im bestehenden Frontend umgesetzt. Den aktuellen Installations- und CI-Stand führt
RELEASE_STATE.json; die angemeldete Haushaltsabnahme bleibt separat offen.

## Drei Hauptzugänge

| Zugang | Aufgabe | Bestehende Bausteine |
|---|---|---|
| Zonen | Zustand verstehen, Quellen einstellen, Verlauf ansehen | Cockpit, Zonenmodule, zonenbezogene Konfiguration und Verläufe |
| Werkzeuge | Bestand prüfen, Entitäten ordnen, Routinen bearbeiten | Organisationsansicht und vorhandene Werkbank |
| System | Verbindung, Version, Darstellung, Sicherung und Rettung | Status und bestehende Maintenance-/Rescue-Seite |

Das sind Navigationsgruppen, keine neuen Anwendungen oder Speicher.
Alte Links, `#ps-all` und gespeicherte Ansichtspräferenzen werden kompatibel zugeordnet.
Keine Funktion und kein ungespeicherter Entwurf darf verschwinden. Die technischen
Ansichtsschlüssel bleiben unverändert; es gibt keinen zweiten Router.

## Ein alltäglicher Zonenweg

Zonenliste → aktuelle Zone → **Zustand**, **Verlauf** oder **Einrichtung**.

Die erste Ansicht zeigt Anwesenheitszustand, kurzen Grund, Nachlauf beziehungsweise
Ungewissheit und getrennten HA-Publikationsstatus. Klima, Licht und Medien sind
sekundärer Kontext. Die Quelle dieses Präsenzstatus ist die bestehende Zoneninstanz,
nicht der ältere Rollen-Aggregatwert. Bei fehlender gültiger Instanz wird
„Unklar / nicht eingerichtet“ gezeigt, kein Ersatzwert als Wahrheit ausgegeben.

„Warum?“ öffnet Quellen und Entscheidungsverlauf. Erforderliche Datenlücken bleiben
bereits in der Zusammenfassung sichtbar. Sitzungstrace und Recorder-Verlauf werden
klar benannt. Ein nicht angelegter Ausgang ist kein Fehler der Präsenzberechnung.
Interner Boolean und öffentlicher Binärsensor sind verschiedene Darstellungen,
keine zwei frei konfigurierbaren Anwesenheitsmodelle.

Einrichtung führt durch vorhandene Auswahl und Verhalten: relevante Quellen,
Signaltypen, nachvollziehbarer Nachlauf, optional eigenes Ausgangspaket.
Relevanz braucht keine zweite Live-/Historienfreigabe. Vorhandene Legacy-Lernschalter
bleiben während der Migration als solche erkennbar; nicht einfach verstecken und
dadurch weiterhin erforderliche Backend-Bedingungen unerklärlich machen.

## Diagnose ohne konkurrierende Wahrheiten

Die Einrichtung bietet vier direkte Aufgaben: Anwesenheit/Nachlauf, Lichtquellen,
Entitäten sowie Name/Bereiche. Sie öffnen die vorhandenen Editoren derselben Zone,
keine zweite Konfiguration. Lichtquellen sind Zuordnungen, keine Schaltknöpfe.
Offene Entwürfe blockieren auch diese Einstiege; fehlende Bereitschaft wird erklärt.
Das gewünschte sichtbare Feld erhält Fokus. Ein Quellenfilter darf den Fokus nicht
auf eine ausgeblendete andere Rolle lenken. Automatische Aktualisierung öffnet
keinen Editor und verschiebt keinen Fokus. Der Hauptsensor-Link führt in die
Konfiguration, nicht in die Lernwerkbank.

Synthetisches Replay, alter expliziter Schattenvergleich, Strukturprüfung und
technische IDs gehören unter benannte Details/Werkzeuge. Sie bleiben erreichbar,
starten nicht durch Navigation und überschreiben keinen Live-Status.
Lichtvorschau ist als Vorschau gekennzeichnet. Der Prüfkompass bleibt Bestandteil
der Routinewerkbank, keine weitere Startseite.

Habituszonen liefert die Trennung von Übersicht, Bedienung, Status, Konfiguration
und Diagnose. Seine pauschale Gleichsetzung „nicht on = Ruhe“ wird nicht übernommen.

## Umsetzung im vorhandenen Frontend

`workspace.js` ordnet vorhandene Elemente, `workspace-model.js` enthält reine
Darstellungsfunktionen, `zone-presence.js` bedient die bestehende Zonen-API.
Diese Dateien schrittweise vereinfachen; kein zusätzlicher Overlay-Adapter, Router,
Frameworkwechsel oder unabhängiger Browser-Datenbestand. Zustandsänderungen werden
über die bestehenden revisionierten API-Wege gespeichert.

Filter bewahren unsichtbare Auswahl; Navigation blockiert bei ungespeichertem
Entwurf. Fehler bewahren Nutzereingaben. Passive Aktualisierung erhält Fokus,
Scrollposition und offene Details. Keine entfernten Assets, automatische Scans,
versteckten Schreibvorgänge oder scheinbar verfügbaren Steuerknöpfe.

## Prüfkriterien

Vorhandene Browserprüfungen weiterverwenden und vor der Änderung um den vereinfachten
Nutzerweg ergänzen: vier Zonen, direkte Links, leere/unklare Daten, parallele Revision,
Pause, Publikation ohne Paket, 390/768/1440 Pixel, beide Themes, Tastatur und
reduzierte Bewegung. GET/Navigation darf weder Paketanlage noch Metadata-Apply
auslösen. Bestehende API-Verträge bleiben kompatibel.

Synthetische Screenshots belegen Gestaltung im Testsystem. Erst die angemeldete,
zunächst ausschließlich lesende Ingress-Prüfung belegt den Haushalt-Nutzerweg.
Bedienzeiten und Verständnis dort messen; keine pauschale Barrierefreiheits-
oder Komfortverbesserungsbehauptung allein aus grünen Tests.
