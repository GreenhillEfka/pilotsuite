# Habituszonen als Grundlage — Arbeitsauftrag 30.09.2026

Zeitfenster: bis 08:00 Europe/Berlin (06:00 UTC). Diese neue ausdrückliche
Beauftragung ersetzt die abgelaufenen Zeitfenster, nicht historische Release-Belege.
Arbeitsbranch: `feat/habitus-zone-setup`, Ausgang `e3e5dc2` / installierte Alpha.71.

## Ziel und Reihenfolge

1. Zonenerstellung aus physischen HA-Bereichen und vorhandenen Zonenlabels in
   einem verständlichen Editor. Geräte-Labels zählen mit ihren Entitäten;
   Mitgliedschaft, Relevanz und Steuerrecht bleiben unterschiedliche Eigenschaften.
2. Persistente Verbindung zum Zonenlabel, Habitus-Rollen und stabilen Identitäten
   im bestehenden SQLite-Zonenmodell. HA bleibt Eigentümer seiner Registry.
   Manueller Bestand wird importiert, Änderungen werden vor dem Abgleich gezeigt.
3. Präsenzmodul: bestehende Ketten verbinden oder notwendige eigene Helfer/Sensoren
   zusammenhängend planen, erstellen und automatisch labeln. Vorhandene Transaktion,
   Rücklesen und Gültigkeit verwenden; keine parallele Präsenzentscheidung.
4. Lichtmodul auf der geklärten Präsenz, vorhandenen Lichtquellen und manueller
   Übersteuerung. Eindeutiger Besitzer; unbekannter Zustand ist kein Ausschaltgrund.
5. Einrichtungsweg und Skills vereinfachen. Klima, Multimedia und Mustererkennung
   erst nach dieser Grundkonfiguration; alte Daten und Werkzeuge bleiben erreichbar.

## Bedienvertrag

Bereits ausgewählte Dinge nicht erneut abfragen. Normales Speichern einer
Zuordnung braucht keinen zusätzlichen Bestätigungsdialog. HA-wirksame Änderungen
erhalten eine gemeinsame konkrete Vorschau statt einer Freigabe pro Helfer.
Speichern aktiviert weder Lernen noch Veröffentlichung noch eine Lichtsteuerung.
Vorhandene HA-Steuerungen und physische Orte bleiben erhalten. Technische IDs sind
kein aufzuräumender Anzeigename. Abweichungen und unvollständige Teilergebnisse
werden sichtbar; kein blindes gegenseitiges Überschreiben.

## Abnahme und Zeitgrenzen

Ein aktives Umsetzungspaket, bestehende Unit/API/Browser/Protokolltests erweitern.
Vier gespeicherte Zonen, fremde Labels und ungespeicherte Eingaben erhalten.
Synthetische Prüfung ist keine Haushaltsabnahme. Keine Haushalt-Testschaltungen.
Neue Funktionspakete enden ab 07:20, neue Veröffentlichung ab 07:30 Ortszeit.
Um 08:00 gesicherten Stand und verbleibende Grenzen berichten; keine Verlängerung.
Jede Auslieferung folgt dem vorhandenen Release-Runbook; dessen Installation und
die konkrete Übernahme einer Haushaltssteuerung sind getrennte Schritte.

## Laufender Stand

- Lokal implementiert: Label-/Geräteimport, atomare Speicherung mit Identitäten,
  Rollen und Relevanz; alte API-Aufrufer unverändert. Labelabgleich als gemeinsamer
  Vorher-/Nachherplan im vorhandenen Ontologiepfad, mit Rücklesen und Rücknahme.
- Label-/Import-Paket: vollständige 661 Python- und 78 JS-Tests sowie 66 API-Verträge
  bestanden. Erweiterter Browser einschließlich Batch-Abgleich und Rücknahme grün.
  Mobile Screenshot-Prüfung führte zum Ausblenden konkurrierender Formulare.
