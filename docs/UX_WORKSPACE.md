# Workspace — Alltag zuerst, Diagnose bei Bedarf

Überarbeitet am 29.09.2026 nach Nutzerfeedback; Zielkonzept gemäß ADR-043.
Alpha.69 besitzt drei Hauptzugänge, Zonenpräsenz, Konfiguration, vier direkte
Einrichtungseinstiege und einen thematischen Automationsbereich je Zone.
IMPLEMENTATION_STATUS.md beschreibt Fähigkeiten, RELEASE_STATE.json die Installation.
Die angemeldete Haushaltsabnahme bleibt ein eigener Nachweis.

Erstes Umsetzungspaket, Alpha.69 installiert: eigener Automationsbereich, ausdrückliche
Themenzuordnung im bestehenden Profil, geteilte Verwendung und geladene Aktivierung,
begrenzte deduplizierte Auswahlprüfung, Fokus-/Entwurfsschutz. Helferzuordnung bleibt
derselbe Editor. Zweites Paket, Alpha.70 installiert: Bestandsmeldung zuerst, getrennte
Vergleichsansicht, fokussierte Wege zur jeweiligen Helferrolle und verständliche
Vorschau des bestehenden eigenen Ausgangspakets. Alpha.71 installiert (PR #151) ergänzt
die gezielte Einzelanlage fehlender Booleans/Timer; aktive HA-Parameter bearbeiten
und Automationen anschließen/übernehmen bleibt offen. Installation siehe Receipt.

## Drei Hauptzugänge

| Zugang | Aufgabe | Bestehende Bausteine |
|---|---|---|
| Zonen | Eine Habituszone vollständig einrichten und verstehen | Übersicht, Einrichtung, Automationen, Verlauf/Diagnose |
| Werkzeuge | Zonenübergreifende Sonderfälle und Altbestand bearbeiten | Globaler Bestandscheck, Bereinigung, vorhandene Lern-/Routinewerkbank |
| System | Verbindung, Version, Darstellung, Sicherung und Rettung | Status und bestehende Maintenance-/Rescue-Seite |

Das sind Navigationsgruppen, keine neuen Anwendungen oder Speicher.
Alte Links, `#ps-all` und gespeicherte Ansichtspräferenzen werden kompatibel zugeordnet.
Keine Funktion und kein ungespeicherter Entwurf darf verschwinden. Vorhandene
Ansichtsschlüssel bleiben gültig; neue Zonenansichten nutzen denselben Router.

## Ontologie: vier verschiedene Fragen nicht vermischen

1. **Wo physisch?** HA-Bereich und Etage, unverändert aus Home Assistant.
2. **Zu welcher Habituszone?** Explizite logische Mitgliedschaft, gegebenenfalls geteilt.
3. **Welche Funktion?** Rohquelle, Boolean, Nachlauf, öffentlicher Sensor, Schreiber
   oder Verbraucher; nicht aus einem hübschen Namen ableiten.
4. **Wo anzeigen?** Vorhandene Habitusrollen Übersicht, Bedienung, Status,
   Konfiguration und Diagnose sowie der Zonenanker „Habitus Zone“.

Habituszonen trennt Alltag, Konfiguration und Diagnose bereits sinnvoll. Diese
Ordnung übernehmen, nicht jede historische Karte oder Steuerungsannahme kopieren.
Themencluster sind keine neuen HA-Labels und ändern keine HA-Topologie.

## Ein alltäglicher Zonenweg

Zonenliste → aktuelle Zone → **Übersicht**, **Einrichtung**, **Automationen** oder
**Verlauf & Diagnose**. Wenige konsistente Ansichten statt weiterer Startseiten.

Die erste Ansicht zeigt Anwesenheit, Herkunft, kurzen Grund, Nachlauf und Datenlücke.
Bei ausdrücklich verbundener Bestandskette ist der öffentliche HA-Sensor der sichtbare
Bestandsstatus; die unabhängige PilotSuite-Bewertung wird als Vergleich ausgewiesen.
Ohne solche Verbindung steht die eigene Berechnung mit getrenntem Publikationsstatus
da; ohne bestätigtes eigenes Paket wird keine HA-Veröffentlichung behauptet.
Ein unklarer öffentlicher Sensor wird niemals durch einen gültigen Boolean oder eine
abweichende Berechnung kaschiert. Alpha.70 setzt diese Zielordnung um; bis Alpha.69
stand die eigene Zoneninstanz zuerst. Kein Wechsel der Steuerungsverantwortung.
„Frei gemeldet“ bezeichnet den ausgelesenen HA-Zustand, keinen unabhängigen Nachweis
physischer Abwesenheit. Eine pausierte PilotSuite-Bewertung pausiert nicht Home Assistant.

„PilotSuite-Belege“ öffnet die eigenen Quellen; der Sitzungsverlauf bleibt getrennt
erreichbar. Diese Belege erklären nicht automatisch die HA-Automation. Datenlücken bleiben
bereits in der Zusammenfassung sichtbar. Sitzungstrace und Recorder-Verlauf werden
klar benannt. Ein nicht angelegter Ausgang ist kein Fehler der Präsenzberechnung.
Interner Boolean und öffentlicher Binärsensor sind verschiedene Darstellungen,
keine zwei frei konfigurierbaren Anwesenheitsmodelle.

Einrichtung zeigt eine kurze Zusammenfassung mit gezieltem „Ändern“ pro Baustein:
Zone/Bereiche, Quellen, bestehende Anwesenheitskette und tatsächlich wirksame Zeiten.
Zustände heißen beispielsweise „nicht zugeordnet“, „verbunden“, „nicht verfügbar“
oder „Prüfung offen“, nie unbelegte Fertigstellungsprozente. Nicht jede Zone braucht
jeden optionalen Helfer. Erst notwendige Lücken bearbeiten, keine Pflicht-Lernfreigabe.

## Automationen gehören zur Zone

Eigener Bereich mit **Anwesenheit**, **Licht** und **Weitere**. Zunächst ausdrücklich
zuordnen; nachvollziehbare Inspector-Bezüge können später Vorschläge begründen.
Keine Zuordnung allein aus Namen, Bereichen oder einer bloßen Namensähnlichkeit.
Eine Automation kann mehreren Themen oder Zonen dienen und bleibt dasselbe Objekt.
Geteilte Verwendung muss vor Änderung sichtbar sein; keine Kopien pro Zone.

Jeder Eintrag unterscheidet:

- **Zuordnung:** gespeichert oder noch Entwurf; Thema und betroffene Zone.
- **Aktivierung:** HA-Meldung mit Datenstand, getrennt von Register-Deaktivierung.
- **Aufgabe:** Schreiber, Verbraucher, gemischt oder ungeklärt, mit konkretem Bezug.
- **Prüfung:** nicht geprüft, strukturelle Hinweise oder offene Verhaltensprüfung.

Statische Analyse bestätigt keine korrekte Laufzeit. Quellen, Bedingungen, Fristen,
manuelle Eingriffe, Neustart, unbekannte Eingänge und konkurrierende Schreiber gehören
in die Prüfung. Globale Konfigurationsabfragen bleiben ausdrücklich ausgelöst und
begrenzt; normales Navigieren startet weder Scans noch Schreibaktionen.

## Helfer: erst wiederverwenden, nur Fehlendes ergänzen

Der Nutzer sieht die zusammenhängende Kette:
**Sensoren → Anwesenheitsautomation mit Nachlauf → Boolean → öffentlicher Sensor → Verbraucher.**
Timer und Nachlauf-Dauer sind Parameter beziehungsweise Zustand dieser Logik, keine
zweite Anwesenheitsentscheidung. Eine vorhandene for:-Regel erzwingt keinen neuen Timer.

Pro notwendiger Funktion: vorhandenen Helfer wählen, fehlenden Helfer planen oder
„noch ungeklärt“ belassen. Vorhandene Bindungen und Identitätsprüfung weiterverwenden.
Namensbereinigung ist optional und vom Verbinden getrennt. Anzeigenamen zuerst;
technische Entity-ID nur mit belegter Verbrauchermigration, niemals still umbenennen.
Ein bestehender kanonischer Sensor darf keine neue _2-Ausgabe auslösen.

Jeder Änderungsplan zeigt Vorher/Nachher, betroffene Objekte und Verbraucher,
Steuerungsverantwortung, Prüfgrenzen und konkreten Rückweg. Bestätigte Teilstände
bleiben sichtbar; verlorene Antworten rechtfertigen kein blindes Wiederholen.
Die fünf Sicherheitsbausteine eigener Ausgaben bleiben erhalten. Ein vorhandener
Teilbestand ist kein Anlass, ein ganzes Parallelpaket anzulegen.

Alpha.70 trennt deshalb den direkten Bestands-Einstieg von der
aufklappbaren Option eines **vollständigen eigenen** Ausgangspakets. Dessen Vorschau
erklärt jeden Baustein, unveränderte Bestandszuordnung, ausgeschaltete Veröffentlichung
und den begrenzten Rückweg: keine automatische Löschung angelegter Helfer. Die Option
ist ausdrücklich keine Reparatur eines einzelnen fehlenden Bestandshelfers. Auch eine
fehlgeschlagene Vorschau bleibt schließbar; keine Sackgasse oder blinde Wiederholung.

Alpha.71 ergänzt innerhalb derselben Helferoptionen einen fokussierten Rollen-/Dauer-
Entwurf und eine konkrete Einzelvorschau. Ohne eigene Präsenzkonfiguration nutzbar;
vorhandene oder unaufgelöste Zuordnungen sperren einen vermeintlichen Ersatz.
Erfolg heißt „Helferanlage bestätigt · Anschluss noch offen“, nicht „Zone fertig“.
Technische ID, unveränderte Steuerung und begrenzter Rückweg bleiben sichtbar.
Ein Fehler erhält die Dauer; Historie zeigt Anlagepläne ohne Namens-Apply/Rücknahme.
Synthetisch geprüft: andersartige Zone ohne Präsenzkonfiguration, Rollenfokus,
240-Sekunden-Entwurf, Vorschau/Bestätigung, keine Bindung/Steuerung, Kollisionsfehler
mit erhaltenem Entwurf; 390/768/1440 px in Hell/Dunkel. Keine Haushaltsabnahme.

Ein Nachlauffeld nennt ausdrücklich seinen Besitzer: **HA-Bestandsautomation** oder
**PilotSuite-Vergleich**. Nur ausgelesene, eindeutig unterstützte HA-Parameter dürfen
als direkt editierbar erscheinen. Unbekannte Templates/Blueprints bleiben begründete
Prüfgrenzen; keine scheinbar wirksame Spiegelkonfiguration.

## Direkte Einrichtung

Alpha.68 bietet vier direkte Aufgaben: Anwesenheit/Nachlauf, Lichtquellen,
Entitäten sowie Name/Bereiche. Sie öffnen die vorhandenen Editoren derselben Zone,
keine zweite Konfiguration. Lichtquellen sind Zuordnungen, keine Schaltknöpfe.
Offene Entwürfe blockieren auch diese Einstiege; fehlende Bereitschaft wird erklärt.
Das gewünschte sichtbare Feld erhält Fokus. Ein Quellenfilter darf den Fokus nicht
auf eine ausgeblendete andere Rolle lenken. Automatische Aktualisierung öffnet
keinen Editor und verschiebt keinen Fokus. Der Hauptsensor-Link führt in die
Konfiguration, nicht in die Lernwerkbank.

## Diagnose ohne konkurrierende Wahrheiten

Synthetisches Replay, alter expliziter Schattenvergleich und technische IDs gehören
unter benannte Diagnose-Details. Strukturprüfung gehört zur betreffenden Automation,
globale Bereinigung zu Werkzeugen. Alle bestehenden Funktionen bleiben erreichbar,
starten nicht durch Navigation und überschreiben keinen Live-Status.
Lichtvorschau ist als Vorschau gekennzeichnet. Der Prüfkompass bleibt Bestandteil
der Routinewerkbank, keine weitere Startseite.

Habituszonen liefert die Trennung von Übersicht, Bedienung, Status, Konfiguration
und Diagnose. Seine pauschale Gleichsetzung „nicht on = Ruhe“ wird nicht übernommen.
Alte Lernhinweise aus der Basis-Einrichtung entfernen, ohne gespeicherte Lernzustände
zu verändern. Die ausdrücklich benannte Legacy-Werkbank erklärt ihre eigenen noch
notwendigen Schalter. Kein Lernangebot als vermeintlich notwendiger Einrichtungsschritt.

## Primärquellen und konkrete Entscheidungen

Gezielte Recherche vom 29.09.2026; keine Behauptung eines universell optimalen UI.
Die folgenden Übertragungen auf PilotSuite sind eigene Designentscheidungen:

- [GOV.UK Aufgabenlisten](https://design-system.service.gov.uk/components/task-list/):
  erst vereinfachen, dann Aufgaben strukturieren. Daher kurze Einrichtung mit klaren
  Zuständen; kein langer Pflichtassistent und kein Gesamt-Fortschrittsprozentsatz.
- [GOV.UK Zusammenfassung vor Bestätigung](https://design-system.service.gov.uk/patterns/check-answers/):
  Änderungen gezielt korrigieren und vorhandene Eingaben erhalten. Auf unsere
  revisionsgebundenen Vorher-/Nachherpläne übertragen, nicht als zweiter Speicher.
- [W3C redundante Eingaben](https://www.w3.org/WAI/WCAG22/Understanding/redundant-entry.html):
  schon bekannte Angaben wieder anbieten. Vorhandene Zuordnungen bleiben ausgewählt,
  auch nach Filtern, Validierungsfehlern und Rückkehr zur Bearbeitung.
- [WAI-ARIA Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/):
  Tabs benötigen eigene Tastatur-/Fokussemantik. Unsere Seitenwechsel bleiben normale
  benannte Navigationslinks mit aria-current; nicht bloß role=tab ergänzen.
- [HA Entity Registry](https://developers.home-assistant.io/docs/entity_registry_index/):
  stabile Identität und sichtbarer Name sind verschieden. Bestehende Registry-Schlüssel
  weiterverwenden, Namen nicht zu Identitäts- oder Eigentumsbeweisen machen.
- [HA Labels](https://www.home-assistant.io/docs/organizing/labels/):
  unabhängig vom Ort gruppierbar, aber auch Ausführungsziele. Daher Metadatenänderungen
  konkret prüfen; UI-Themencluster benötigen keine neuen Labels.
- [HA Automations-Traces](https://www.home-assistant.io/docs/automation/troubleshooting/):
  tatsächlicher Pfad ist etwas anderes als „Aktionen ausführen“, das Auslöser und
  Bedingungen überspringt. Keine Haushalt-Testschaltung als Abnahmekürzel.
- [HA Timer](https://www.home-assistant.io/integrations/timer/) und
  [for:-Auslöser](https://www.home-assistant.io/docs/automation/trigger/):
  idle ist kein Ablaufnachweis; verpasste Timer-Endereignisse werden nicht nachgeholt,
  for:-Wartezeiten überstehen Neustart/Automationsneuladen nicht. Im Bestandsreview
  sichtbar machen, nicht durch einen neuen UI-Zeitwert vermeintlich reparieren.

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
