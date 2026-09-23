# Verbindliches Paket: Beobachtungen, Sensorgruppen und erster Lernkreislauf

## Ein konsistenter Ablauf

Zone → Kandidaten → ausdrückliche Relevanz → normalisierte Beobachtungen →
Sensorgruppen → kompakte Bewertung → optional bestätigtes Lernen → Musterkandidat
→ Nutzerfeedback. Ein vorhandenes Gerät oder eine Empfehlung ist keine Zustimmung.

| Zustand | Beobachtung/Bewertung/Lernen |
|---|---|
| Relevant | Geeignete, aktuell zur Zone gehörende Entität darf beitragen |
| Ungeprüft | Nur Kandidat; keine Neuronen oder Lernbelege |
| Ignoriert | Ausgeschlossen, Entscheidung bleibt erhalten |
| Nicht mehr vorhanden | Entscheidung erhalten; keine erfundenen Werte |
| Zone pausiert | Keine Auswertung und keine neuen Lernbelege |

Die globale Verbindung bleibt auch bei leerer Auswahl betriebsbereit. In der UI
werden Kandidaten, Relevanz und tatsächlich ausgewertete Beobachtungen getrennt.
Nicht unterstützte Aktions-/Diagnose-Domänen erzeugen trotz Markierung keine Neuronen.

## Sensorgruppen

Rollen besitzen Listen statt einzelner IDs, höchstens 20 pro Rolle. Nur passende
bestätigte Entitäten sind neu zuweisbar. Geräteklassen werden nicht umetikettiert.
Temperatur und Feuchte: Median der gültigen normalisierten Hauptwerte; Min/Max,
Spanne, Herkunft und fehlende Quellen bleiben sichtbar. Ohne Zuordnung ist nur
ein einziger eindeutiger Sensor automatisch verwendbar. Referenztemperaturen
bleiben eigene Werte und können nicht zugleich Hauptsensor derselben Zone sein.

Präsenz: ein gültiges On bedeutet Aktivität; All-Off nur, wenn alle Quellen gültig
sind. Ein Ausfall bedeutet unbekannt/teilweise verfügbar. Lernen braucht eine
explizite Präsenzgruppe. Hauptsensorgruppen über mehrere Räume beschreiben einen
Bereich, nicht ein physikalisch einheitliches Raumklima; getrennte Zonen bleiben
für raumspezifische Regeln sinnvoll. Extreme Einzelwerte werden nicht weggefiltert,
sondern über Min/Max und Details sichtbar. Die Zusammenfassung ersetzt keinen Alarm.

## Lernvertrag activity-v1

- Standard aus; Zustimmung pro Zone und Präsenzgruppe, Zeitpunkt gespeichert.
- Nur abonnierte frische Off→On-Ereignisse nach Zustimmung und bei gesundem Stream.
- Keine Snapshot-/Reconnect-Beobachtungen, keine historischen Importe, kein Replay
  älter als 120 Sekunden oder aus der Zukunft über fünf Sekunden.
- Pro Zone fünf Minuten Sperrzeit nach einem Beleg, einschließlich aller Gruppenmitglieder.
  Das reduziert Duplikate; es ist keine präzise Erkennung menschlicher Besuche.
- 14 Tage Aufbewahrung; maximal 5.000 Belege global. Aufräumen auch bei normalen
  Abgleichen ohne neue Ereignisse. Bei ausgeschalteter App beim nächsten Start.
- Standard: fünf Aktivierungen an drei Tagen im selben Zwei-Stunden-Fenster.
  Mindestwerte, Zeitzone und Tagesgruppen sind im Entwicklungszweig konfigurierbar.
  UTC bleibt Bestandsstandard. Grundraten und durchgängige Beobachtungsabdeckung
  sind nicht implementiert; siehe RHYTHMS_AND_CONTEXT.md.
- Beobachtungsstatistik (Ereignisse, Tage, Gesamtbelege, Herkunft), deterministische
  Regelschwelle, statistische Konfidenz, Read-only-Risiko und Nutzerpräferenz sind
  getrennte Felder. Regelstärke zeigt nur den Abstand zur Kandidatenschwelle, keine
  Wahrscheinlichkeit. Statistische Konfidenz bleibt unbekannt (`null`).
- Herkunft nur user_context/derived_context/unknown, ohne Benutzer-/Context-IDs.
  Das ist kein Beweis für manuelle Bedienung oder eine konkrete Automation.
- Stabile Muster-ID aus Algorithmus, Zone, sortierter Quellgruppe und Zeitfenster.
- Nutzerpräferenz getrennt von Belegen; höchstens 2.000 letzte Feedbackeinträge.
  Eine Präferenz ändert weder Beobachtungszahlen noch Regelstärke oder Konfidenz.
- Widerruf stoppt Aufzeichnung. Reset löscht Belege/Feedback und widerruft Freigabe.
  Wechsel der Präsenzgruppe löscht alte Belege/Feedback; die UI informiert vorher.
  Referenz-/Klimagruppenänderungen ändern keine Aktivitätsbelege.
- Export pro Zone enthält eigene Konfiguration, Belege und Kandidaten, keine Tokens.

## Persistenz und Freigabe

SQLite-Schema 5 im Entwicklungszweig, Sicherung vor Migration aus Schema 1–4,
atomare Schemaänderung, gemeinsame Revisionskontrolle für Zonen/Auswahl/Rollen.
Die automatische Auswahl-Ausnahme entfällt ohne vorhandene Entscheidungen zu ändern.
Bestehende App-Backups werden bei einem Lernreset nicht verändert. Downgrade nur
mit passender App-und-Daten-Sicherung. Keine Änderungen an HA-Registries/Automationen.

## Abnahme

Regressionen für strikte Auswahl, Gruppenmedian, Referenzen, fehlende Quellen,
Migration mit Backup, Ereignis-Deduplizierung, Zustimmung, Revisionen, Ablauf/Limit,
Feedback ohne Zähleränderung, Neustart, Export und Reset. Browserprüfung zusätzlich
für Sensorgruppen und Freigabe-/Feedback-/Reset-Bedienung. Live-Abnahme nach Deployment
prüft Betrieb separat; echte Muster brauchen reale Beobachtungstage. Keine synthetischen
Belege in produktive HA-Daten schreiben, um Lernen vorzutäuschen.