- Anschließend implementiert: Namen und Autolabeling als Teil des vorhandenen
  Helferplans, kumulative Metadatenbelege und Wiederanlauf ohne Doppelanlage;
  neue eigene Ausgangsmitglieder werden atomar in die Zonenstruktur aufgenommen.
  88 Zonentests grün; vollständiger Folgecheck mit 665 Python-Tests bestanden,
  erweiterter Browserablauf ebenfalls grün. 78 JS-Tests und 66 API-Verträge grün.
  Screenshots mobil/hell tatsächlich angesehen; Theme-Übergänge werden in den
  Prüfbildern durch reduzierte Bewegung vermieden.
- Skills home-assistant-struktur und pilotsuite-quality-release aktualisiert und
  quick_validate erfolgreich. Keine HA-Schreiboperation/Installation erfolgt.
- Zweiter lokaler Schritt: neue Zonenlabels samt Mitgliedslabels in einem Plan;
  atomare Bindung der tatsächlich von HA zurückgegebenen Label-ID. Kein Raten der
  ID und keine erneute Anlage bei verlorener Antwort. Mit Beleg ist Wiederanlauf
  möglich; ohne Beleg muss vorhandener Bestand ausdrücklich gewählt werden.
  Bereiche/Zusatzentitäten lassen sich im selben Editor als Mitglieder vorschlagen.
- Neue Regressionen reproduzierten zunächst fehlende Anker-/Rollenprüfungen beim
  Apply sowie übersehene manuelle Änderungen während der Helferanlage. Korrigiert:
  frisches Geräte-/Entitätsregister, zonenübergreifende Rollen, finale Metadatenprüfung.
  Keine atomare HA-Registry-Sperre behauptet; Konflikte und Teilstände bleiben sichtbar.
- Aktuell 679 Python-Tests, 78 JS-Tests, 67 API-Verträge grün. Alle elf vorhandenen
  Browser-Suiten bestanden (Auswahltest mit NODE_PATH erneut grün). Der neue Verlauf
  für Metadatenpläne besteht zusätzlich den erweiterten Zonenbrowser und den
  erneut ausgeführten Organisationsbrowser.
  Sieben native Protokollszenarien gegen lokale wegwerfbare HA 2026.9.3 bestanden,
  einschließlich neuer Labelanlage, Bindung, Wiederholungsschutz und Rücknahme.
  Handy-Screenshots des neuen Formulars in Hell und Dunkel angesehen.
- Präsenz-Einrichtungsweg lokal vollständig verbunden: sichtbare Schritte, direkte
  Einstiege in bestehende Editoren, passende Quellen vorbefüllt. Bestandszuordnungen
  werden nur für leere Funktionen vorgeschlagen und erst durch Speichern übernommen.
  Publikationswirkung samt tatsächlichem eigenem Ziel steht direkt im Formular.
  Deaktivierter Bestandsanker verhindert weiterhin Ersatzanlage. 685 Python-/78 JS-
  Tests, 67 Verträge und vier betroffene Browser grün; neue Screenshots angesehen.
- Lichtvergleich lokal verbunden: vorhandene Policy, dieselbe Zonenpräsenz und
  derselbe Tick/Checkpoint. Einstellbare Luxherkunft, Stimmung, Grenzen, Stabilität
  und Bedienpause; kein neuer Präsenzkern. Neustart erhält Mindestabstand,
  Quellenkonflikte bleiben bis zur expliziten Prüfung ausgesetzt. 704 Python,
  78 JS und 68 Verträge grün; erweiterter Zonenbrowser und sieben native HA-Fälle grün.
  Aktive Lichtausführung/Automationsübernahme bleibt offen; es existiert weiterhin
  kein Leuchten-Schreibpfad. Alle elf Browser-Suiten und die Ressourcenprüfung
  sind grün. Das Komponentenskript hat abweichend keinen `_browser`-Suffix;
  der erste Sammelaufruf wurde entsprechend korrigiert.
  Eigenes Diff-Review ergänzte einen rot/grün belegten Schutz für reine Farb- und
  Effektwechsel (HS/XY/RGBW/RGBWW/Effekt/Mireds), die ebenfalls die Bedienpause starten.
  Zusätzlich: ältere Teil-Speicherpunkte dürfen neue Zonen-/Präsenz-/Lichtparameter
  und Ausgangsbindungen nicht entfernen. Vorschau und Restore-Transaktion prüfen
  den tatsächlichen Umfang; vollständiger Rückweg bleibt die native App-Sicherung.
  Drei fehlende Umfangsschutzfälle zunächst rot; Gesamtsuite und Wartungsbrowser grün.
