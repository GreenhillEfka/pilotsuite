# Bestand, Ordnung und kontrollierte Migration

## Zielbild

PilotSuite übernimmt nicht jede Altlast unverändert und ersetzt nicht jede vorhandene
Automation. Sie ordnet Funktionen einer gemeinsamen Ontologie zu, bewertet Abweichungen
und überführt geeignete Teile kontrolliert in eine verständliche Zielstruktur. Dieselben
Regeln gelten für PilotSuite selbst. Einheitliche Bedeutung und klare Zuständigkeit sind
verbindlich; unterschiedliche technische Umsetzung braucht einen sachlichen Grund.

**Alpha.32 liefert den durchgehenden Arbeitsweg** von bestehenden Automationen über
manuelle Funktionszuordnung bis zu bestätigter Anzeigenamen-Bereinigung. Reparaturpläne
und technische Ziel-IDs sind prüfbar, ihre Ausführung bleibt ausdrücklich getrennt.
Ein funktionierender for-Nachlauf oder vorhandener Timer ist kein Grund für Duplikate.

## Ontologie und Konfiguration

| Funktion | Bestandstypen | Bedeutung |
|---|---|---|
| Präsenzquellen | binary_sensor, input_boolean | Beobachtungsquellen; logische/abgeleitete Quellen sind gekennzeichnet |
| Raumstatus | input_boolean, binary_sensor | Bestehender bestätigter Status, nicht zwingend beschreibbarer Ausgang |
| Nachlauftimer | timer | Vorhandene Zeitkomponente |
| Nachlauf-Dauer | input_number, number | Parameterquelle, Einheit ausdrücklich beachten |
| Manuelle Bedienung | input_boolean, binary_sensor | Bestehender Override, keine automatische Umdeutung |
| Automatiksperre | input_boolean, binary_sensor | Bestehende Freigabe-/Sperrfunktion; Polarität noch nicht automatisch interpretiert |
| Zuständige Automationen | automation | Bewusst ausgewählte Bestandslogik zur Untersuchung, nicht Ausführungsübernahme |

Nachlaufverfahren sind unabhängig auswählbar: beobachten, vorhandenes for, vorhandener
Timer oder andere Bestandslogik. Eine Zone kann mehrere HA-Bereiche enthalten. Globale
Auswahl findet auch Helfer ohne Bereich; eine Bereichszuordnung wird nicht erzwungen.
Ein Gruppensensor und seine Mitglieder sind nicht automatisch unabhängige Belege.
Quellenzusammenhänge können noch unvollständig sein; die Oberfläche behauptet keine
vollständige Entdoppelung oder Laufzeitsemantik.

Manuelle Zuordnung ist die maßgebliche Bestätigung und wird von einer Analyse nicht
überschrieben. Neue Zuordnungen benötigen aktive Registereinträge passenden Typs;
bereits gespeicherte, inzwischen fehlende Identitäten bleiben als ungeklärt erhalten.
Die Kombination Domain, Plattform und unique_id identifiziert ein Objekt. Eine neue
Entity-ID mit demselben Schlüssel wird aufgelöst; ein fremdes Objekt unter der alten
ID wird nicht automatisch übernommen. Ohne stabile Kennung bleibt die Aussage enger.

Funktionsbindungen liegen als ergänzendes `organization`-Objekt in der vorhandenen
`zone_context`-Konfiguration. Die bisherige Lern-/Auswahlkonfiguration bleibt erhalten.
Die manuelle Zuordnung ist keine implizite Entscheidung „relevant“, keine Lernfreigabe,
keine Steuerungsfreigabe und keine automatische Neuanlage. Änderungen verwenden dieselbe
Zonenrevision wie Rollen und Definitionen; die vorherige Zuordnung bleibt im bestehenden
begrenzten Änderungsjournal. Vorhandene Speicherpunkte können die optionalen Bindungen
mit sichern/wiederherstellen. Alte Punkte ohne dieses Feld bleiben lesbar; Wiederherstellung
setzt dessen damaligen Stand (gegebenenfalls ohne Bindung) zurück, pausiert die Zone und
stellt keine Lernfreigaben wieder her. Der automatisch erzeugte Vorher-Punkt enthält den
Zustand vor der Wiederherstellung. Keine direkte Bearbeitung von HA-.storage-Dateien.

## Bestandsanalyse und Reparaturplanung

Analyse startet ausdrücklich mit einer bis acht ausgewählten Automationen, auch wenn
Raumstatus und Timer noch nicht zugeordnet sind. Damit entfällt der Zirkelschluss der
bisherigen Prüfung. Die Konfiguration wird transient gelesen und nicht vollständig
in PilotSuite gespeichert. Angezeigt werden Referenzen und JSON-Fundstellen, nicht
potenziell sensible Roh-Templates, Beschreibungen oder beliebige Aktionsdaten.

