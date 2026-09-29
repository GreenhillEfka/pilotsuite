# Zoneninstanz, Relevanz und Ontologie — Alpha.49 mit Alpha.50-Wiederanlauf

## Historischer Ausgangspunkt (Alpha.50)

Kanonisch: GreenhillEfka/pilotsuite, App 0d79c5e8_pilotsuite. Alpha.50 ist aus
`9aea467a81fcdbd9fc96a0199cb2a1c57826702b` veröffentlicht und installiert; exakte
Kandidaten-/Main-CI, wegwerfbares HA-Protokoll und App-Startprüfung wurden im
damaligen Release-Receipt belegt. Die Wiederanlauflogik erweitert keine Ausführungs-
oder Lernberechtigung.
Den aktuellen Installationsstand weist `docs/RELEASE_STATE.json` aus.

Das echte Storage-Dashboard „Habituszonen“ wurde gelesen. Seine Struktur dient als
fachliche Referenz, nicht als unfehlbare Steuerungslogik. Keine Dashboard-Konfiguration,
privaten Gerätekennungen oder HomeKit-Daten wurden in diesen Quellcode übernommen.

## Zielordnung aus dem Dashboard

Physischer Floor/Area bleibt physisch. Ein Zonenlabel beschreibt logische Mitgliedschaft.
Die Fachart folgt Domain und Device Class, nicht redundanten Funktionslabels. Die sechs
Rollen sind Habitus Zone, Habitus Übersicht, Habitus Bedienung, Habitus Status,
Habitus Konfiguration und Habitus Diagnose. Eine Entity kann begründet mehrere Rollen
haben; ein Zonenanker ist ein semantischer Anwesenheits-Binärsensor. Alltag, Konfiguration
und Diagnose bleiben getrennt. Bestehende unbekannt/off-Vereinfachungen des Dashboards
werden in neuen Diagrammen nicht übernommen. Das Dashboard selbst blieb unverändert.

## Relevanz und Daten

Die neue Präsenz-/Datenstrecke benötigt KEINE separate Lern-, Kontext- oder
Historienzustimmung. Relevante Quellen einer aktiven Zone werden sofort interpretiert.
Eine explizite Pause bleibt eine Laufzeitfunktion, keine Datenfreigabe. Historische
Recorder-Zustände werden automatisch zunächst für 24 Stunden in 40er-Paketen gelesen;
maximal ein Paket je Hintergrundschritt, Wiederholung nach 15 Minuten, Fehler-Backoff.
Manuell gewählte ältere Intervalle bis 31 Tage pro Anfrage benötigen keine neue Freigabe.
Es wird nicht behauptet, die gesamte verfügbare Vergangenheit bereits importiert oder
ausgewertet zu haben. Nicht aufgezeichnete Event-Bus-Ereignisse lassen sich nicht
rekonstruieren; die Historienansicht ist eine Zustands-/Messwertanalyse.

Live-Kern und Historienabfragen laufen getrennt. Ein alter Datensatz kann keinen heutigen
Nachlauf starten. Quellenidentität/Relevanz/Revision werden vor und nach I/O geprüft;
unangeforderte Daten werden verworfen. Die Anzeige ist zeitlich begrenzt, keine zweite
Recorder-Datenbank. Akzeptierte direkte Aktivitätsbelege verwenden den vorhandenen
begrenzten Aktivitätsspeicher; dessen bestehende Aufbewahrung bleibt wirksam.
Ältere Analyse-APIs und deren gespeicherte Legacy-Lernfelder bleiben abwärtskompatibel;
sie sperren diesen neuen Pfad nicht. Dies ist keine vollständige Migration jedes alten
Lernalgorithmus auf TV-/Nutzungsmerkmale und kein neuer autonomer Komfortlerner.

## Präsenzsemantik

- Dauerpräsenz, Bewegungsimpuls und unterstützende Nutzung sind getrennte Signaltypen.
- Eine Quelle darf beginnen, nur halten oder lediglich ergänzen; entsprechende Eingriffe
  erfolgen über die Quelleneinstellungen, nicht über weitere Zustimmungsdialoge.