- Nächster Schritt: vollständige Gates/Review, Version und sichere Auslieferung
  nach Runbook. Alpha.72 lokal vorbereitet, keine Veröffentlichung/Installation.
  Frische Sicherung `63f11346` enthält bestätigt nur PilotSuite Alpha.71 lokal;
  `backup/details` meldet jedoch Lesefehler zweier weiterer Synology-Agenten.
  Die verlangte leere `agent_errors`-Liste ist damit nicht bestätigt. Kein blindes
  erneutes Backup, keine Änderung der fremden Speicherorte oder stiller Gate-Verzicht.
  Entwurfs-PR #153 ist gesichert; GitHub-Connector statt nicht angemeldetem CLI-Push.
  Lokale Commits bleiben erhalten, der gefetchte Kandidatenbaum wurde identisch
  geprüft. CI immer auf den neuesten Connector-Kandidaten beziehen; Main unverändert.
- Fortsetzung: Kandidat `4fc9808` bestand alle fünf CI-Jobs; finaler Python-
  Ressourcencheck mit 704 Tests und Garbage Collection ohne ResourceWarnings.
  Der weitere Bedienreview fand einen zu breiten Label-Filter: Namen wie
  „Habitus Demobereich“ dürfen nicht zusammen mit den sechs Rollen ausgeblendet
  werden. Im bestehenden Browserablauf rot reproduziert; Filter auf exakte
  Rollenmitgliedschaft begrenzt. Vollständiger Zonenbrowser und 68 Verträge grün,
  tatsächlicher Handy-Screenshot geprüft. Neue Kandidaten-CI bleibt erforderlich.
- Kandidat `c8f37e4` bestand danach alle fünf CI-Jobs. Die reine HA-Bestandsprüfung
  bestätigte gekoppelte Anwesenheits-/Lichtverantwortung; private Daten liegen nur
  unter ignoriertem `pilot_data/reviews/`, keine Live-Zuordnung oder Steuerung geändert.
  Der anschließende Gruppenreview reproduzierte acht fehlschlagende Fälle:
  Gruppen/Mitglieder dürfen nicht doppelt geplant werden, unaufgelöste Mitglieder
  und geänderte Identitäten sind keine verlässliche Vergleichsbasis. Der vorhandene
  Lichtadapter berücksichtigt jetzt bekannte Mitglieder auch für die Bedienpause.
  711 Python-/78 JS-Tests und 68 Verträge sowie der erweiterte Zonenbrowser grün;
  kein ResourceWarning nach Gesamtsuite und Garbage Collection. Exakte neue CI folgt.

Synthetische UI-Belege, keine Haushaltsbilder:
Weitere Prüfung 05:15 Ortszeit: Der Gruppen-Kandidat `7869be3` bestand alle fünf
CI-Jobs (`36662483135`). Anschließend wurde eine Sackgasse bei pausierten Zonen
korrigiert: Ganzzonenpause und Präsenzmodulpause besitzen passende nächste Schritte.
Der neue Link fokussiert nur die bestehende Startaktion; er startet keine Auswertung
und ändert keine Betriebsart. Eine gespeicherte Veröffentlichung wird ausdrücklich
benannt. Vier Unit-Fälle zunächst rot, anschließend 713 Python-/78 JS-Tests und
68 Verträge grün; Zonenbrowser prüft Tastatur, keine Schreibaktion und erhaltene
Konfiguration. Logs: `/private/tmp/habitus-paused-full-tests.log` und
`/private/tmp/habitus-paused-browser-green.log`. Neue exakte Kandidaten-CI folgt.