Unterstützt werden aktuelle und ältere Singular-/Pluralfelder, verschachtelte Bedingungen
und Aktionen, `event_data.entity_id` sowie statische Argumente bekannter Templatefunktionen
und `states.domain.object`-Referenzen. Templates werden nicht ausgeführt. Literal-Fundstellen
sind Kandidaten für Abhängigkeiten, kein Beweis für eine vollständige Templateauswertung.
Dynamisch zusammengesetzte IDs, Blueprint-Auflösung, indirekte Ziele/Aufrufe und unbekannte
Strukturen bleiben sichtbar begrenzt. Deaktivierte oder dynamisch aktivierte Zweige werden
nicht als bestätigte aktive Rollenhinweise behandelt. Umfang/Größe/Tiefe sind begrenzt.

Fehlende Referenzen, deaktivierte Objekte, unbekannte/unverfügbare Zustände und veraltete
Snapshots sind unterschiedliche Befunde. Ein veralteter Snapshot begründet keinen
fehlenden Helfer. Ein nicht lesbarer Teil bleibt unvollständig, niemals „konfliktfrei“.

Ersatzvorschläge sind auf dieselbe Domain begrenzt und nennen ihre Gründe: passende
Speicherkennung, Bereichsbezug oder Namensähnlichkeit. Rangwerte sind keine kalibrierten
Wahrscheinlichkeiten. Einheit und Zustand werden angezeigt. Eine bloße Ähnlichkeit beweist
weder dasselbe Gerät noch dieselbe Funktion. Manuelle Auswahl muss die Bedeutung bestätigen.
Die Reparaturvorschau liest die Automation erneut und verwirft einen geänderten Fingerabdruck.
Sie speichert konkrete alte/neue Referenzen mit Fundstellen; keine Automationskonfiguration
wird geschrieben. Dieser Ausführungspfad ist bewusst noch nicht implementiert.

## Ordnung statt kosmetischer Umbenennung

Für gebundene Helfer wird ein gemeinsames Schema vorgeschlagen:

- Anzeigename: `<Zonenname> · <Funktionsbezeichnung>`.
- Technische Ziel-ID: `<domain>.<normalisierter_zonenname>_<funktionssuffix>`.

Beides sind getrennte Vorgänge. Die aktuelle ausführbare Bereinigung ändert nur den
Anzeigenamen. Eine technische ID-Migration muss zusätzlich alle erreichbaren Verbraucher
prüfen: Automationen, Skripte, Szenen, Dashboards, Gruppen, Konfigurations-Entries und
externe Anwendungen. Ausgewählte Automationen decken das nicht ab. Deshalb zeigt Alpha.32
Kollisionen/ungeprüfte Verbraucher und bietet keinen ausführbaren technischen Rename.
Das ist kein Vorschlag, technische Unordnung dauerhaft beizubehalten, sondern eine
explizite Grenze vor einer noch nicht abgesicherten Migration.

Werden Helfer bereits mehreren PilotSuite-Zonen zugeordnet, wird eine einseitige
Namensbereinigung blockiert. Ein gemeinsamer Namensraum muss vorher festgelegt werden.
Die reine Metadatenoperation ändert keine Werte, Bereiche, Labels, IDs oder bestehenden
Automationsdefinitionen. Trotzdem können Sprachassistenten und Anzeigenamen-basierte
Vorlagen betroffen sein; die Freigabe muss diese Auswirkungen berücksichtigen.

## Bestätigte Namensänderung und Rücknahme

Der bestehende PlanStore speichert begrenzte Pläne in seiner bestehenden SQLite-Datenbank
(`zone_meta`, keine neue Datenbank, Schema weiterhin 8). Namenspläne enthalten pro Objekt
stabile Identität, aktuellen Namens-Override einschließlich null, Zielname und Zonenrevision.
Die Vorschau wird unabhängig aus der nativen Registry gelesen, ist 15 Minuten gültig und
bekommt eine Prüfsumme. Nicht bestätigte Vorschau ist keine Erlaubnis zur Ausführung.

Nach Bestätigung wird der Auftrag einmalig beansprucht. Vor jedem externen Schreibaufruf
stehen der Vorher-Zustand und ein `sending`-Marker dauerhaft auf Datenträger. Aktuelle
Identität, Ausgangsname, gemeinsame Zonennutzung und Revision werden erneut geprüft.
Die native WebSocket-Aktion enthält ausschließlich `entity_id` und `name`; kein
`new_entity_id`, keine Labels, Optionen, Freigaben oder generische Serviceaktion.
Unabhängiges Rücklesen bestätigt den Zielzustand. Native HA-Adminrechte müssen vorhanden
sein; bei Ablehnung wird keine Berechtigung erweitert oder ein alternativer Zugang versucht.

HA bietet für diese Registry-Operation keine atomare Compare-and-swap-Zusage. Zwischen
Prüfung und Schreiben kann eine externe Änderung stattfinden; Rücklesen und Vorher-Daten
begrenzen die Folgen, beseitigen dieses Rennen aber nicht. HA und SQLite sind auch keine
gemeinsame Transaktion. Bei mehreren Objekten kann ein bestätigter Präfix und ein Konflikt
oder unbekannter Rest verbleiben. Diese Einzelzustände werden angezeigt.