- Ein unverändert laufender TV startet beim Kaltstart keinen Aufenthalt. Die Haltewirkung
  endet an einer begrenzten, tatsächlich verankerten Frist; Polling verlängert sie nicht.
- Eigene bekannte Ereignisse dürfen keine neue Präsenz begründen. Der Publisher schaltet
  nur eigene Zustandshelfer, keine Mediengeräte. Automatische oder nicht zuordenbare
  TV-Bedienung ist nicht als bewiesene menschliche Bedienung deklariert.
- Ein positiver tragender Beleg darf einschalten. Zum Ausschalten müssen die vereinbarten
  erforderlichen Abdeckungsgruppen frei sein; optionale ausgefallene Indizien blockieren
  die Zone nicht. Redundanz wird ausdrücklich gruppiert, nicht aus Geräteähnlichkeit erraten.
- Gruppen und Mitglieder werden nicht doppelt verwendet. Abgeleitete Templates sind in
  diesem Paket nur Zusatzindizien; unabhängige Raumabdeckung wird nicht behauptet.
- Alpha.54 korrigiert die Gruppenauswertung: Eine `off`-Quelle beweist keine freie
  erforderliche Abdeckungsgruppe, solange eine andere erforderliche Quelle derselben
  Gruppe `unknown` oder `unavailable` ist. Ein positiver Beleg bleibt gültig;
  optionale unklare Indizien blockieren eine klare erforderliche Abdeckung nicht.
- Alpha.56 ergänzt die Mindestbeobachtung: Sind sämtliche direkten Quellen unklar,
  abgelaufen oder nicht verwertbar, ist auch bei ausschließlich optionalen Quellen
  keine Freimeldung belegt. Ein zuvor freier Zustand verliert dann seine Gültigkeit.
  Eine gültige direkte Beobachtung und die erforderlichen Abdeckungsgruppen bleiben
  maßgeblich; Quelleinstellungen und gespeicherte Fristen werden nicht migriert.
- Meldealter 0 bedeutet ereignisorientierter gehaltener HA-Zustand. Periodische Quellen
  können explizite Altersgrenzen haben. Datenalter ist kein physikalischer Genauigkeitswert.
- Frist, Generation und Gültigkeit stammen aus dem bestehenden Kernel. Neustarts erneuern
  Fristen nicht. Unklar wird nicht zu frei; die stabile Freiphase hat einen festen Beginn.

## Konfiguration speichern ohne unbeabsichtigten Neustart

Alpha.63 erhält bei identischer gespeicherter Konfiguration, Betriebsart und geprüfter
Quellenbasis die vorhandene Sitzung, Revision und Nachlauffrist. Revision, Relevanz,
Quellenidentität und Rückkopplungsschutz werden weiterhin geprüft. Der unveränderte
Aufruf schreibt keine Konfiguration, startet keinen zusätzlichen Zonenlauf und setzt
keinen eigenen Ausgang ungültig. Er erneuert weder Beobachtungen noch Rücklesenachweise;
veraltete oder getrennte Daten bleiben nicht beurteilbar.

Erstmaliges Speichern, echte Änderungen, alte parallel gespeicherte Schattenkonfigurationen
oder eine gesperrte Auswertung/Publikation durchlaufen weiterhin den vollständigen
Speicherpfad. Insbesondere bleibt erneutes bestätigtes Speichern die bewusste Wiederaufnahme
nach einer Sperre. Kein neuer Speicher, Scheduler oder HA-Schaltrecht; bestehende
Automationen und deren Nachlauf werden dadurch nicht verändert.

## Bestehende Anwesenheitssteuerung: lesend verbinden

Alpha.69-Kandidat bündelt den vorhandenen Organization-Editor im eigenen Zonenbereich
„Automationen“. `presence_automations` bleibt kompatibel; ausdrückliche Zuordnungen
für `lighting_automations` und `other_automations` nutzen denselben Speicher und
dieselbe Identitätsprüfung. Themen sind weder neue HA-Labels noch Ausführungsrechte.
Mehrfach verwendete Automationen bleiben ein Objekt; ausgewählte Strukturprüfungen
lesen die deduplizierte Vereinigung in ausdrücklich gestarteten Achterpaketen.
Damit sind keine vorhandenen Automationen geändert oder fachlich abgenommen.

