# Habituszonen als Grundlage — Arbeitsauftrag 30.09.2026

**Abgeschlossenes Umsetzungspaket.** Nach Alpha.72 hat der Nutzer den nächsten
Umfang auf reine Zonenerstellung, Darstellung und Dokumentation begrenzt.
Vergleiche und weitere Module sollen ausgeblendet werden. Dafür gilt jetzt
[HABITUS_FOUNDATION_RESET.md](HABITUS_FOUNDATION_RESET.md) / ADR-044; die folgende
Chronik bleibt als Nachweis erhalten und ist kein Auftrag zum weiteren Modulausbau.

Zeitfenster: bis 08:00 Europe/Berlin (06:00 UTC). Diese neue ausdrückliche
Beauftragung ersetzt die abgelaufenen Zeitfenster, nicht historische Release-Belege.
Arbeitsbranch: `feat/habitus-zone-setup`, Ausgang `e3e5dc2` / installierte Alpha.71.

## Fortsetzung nach Ende des Zeitfensters

Der Nutzer beauftragte am 30.09.2026 nach 08:00 mit „weiter“ die direkte Fortsetzung
im bestehenden Chat. Der abgelaufene Heartbeat ist PAUSED; kein neuer Zeitlauf.
Die folgenden Zeitgrenzen dokumentieren den beendeten Nachtauftrag. Bestehende
Haushalts- und Release-Grenzen gelten weiter; die offene Backup-Ausnahme ist nicht
beantwortet. Aktueller Arbeitsstand: CURRENT_STATE.md, exakte CI-Belege in PR #153.

## Auslieferungsabschluss

Mit „Bitte abschließen“ beauftragte der Nutzer den Abschluss nach Benennung der
lokalen Backup-Ausnahme. PR #153 ist gemergt, Alpha.72 installiert und gesund.
Exakte Kandidaten-/Main-CI: 36687732779 / 36690038477, alle fünf Jobs grün.
Frische PilotSuite-only-Sicherung e636bd76; Synology-Listenfehler ausdrücklich als
enge Ausnahme dokumentiert, ohne NAS-Konfigurationsänderung. Ein Store-Refresh,
ein gezieltes Update, vier Optionen/Betriebsmodus unverändert. Verbindlicher Beleg:
[RELEASE_STATE.json](RELEASE_STATE.json). Die folgende Chronik bewahrt frühere
Zwischenstände; fehlende Haushaltsabnahme und aktive Lichtausführung bleiben offen.

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

Weitere Fortsetzung: Rückkopplungsschutz auf `351283e` mit fünf grünen CI-Jobs
(`36665786791`). Im gespeicherten Zoneneditor sechs Bedienlücken zuerst im Browser
rot reproduziert: feste Labelbindung blieb wechselbar, fehlende Labelkennung und
Ursache verschwanden, Speicherkonflikte verloren ihren Grund, laufender Import ließ
eine andere Auswahl zu. Der bestehende Editor zeigt Bindung/fehlendes Label und
Konfliktursache, erhält den Entwurf und sperrt die Auswahl nur passend zum Zustand.
Kein neuer Store oder HA-Schreibweg. Logs `/private/tmp/habitus-label-guidance-*`;
Erweiterter Zonenbrowser, 78 JS-Tests und 68 Verträge grün; tatsächliche Handy-/
Desktop-Screenshots angesehen. Abschluss-CI im bestehenden PR. Ein alter Browser-Wartepunkt wurde auf den tatsächlichen
Wechsel zur neu gespeicherten Zone präzisiert, statt schon die vorige Zone zu akzeptieren.

