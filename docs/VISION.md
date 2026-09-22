# PilotSuite — verbindliche Gesamtvision

Stand: 2026-09-22. Zielbild, nicht Funktionsversprechen der aktuellen Alpha.

PilotSuite steigert den Komfort mit den vorhandenen Home-Assistant-Geräten und
Automationen: beobachten, Zusammenhänge erklären, Gewohnheiten mit Zustimmung
erkennen, passende Verbesserungen vorschlagen und freigegebene Maßnahmen prüfen.
Bestehende Automationen haben Vorrang vor neu erzeugten Duplikaten.

## Verantwortlichkeiten

| Bestandteil | Besitzt | Besitzt nicht |
|---|---|---|
| Home Assistant | Geräte, Entitäten, Areas, Labels, Zustände, Ausführung | PilotSuite-Lernmodell |
| Add-on-Kern | Semantik, Habitus-Zonen, Rollen, Vorschläge, Policies, Feedback | zweite HA-Gerätedatenbank |
| SQLite (geplant) | eigene Definitionen, begrenzte Belege, Journal | vollständige HA-Historie |
| Ingress-UI | Erklärung, Konfiguration, Freigaben, Dev/Wiki-Ansichten | eigene Entscheidungslogik |
| Optionaler HA-Adapter | native Entitäten, Conversation, Bedienfunktionen | zweite Engine oder Zonendefinition |
| Optionales LLM/RAG | Dialog, Erklärung, Entwürfe | unmittelbare Aktorbefehle oder Policy-Ausnahmen |

## Fachmodell

Eine Habitus-Zone besteht aus HA-Referenzen, Rollen, Fähigkeiten und Policies.
Der Erdkellerbereich kann Eingang, Innenraum und Referenzmessungen umfassen.
Die konkrete Zuordnung muss mit dem Nutzer geprüft werden; keine erfundenen IDs.
Klima ist die erste Domäne, nicht das allgemeine Modell für Licht, Präsenz und Medien.

Beobachtungen tragen Einheit, Quelle und Qualitätsinformationen. Ein fehlender
Messwert ist unbekannt, nicht null und nicht unauffällig. Frische der HA-Projektion
und tatsächliche Aktualität eines physischen Sensors sind unterschiedliche Dinge.
Ein unveränderter HA-Zustand ist nicht allein wegen eines alten Zeitstempels defekt.

Muster tragen Zeitraum, Zähler, Grundhäufigkeit und Unsicherheit. Korrelation ist
kein Kausalitätsbeweis. Menschliche Bedienung, bestehende Automation und eigene
PilotSuite-Aktion müssen, soweit belegbar, unterschieden werden; unbekannte Herkunft
bleibt unbekannt. Eigene Aktionen dürfen keine selbstverstärkenden Lernbelege erzeugen.

Vorschläge besitzen stabile Identität und Lebenszyklus: vorgeschlagen, angenommen,
abgelehnt, vertagt, abgelaufen. Nutzerfeedback beeinflusst Präferenz/Rangfolge,
nicht die historische Zahl beobachteter Ereignisse. Mehrnutzerkonflikte erfordern
explizite Regeln, keine erratene Identität.

Der Brain-Graph zeigt nachvollziehbare Pfade von Beobachtung über Regel zum Vorschlag.
Keine unabhängige zweite Wahrheit und keine dekorative Behauptung neuronalen Lernens.

## Bedienung und Komfort

- Zentrale Text-/Sprachoberfläche mit Kontext und auswählbaren verfügbaren Geräten.
- HA Assist nutzen; Sonos, Alexa, Siri und Apple-Geräte einzeln auf tatsächliche
  Ein-/Ausgabefähigkeiten prüfen. Kein pauschales Versprechen bidirektionaler Sprache.
- Module, Automatisierungsmanager, Erklärungen, Health, Wiki und Entwickleransicht.
- HomeKit-Kandidaten zunächst nur vorschlagen; nichts ungefragt exportieren.
- Sinnvolle Presets und manuelle Updates zuerst, geprüfte automatische Updates später.
- Grundfunktionen bleiben ohne LLM, Cloud oder separaten Modellserver nutzbar.

## Sicherheit und Datenschutz

Eine einzige Ausführungskette: Plan, Policy/Freigabe, erforderliche Sicherung,
Ausführung, Verifikation, aktionsspezifische Wiederherstellung oder Eskalation.
Freigaben haben Scope und Ablaufzeit; Zustände werden unmittelbar vor Ausführung
erneut geprüft. Widerruf und Not-Aus müssen sichtbar sein. Ein physischer Effekt
oder eine gesprochene Nachricht ist nicht allgemein rückgängig zu machen.

Lernen benötigt Zustimmung, begrenzte Aufbewahrung, Export und Löschen/Reset.
Keine ungeprüften Alt-Datenimporte, keine unverschlüsselten zentralen Secret-Dateien.
Keine direkte Änderung von HA `.storage`; bestehende Konfigurationen erhalten.

## Herkunft und Wiederverwendung

Referenzstände: `pilotsuite-styx-ha@4f78be5`, `pilotsuite-styx-core@d4e3a7b7`.
Die alte HA-Konzept-Richtlinie belegt die Zuständigkeitsprobleme. Der Core enthält
wertvolle Muster-/Feedback-Ansätze, aber mehrere parallel verdrahtete Dienste.
Übernahme nur pro Baustein mit fachlichem Vertrag, Tests und einem Besitzer.
Insbesondere keine Feedback-bedingte Veränderung statistischer Beobachtungszähler.

Siehe `IMPLEMENTATION_STATUS.md` für den belegten Umfang und `ROADMAP.md` für die Reihenfolge.