Die neue Nutzerfreigabe vom 28.09.2026 erlaubt kontrollierte Automationsübernahme.
Die folgenden Alpha.61-Laufzeitgrenzen sind Implementierungsstand, kein dauerhaftes
Übernahmeverbot. Alpha.66 ergänzt im selben Inspector die Weiterverwendungsprüfung:
Steuerung, Verbraucher, gemischte Logik und direkte Bezüge; alle Verhaltens-/Rückweg-
Prüfungen bleiben offen. Keine Struktur meldet automatische Übernahmebereitschaft.
Noch kein ausführbarer Automationsänderungsplan oder aktiver Zuständigkeitswechsel.

Alpha.61 ergänzt den ausdrücklich gewählten Bestandsweg: HA-Automationen bleiben
alleinige Schreiber ihrer vorhandenen Helfer. Die Zonenansicht verweist auf den
bestehenden Editor „Bestand & Ordnung“; kein zweiter Konfigurationsspeicher.
`organization.assignments` ordnet `presence_status` (Boolean/logischer Status),
`presence_timer`, `presence_output` (Binärsensor, Klasse occupancy/presence) und
`presence_automations` zu. Fehlende Teile und for-/externe Nachläufe sind erlaubt;
es entsteht weder ein Ersatzsensor noch eine neue Schreibberechtigung.

Die Ansicht liest den vorhandenen HA-Zustandsstrom. Stabile Identität wird aufgelöst,
Ersetzung, Deaktivierung, veraltete Daten und unknown/unavailable bleiben unklar.
Timer active/paused/idle und eine tatsächlich gemeldete `finishes_at`-Frist werden
getrennt angezeigt; idle ist kein Freibeleg. Der öffentliche Bestandsstatus hat beim
Vergleich Vorrang. Ist er unklar, wird nicht still auf einen gültigen Boolean
zurückgefallen. Widerspruch zwischen Boolean und öffentlichem Sensor bleibt sichtbar.
Eigene Ausgaben zählen nicht als unabhängiger Bestandsvergleich. Ein zugeordneter
Ausgang darf nicht zugleich Eingang der eigenen Bewertung sein; beide Speicherrichtungen
und die laufende Auswertung prüfen das. PilotSuites Zeiten ändern keinen HA-Nachlauf.

Explizite Strukturprüfung verwendet den bestehenden begrenzten Inspector und
Related-Lookup plus ausgewählte Automationen (höchstens 50, keine rekursive Suche).
Status-/Timer-Schreiber, Verbraucher in Triggern/Bedingungen, gemischte und nicht
direkt zuordenbare Logik bleiben sichtbar. Dynamik/Blueprints/indirekte Ziele bleiben
Prüfgrenzen; ein Entity-Refresh ist kein bestätigter Boolean-Schaltaufruf.
Unlesbare Konfigurationen oder geänderte Revision/Identität/Verbindung liefern
keinen bestätigten Teilbefund. Keine Konfiguration wird gespeichert oder ausgeführt.
Prüfzeit und damalige Aktivierung sind historische Strukturbelege, keine dauerhafte
Laufzeitgarantie. Bestehende downstream-Automationen werden nicht umverdrahtet.

## Eigener HA-Ausgang: implementiert, vor Freigabe noch real zu validieren

Nur ein neu angelegtes, durch diesen Plan identifiziertes Paket darf publiziert werden:
interner input_boolean, Gültigkeits-Boolean, input_datetime für den Ablauf der Gültigkeit,
ein timer und ein Template-binary_sensor mit occupancy-Klasse. Der öffentliche Sensor
wird nach `<Zone> Anwesenheit` benannt. Gibt es diese kanonische ID bereits, wird die
Neuanlage blockiert und auf Bestandsprüfung verwiesen, statt einen _2-Doppelgänger zu bauen.
Interne IDs bleiben stabil an eine Zone gebunden; deren Anzeigenamen können anschließend
mit demselben Ontologiepfad lesbar eingeordnet werden.

Schritte: Verhalten speichern → eigenen Ausgangsplan prüfen/bestätigen → neu angelegte
Identitäten unabhängig lesen → Paket an dieselbe Revision binden → zunächst Vergleich.
Erst explizit gewählter Veröffentlichungsmodus aktiviert normale Boolean-Ausgaben.
Ein fremder bestehender Master oder eine fremde Automation wird nicht übernommen.