Weitere Fortsetzung: Labelbedienung auf `b9b2772`, alle fünf CI-Jobs in `36666545782`
grün. Gespeicherte Mitglieder erhalten nun eine lesende Identitätsanzeige über den
vorhandenen Organization-Resolver: unverändert, umbenannt, deaktiviert oder ungeklärt.
Struktur/Relevanz werden beim Öffnen aus dem bestehenden Speicher gelesen; abweichende
Revisionen öffnen keinen vermischten Entwurf. Keine automatische Umbindung, Migration
oder Ersatzanlage. Sechs API-Fälle zunächst rot, danach 718 Python/78 JS-Tests,
68 Verträge, Auswahl- und Zonenbrowser grün. Tatsächliche Handy-/Desktop-Screenshots
unter `/private/tmp/habitus-member-identity-ui`, Logs `/private/tmp/habitus-member-*`.
Ein zusätzlicher Browserfall verhinderte das erneute Freigeben einer mehrdeutigen
Identität nach Tag-Import; rot reproduziert und im bestehenden Editor korrigiert.
Python-Abschluss mit Garbage Collection ohne ResourceWarnings. Exakte CI im PR.

[Zonenlabel](screenshots/habitus-setup-alpha72/zone-new-label-light-390.png),
[Einrichtung](screenshots/habitus-setup-alpha72/foundation-390.png),
[Lichteditor](screenshots/habitus-setup-alpha72/zone-lighting-editor-390.png),
[Lichtvergleich](screenshots/habitus-setup-alpha72/zone-lighting-comparison.png).

Weitere Fortsetzung: Mitgliedsidentitäten auf `5b59d4c`, alle fünf CI-Jobs in
`36667558353` grün. Ergänzte Lichtdiagnose erklärt die bereits vorhandenen Lux-
Gültigkeitsgrenzen und zeigt manuelle Sperrsensoren mit Namen und Zustand. Neun
Fälle zunächst rot, anschließend 719 Python-/78 JS-Tests, 68 Verträge und der
Zonenbrowser grün. Unbekannte Eingänge erzeugen keinen Vorschlag; nach Rückkehr
muss die Stabilität neu entstehen. Offene Details und Tastaturfokus bleiben beim
Nachladen erhalten. Keine Änderung an Policy, Store oder Schaltrechten.
Logs `/private/tmp/habitus-light-diagnostics-*`, tatsächlich angesehene Bilder
unter `/private/tmp/habitus-light-diagnostics-ui/`. Zwei Browser-Wartepunkte wurden
an bestätigte Antwort bzw. beendetes Nachladen gebunden, ohne feste Wartezeiten.
Abschluss-CI wieder am exakten neuen Kandidaten prüfen; keine Auslieferung behaupten.

Manuelle Fortsetzung nach 08:00: Der Lichtdiagnose-Kandidat `8a48e8d` bestand
alle fünf CI-Jobs (`36668689077`). Der abgelaufene Heartbeat ist bestätigt pausiert.
Im Präsenzeditor wurden verschwundene gespeicherte Quellen bislang nicht angezeigt;
neues Speichern konnte sie dadurch still entfernen. Fehlende Quellen bleiben jetzt
sichtbar, bis sie ausdrücklich entfernt oder im Bestand geklärt werden. Leere
Auswahl und reine Nutzungsindizien erklären die fehlende direkte Quelle vor dem
Speichern. Beide Fälle rot reproduziert; der Test benennt nach Reload ausdrücklich
die betroffene Zone. Gesamter Zonenbrowser, 78 JS-Tests und 68 Verträge grün; keine
Python-Änderung. Abbrechen erhält die vollständige Quellenspezifikation und alle
geprüften Schreibzähler. Angesehene Screenshots unter
`/private/tmp/habitus-incomplete-presence-ui/`, Logs `/private/tmp/habitus-*-presence-*`.
Beide Skills gepflegt/validiert. Exakte Folge-CI im PR; keine Auslieferung behaupten.

## Übergabepunkte für die Fortsetzung

- Ausgelieferter Stand und exakte CI: PR #153, RELEASE_STATE.json und CURRENT_STATE.md.
  Lokale/Connector-Commit-IDs unterscheiden sich bei gleichem geprüftem Quellbaum.
  Alpha.72 ist installiert; nicht erneut updaten. AGENTS.md unverändert lassen.
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
- Kein authentifizierter Haushaltsbrowser beobachtet. Den tatsächlichen App-Stand
  vor Auslieferung nativ neu lesen; keine Installation aus diesem Übergabetext ableiten.