Fortsetzung: Pausen-Navigation `a653cc3` mit fünf grünen CI-Jobs (`36663683536`).
Erneutes Einlesen von Label-/Bereichsmitgliedern setzte zuvor explizite Abwahlen
zurück; beide Browserfälle zunächst rot reproduziert. Auswahl und Rollen bleiben
nun erhalten. Fehlende Labelmitgliedschaft und HA-/Entwurfsrollen werden benannt;
neue Kandidaten erhalten keine Analysefreigabe. Lesefehler erhalten den Entwurf.
Erweiterter Zonenbrowser und 713 Python-/78 JS-Tests/68 Verträge grün. Screenshots
mobil/dunkel und Desktop angesehen. Logs: `/private/tmp/habitus-tag-refresh-*`.
Kein neuer Speicher, automatischer HA-Scan oder Metadaten-Schreibpfad. Exakte neue
CI folgt im bestehenden PR; keine Auslieferung oder Haushaltsänderung.

Weitere Fortsetzung: Import-Kandidat `6ed081f` mit fünf grünen CI-Jobs
(`36664522982`). Der ältere Relevanzweg konnte danach einen gespeicherten Anker als
Präsenzquelle wieder einführen. Neun Unit-/API-Fälle zunächst rot: Zonenanker vor
Bestandsbindung, Umbenennung, Mehrdeutigkeit/Ersetzung, direktes und unterstützendes
Signal sowie automatischer Quellenvorschlag. Die bestehende Eingangsvalidierung
bezieht nun alle bekannten Ausgänge ein. Laufzeit und Wiederanlauf bleiben bei
Altfehlern unklar; nur der Statusvergleich ist weiterhin erlaubt. Der Editor erklärt
die konkrete Quellenkorrektur und bewahrt die gespeicherte Konfiguration bei Abbruch.
717 Python-/78 JS-Tests/68 Verträge und erweiterter Zonenbrowser grün; Handy-/Desktop-
Screenshots angesehen. Logs `/private/tmp/habitus-anchor-*`. Neue exakte CI folgt.

[Zonenlabel](screenshots/habitus-setup-alpha72/zone-new-label-light-390.png),
[Einrichtung](screenshots/habitus-setup-alpha72/foundation-390.png),
[Lichteditor](screenshots/habitus-setup-alpha72/zone-lighting-editor-390.png),
[Lichtvergleich](screenshots/habitus-setup-alpha72/zone-lighting-comparison.png).

## Übergabepunkte für die Fortsetzung

- Lokaler geprüfter erster Commit: `04425ae`. Nicht veröffentlicht; App-Version
  noch nicht angehoben. Untracked AGENTS.md unverändert lassen.
- Python: `/private/tmp/pilotsuite-test-env.saaFlP/bin/python`, `PYTHONPATH=pilotsuite`.
  Browserbibliothek: `/Users/andreas/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright`.
  `PLAYWRIGHT_BROWSERS_PATH=/private/tmp/pilotsuite-browsers`; `PYTHON` wie oben.
  Beim älteren Auswahlbrowser zusätzlich `NODE_PATH` auf das parent node_modules.
- Native HA-Protokollumgebung: `/private/tmp/pilotsuite-ha-protocol-env/bin/python`
  als `HA_PROTOCOL_PYTHON`; Runner bleibt der PilotSuite-Test-Python. Log:
  `/private/tmp/habitus-native-protocol.log`. Keine Haushaltszugangsdaten.
  Vorhandene Browser-Skripte benötigen einen lokalen Testserver, daher die
  normale Sandbox-Freigabe für isolierte Tests verwenden.
- Bisherige Logs: `/private/tmp/habitus-full-tests.log`,
  `/private/tmp/habitus-js-tests.log`, `/private/tmp/habitus-setup-browser.log`.
  Synthetische Screenshots: `/private/tmp/habitus-setup-ui/`.
- Kein authentifizierter Haushaltsbrowser beobachtet. Die HA-App-Metadaten wurden
  frisch geprüft: Alpha.71 gestartet, kein Update angeboten. Keine Live-Applys.