Vor Änderungen des gehaltenen Ausgangs wird die Gültigkeit zurückgenommen. Ungültiger
Präsenzstand setzt nicht owner.off. Veröffentlichung prüft Boolean und öffentlichen
Binärsensor zurück; nur Leseabfragen dürfen bei verzögerter Template-Aktualisierung
wiederholt werden. Unklare Ergebnisse setzen den Publisher dauerhaft bis zur erneuten
Konfiguration aus. Ein separater Gültigkeitsablauf (90 Sekunden) verhindert unbegrenzt
veraltete Aussagen bei Appausfall; HA-Template-Neuauswertung mit `now()` kann bis zum
nächsten Minutenwechsel dauern. Daher keine sekundengenaue 90-Sekunden-Abschaltzusage.

Alpha.60 trennt zusätzlich den letzten Rücklesenachweis von der aktuellen
Berechnung: `publication_checked_at` wird erst nach erfolgreicher Prüfung gesetzt.
Die bestehende Publikationsdrosselung bleibt 20 Sekunden; ein gleichbleibender Tick
verliert den Nachweis nicht. GET verlängert ihn nicht und ruft HA nicht auf. Nur bei
passender Revision/Entscheidung und frischer, gültiger Grundlage wird er für weniger
als 20 Sekunden als `verified` ausgegeben; die UI nennt ihn „Zuletzt bestätigt“ mit
Datum/Uhrzeit. Bei Ausfall, Konflikt oder Neustart keine Wiederverwendung. Das ist
keine zusätzliche Gültigkeitsgarantie des HA-Sensors und verändert seine Lease nicht.

Das ist keine atomare HA-/SQLite-Transaktion. Bei unklarer Helferanlage wird der Plan
mit Einzelschritt und Identitätsbeleg behalten; es gibt weder blinde Wiederholung noch
automatisches Löschen fremder Objekte. Alpha.50 bewahrt Erstellungs- und Registry-Beleg
kumulativ und kann nach einem Abbruch ausschließlich exakt belegte eigene Ausgaben erneut
lesen. Danach dürfen noch nie gestartete Schritte desselben bestätigten Plans fortgesetzt
oder ein vollständig belegtes Paket ohne erneute Anlage gebunden werden. Fehlende Belege,
Namensähnlichkeit, mehrdeutige Identitäten, Fremdzonen oder geänderte Revisionen bleiben
gesperrt. Ein lokaler Konfigurations-Speicherpunkt enthält diese neuen Betriebs-/
Ausgangspakete nicht; native App-/Datensicherungen bleiben für die vollständige
Wiederherstellung erforderlich.

Alpha.57 prüft die laufende Publikationsgrundlage nach wartenden HA-Aufrufen erneut:
Revision, Generation, aktive Zone, Verbindung und das höchstens 15 Sekunden alte
Bewertungsergebnis müssen weiterhin passen. Bei einem während des Aufrufs entstandenen
Konflikt greifen Ungültigsetzung und dauerhafte Ausgabesperre. Ein bereits gestarteter
HA-Aufruf kann nicht rückwirkend verhindert werden; der begrenzte Gültigkeitsablauf
bleibt daher erforderlich. Die Fehlermarkierung wird auf den neuesten lokalen
Zwischenstand gesetzt und überschreibt keine zwischenzeitlich erneuerte Frist.

## Visualisierung und Konfigurator

Alpha.55 ordnet die vorhandene Karte zuerst unter Zustand/Einrichtung/Verlauf ein;
sie bleibt unabhängig von der Diagnose-Modulauswahl. Fehlende Grundlage wird unklar,
Pause und HA-Veröffentlichung werden getrennt ausgewiesen. Module und alter expliziter
Schattenvergleich bleiben aufklappbare Diagnose, nicht ein zweiter Alltagsstatus.

Die Karte zeigt aktuellen unabhängigen Status, optionalen
HA-Vergleich, Quellen mit Signaltyp/Gültigkeit/Meldealter, verbleibender Nachlauf und
Publikationsstatus. Konfigurator bietet pro Quelle Suchfilter und unverlierbare Auswahl.
Der Sitzungsverlauf enthält höchstens 128 Übergänge im Arbeitsspeicher; er ist nicht
als Recorder-Historie etikettiert.