Verlorene Antworten führen zu Rücklesen, nicht zum automatischen Wiederholen. Ein erneut
aufgerufener oder nach Prozessneustart vorgefundener Auftrag gibt den dauerhaften Status
zurück. `sending` bedeutet unbekannter Ausgang, nicht Erfolg. Auch ein bestätigter Zielzustand
nach verlorener Antwort belegt nicht sicher, wer die Änderung vorgenommen hat.

Rücknahme ist deshalb ein neuer, separat bestätigter Plan. Nur Operationen mit bestätigter
Schreibantwort, passendem Rücklesen, weiterhin derselben Identität und unverändertem Zielnamen
kommen dafür infrage. Spätere fremde Änderungen werden nicht überschrieben. Die Sammlung ist
auf 100 Pläne begrenzt; Wiederherstellungsdaten werden nicht stillschweigend gelöscht.
Ein Punktelimit erfordert bewusste weitere Verwaltung, nicht automatische Löschung von
Recovery-Daten. Vollständige native App-Sicherungen bleiben davon getrennt.

## Habitus: stabile Struktur, adaptives Verhalten

Die Ontologie, Identitäten, Einheiten und Zuständigkeiten sollen stabil sein. Sensorgruppen,
Zeitverfahren, Kontexte und später gelernte Komfortpräferenzen dürfen sich innerhalb
bestätigter Grenzen unterscheiden. Keine Raumkategorie erzwingt identische Verhaltensregeln.

Der vorhandene Aktivitätsdetektor bleibt in Alpha.32 unverändert. Er ist kein umfassender
Situationslerner. Das nächste fachliche Modell unterscheidet (1) beobachtete Gegenwart,
(2) nachvollziehbare Situationen wie Durchgang/Aufenthalt/Mediennutzung, (3) zeitlich
wiederbeobachtete Präferenzen und (4) separat freigegebene Umsetzung. Jeder Lernschritt
braucht seine zulässigen Quellen und Herkunft, Zeit-/Kontextgruppe, Belege, Unsicherheit
und Korrekturmöglichkeit. Ein manueller Eingriff ist ein Hinweis, kein automatischer Befehl
zum Umlernen. Fehlende Daten sind nicht Abwesenheit. Abgeleitete Zustände dürfen keine
zusätzlichen unabhängigen Stimmen bekommen. Eine bestätigte Ordnung schafft die Basis
für diese Flexibilität; sie ersetzt nicht die noch nötigen Modelltests.

Die ältere Presence-Runtime-Aktivierung ist in diesem Paket fail-closed: ihre
Timer-Ende-Verarbeitung und die kontrollierte Zuständigkeitsübergabe wurden noch nicht
hinreichend akzeptiert. HA-Timer haben keinen persistenten Zustand `finished`. Die
bloße Zuordnung oder eine grüne Planungskarte darf diese Lücke nicht verdecken.
Ein aktiver Owner-Wechsel und adaptive Licht-/Musik-/Klimasteuerung sind nicht enthalten.

## Prüfumfang und Abnahme

Unit-/Integrationstests verwenden ausschließlich synthetische Namen/IDs. Geprüft werden
unter anderem Template-/Eventreferenzen, deaktivierte Zweige, fehlende und umbenannte
Identitäten, manuelle Bindungen über Bereichsgrenzen, Persistenz/Revision, unveränderte
Lernbelege, bestehende for/timer-Planung, native Registry-Nachrichten, separate Namensfreigabe,
Teilfehler, Antwortverlust, Prozessneustart und konfliktgeschützte Rücknahme. Bestehende
Regressionstests bleiben erhalten. Ein neuer tatsächlicher App-Browsertest prüft Suche,
Analyse, Reparaturvorschau, Speichern, Navigation, Namensplan/Rücknahme und kleine Bildschirme.

Synthetische Abnahme ist keine authentifizierte Haushaltssitzung und keine echte HA-
Disaster-Recovery-Übung. Die Auslieferung aktiviert keine Haushaltsfunktion und führt keine
Umbenennung aus. Native PilotSuite-only-Sicherung, exakte CI und Versions-/Laufzeitprüfung
bleiben die Release-Gates; die Bedienung im Haushalt wird separat bestätigt.

## Primärquellen der API-/Zeitsemantik

- https://www.home-assistant.io/integrations/timer/
- https://www.home-assistant.io/docs/automation/trigger/
- https://developers.home-assistant.io/docs/api/websocket/
- https://raw.githubusercontent.com/home-assistant/core/2026.9.3/homeassistant/components/config/entity_registry.py
- https://raw.githubusercontent.com/home-assistant/core/2026.9.3/homeassistant/helpers/entity_registry.py

Diese Quellen wurden für die implementierten Registry-GET/UPDATE-Verträge und die
Timer-/for-Grenzen geprüft. Ein späterer technischer Migrations-/Automationsschreibpfad
benötigt eigene API-, Verbraucher- und Fehlerfalltests; dieses Dokument bescheinigt ihn nicht.