Historie: einzelne Sensorreihen, echte Einheiten, bekannte Wechsel, Tabellen, Min/Max und
begrenzte Verdichtung. Null ist ein Wert, unknown/unavailable sind Lücken. Mehrzustands-
Entitäten behalten unterschiedliche Kategorien; paused/idle werden nicht pauschal off.
Einheitenwechsel blockieren die gemeinsame Zahlenachse. Keine Anzahl von Ereignissen
oder Statistik wird aus der verdichteten Anzeige berechnet. Linien zwischen erhaltenen
Messpunkten sind eine Darstellung, keine Behauptung lückenloser physischer Beobachtung.

## Ontologisches Überführen

Ein expliziter Klick erzeugt einen Vorher-/Nachherplan für Anzeigename plus Rollenlabels
und gewähltes bestehendes Zonenlabel. Fremde Labels, Area, Floor und technische Entity-ID
bleiben erhalten. Identität, vollständiger Vorherzustand und Revision werden vor dem
Schreiben erneut gelesen. Das Ergebnis wird unabhängig verifiziert. Die Rücknahme ist
ein neuer expliziter Plan und wird bei zwischenzeitlichen Änderungen blockiert.

Rollenlabels müssen vorhanden und eindeutig sein. Die sechs Rollen werden nicht aus
Namen beliebiger Labels erraten. Label-basierte Automationen und dynamische Dashboards
können auf Metadatenänderungen reagieren; dieser Effekt steht im Plan. Der vorhandene
HA-Metadaten-Endpunkt besitzt keine atomare Compare-and-swap-Garantie.

Eine technische Entity-ID-Änderung liefert `migration_required`, niemals einen verdeckten
Registry-Rename. Automationen, Skripte, Szenen, Dashboards, Gruppen, Templates und
Config-Entries sowie integrationsinterne Verbraucher müssen gemeinsam migriert werden.
Diese vollständige Migration und vorhandene Automationsübernahme sind noch NICHT
implementiert. Darum keine Behauptung einer vollständigen Ein-Klick-ID-Bereinigung.

## Nachweise und nächste verbindliche Schritte

Lokale Produktionspfad-Tests verwenden echte HTTP-Routen und SQLite, aber ein synthetisches
HA-Gegenüber. Transporttests prüfen die tatsächlichen WS/Flow-Payloadformen. Das ist kein
Nachweis der installierten App-Berechtigungen oder realen HA-Konfigurationsflow-Schemata.
Alpha.49 bestand zusätzlich den isolierten CI-Lauf mit Home Assistant Core 2026.9.3 und
die vollständige Chromium-Anwendungsfolge. Die angemeldete Haushalt-Ingress-Oberfläche
bleibt ein eigener Nachweis; direkter Zugriff wurde korrekt mit 403 abgewiesen.

Alpha.50 bestand lokal 560 Python-, 68 JavaScript- und 62 API-/Repository-Verträge sowie
exakte Remote-CI einschließlich Browsersuiten, Container und wegwerfbarem HA-Protokoll.
Die frische native PilotSuite-only-Sicherung `c31afe38` wurde vor Store-Abgleich und
Installation verifiziert. Keine bestehende Hausautomation und kein Haushalt-Helfer
diente als Installationstest.

Primärreferenzen: https://www.home-assistant.io/integrations/timer/
https://www.home-assistant.io/integrations/template/
https://www.home-assistant.io/integrations/recorder/
https://www.home-assistant.io/docs/configuration/state_object/

## Release acceptance continuation

Der isolierte HA-Protokolljob installiert eine wegwerfbare Core-Instanz und prüft den
produktiven WS-/REST-Pfad für Helfer, natives Template, Gültigkeit, Timer und
Metadatenrücknahme mit echter Authentifizierung. Er verbindet sich nie mit dem Haushalt
und behält keine Zugangsdaten. Alpha.50 bestand diesen exakten Kandidatenpfad; die noch
offene angemeldete Ingress-Abnahme wird dadurch nicht ersetzt.
