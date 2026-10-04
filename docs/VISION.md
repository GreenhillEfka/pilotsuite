# PilotSuite — ein verständlicher Zonenassistent

## Aktuelles Produkt: Habituszonen sauber aufbauen

Neue Nutzerentscheidung vom 30.09.2026 nach Auslieferung von Alpha.72: PilotSuite
auf **Erstellung, Darstellung und Dokumentation von Habituszonen** reduzieren.
Die Oberfläche wird dafür von Grund auf neu geordnet. Vergleiche, Präsenz-/Licht-
einrichtung, Automationswerkzeuge, Lernen und weitere Module vorerst ausblenden.

PilotSuite beantwortet zunächst: **Welche Zonen habe ich? Was gehört dazu?
Wie ist die Zuordnung begründet und dokumentiert?** HA-Bereiche und manuelle Tags
werden in einem verständlichen Zonenweg zusammengeführt. Vorhandene Daten,
stabile Identitäten und die bestehenden Speicher bleiben erhalten.

Verbindlicher nächster Umfang und Abnahme:
[HABITUS_FOUNDATION_RESET.md](HABITUS_FOUNDATION_RESET.md), ADR-044.
Alpha.73 setzt diese Richtung um und ist nach geprüfter Auslieferung installiert. Reale strukturelle Zonenabnahme ist ausdrücklich beauftragt
und benötigt die angemeldete Prüfung der tatsächlichen Zuordnungen. Aktive Lichtsteuerung bleibt offen. Erst nach tragfähiger Struktur folgen Präsenz/Helfer, dann Licht und später
Klima, Multimedia und Mustererkennung.

HA-Bestandsabgleich vom 04.10.2026: sechs öffentliche Habituszonen-Anker sind
vorhanden; weitere Zonen sollen ohne feste Anzahl ergänzt werden können. Jede der
sechs HA-Zonen besitzt eine Lichtgruppe mit vorhandener Lichtautomatik-Freigabe.
Vier Zonen (Bad, Gang, Küche, Wohnen) besitzen außerdem eine optionale
präsenzgeführte Sonos-Sound-Cloud-Kopplung. Das sind HA-eigene Funktionen, keine
PilotSuite-Licht-/Medienmodule und kein Beleg für bereits synchronisierte
PilotSuite-Zonen. Die spätere Einbindung nutzt denselben geklärten Zonen- und
Präsenzbezug, ohne eine konkurrierende Licht- oder Sound-Engine zu bauen.

## Nachgelagerte Vision und bestehende fachliche Grundlagen

Die folgenden Abschnitte bewahren Ziele und technische Invarianten des bisherigen
Produkts. Sie sind kein Auftrag, diese Module jetzt sichtbar zu lassen oder weiter
auszubauen. Der frühere Nachtauftrag steht in [HABITUS_SETUP_PLAN.md](HABITUS_SETUP_PLAN.md).

Konsolidiertes Zielbild vom 28.09.2026, zur schrittweisen Umsetzung im bestehenden
Projekt. Dies ist kein Nachweis neuer Laufzeitfunktionen. Den Funktionsstand führt
[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md), die Installation
[RELEASE_STATE.json](RELEASE_STATE.json).

Präzisierung vom 29.09.: zuerst vorhandene Habituszonen vollständig und verständlich
einrichten, noch keine neue Intelligenz. Übersicht, Einrichtung, thematisch gebündelte
Automationen und Diagnose gehören zur Zone. Bestehende Helfer/Regeln wiederverwenden,
notwendige Lücken konkret planen. ADR-043 und [UX_WORKSPACE.md](UX_WORKSPACE.md)
definieren diesen Nutzerweg; Fähigkeiten nicht aus dem Zielbild ableiten.

## Nutzen vor Funktionsumfang

PilotSuite soll drei Fragen zuverlässig beantworten: **Was passiert in meiner
Zone? Warum wird das so bewertet? Was muss ich gegebenenfalls ändern?**

Präsenz ist die erste Priorität. Licht, Klima und Medien nutzen diesen Kontext,
bekommen aber keine zweite Präsenzlogik. Bestehende HA-Automationen werden zuerst
verstanden; PilotSuite ersetzt sie nicht ungefragt. Ein ideales System bedeutet
hier weniger Bedienaufwand bei nachvollziehbaren Aussagen, nicht möglichst viele
Module oder eine behauptete mathematisch optimale Haussteuerung.

## Der kleinste tragfähige Kern

1. **Zone:** stabile Identität, vorhandene HA-Referenzen, relevante Quellen und
   explizites Verhalten. Ein HA-Bereich ist nicht automatisch eine Habitus-Zone.
2. **Bewertung:** typisierte Quellen, ein deterministischer Präsenzkern, begrenzte
   Historienanalyse und eine erklärbare Entscheidung mit Zeit- und Qualitätsbezug.
3. **Ausgabe:** dieselbe Entscheidung in der Oberfläche und optional im geprüften
   eigenen HA-Ausgangspaket. Analyseberechtigung und Schreibrechte bleiben getrennt.

Home Assistant besitzt Geräte, Zustände, Recorder und Ausführung. PilotSuite besitzt
seine Zonen, Regeln, begrenzten Belege und Änderungspläne. Oberfläche, Graph und
optionale Sprachassistenz sind Ansichten dieser Daten, keine weiteren Entscheider.
Ein Prozess, die bestehende SQLite-Datenbank und der vorhandene HA-Client genügen.
Kein neuer Broker, Plugin-Unterbau, Graphspeicher oder separater KI-Dienst.

## Verbindliche Präsenzsemantik

Dauerpräsenz, Bewegungsimpuls und TV-/Nutzungsindiz bleiben verschieden.
Ein positiver tragender Beleg kann Anwesenheit begründen. Frei wird eine Zone erst
nach nachvollziehbarem Nachlauf und geklärter erforderlicher Abdeckung.
Unklar oder unavailable ist niemals stillschweigend frei. Polling und Neustarts
verlängern keine Frist; ein laufender Fernseher beweist keinen Menschen.
Eigene Ausgaben dürfen sich nicht als Eingang selbst bestätigen.

Der interne Boolean hält den Zustand; allein bildet er keine Ungewissheit ab.
Der öffentliche Anwesenheits-Binärsensor berücksichtigt deshalb zusätzlich
Gültigkeit und deren Ablauf. Vorhandene gleichnamige Sensoren werden weder übernommen
noch durch einen `_2`-Doppelgänger umgangen. Details: [ZONE_INSTANCE_V2.md](ZONE_INSTANCE_V2.md).

Der erste Bestandsweg lässt vorhandene Automationen bewusst zuständig: deren
Boolean, Nachlauf und öffentlicher Sensor werden zugeordnet, gelesen und mit der
unabhängigen PilotSuite-Bewertung verglichen. „Verbinden“ bedeutet keine Übergabe
der Steuerung. Verbraucher werden sichtbar gemacht, nicht automatisch umgestellt.
Die neuere Nutzerfreigabe erlaubt ausdrücklich die kontrollierte Übernahme bestehender
Automationen. Weiterverwendung ist der bevorzugte Ausgangspunkt, kein dauerhafter
Vergleichszwang. Eine spätere Anpassung oder Steuerungsübergabe braucht konkrete
Änderungen, geklärte Schreiber, Verhaltensprüfung, Freigabe und Wiederherstellung.
Die bestehende Prüfung bereitet dies vor; ein ausführbarer Übernahmepfad ist noch offen.

## Bedienung und Analyse

Im Alltag zuerst Zone, Zustand, Grund, verbleibender Nachlauf und Datenlücke.
Seit Alpha.70 erscheint bei ausdrücklich verbundener Bestandskette ihr öffentlicher
HA-Sensor als Bestandsmeldung, die eigene Bewertung getrennt als Vergleich. Ohne
Verbindung bleibt sie klar als PilotSuite-Berechnung gekennzeichnet. Ein unklarer
Bestandsstatus darf niemals unbemerkt durch die eigene Berechnung ersetzt werden.
Diese Darstellungsrichtung ist keine bereits erfolgte Steuerungsübergabe.
Quellenkonfiguration, Verlauf und Diagnose werden bei Bedarf geöffnet. Das Dashboard
„Habituszonen“ bleibt ontologische und gestalterische Referenz, nicht Wahrheitsbeweis.
Alle gespeicherten Zonen und die laufende Entitätsbereinigung bleiben erhalten;
vier war der dokumentierte PilotSuite-Bestand am 30.09.2026, keine feste Obergrenze.

`relevant` autorisiert Live- und verfügbare historische Auswertung ohne weitere
Datenfreigabe. Pause, Aufbewahrung, Export und Löschen sind eigene Funktionen.
Legacy-Lernschalter sind noch vorhandene Kompatibilität, kein neues Produktprinzip.
Lernbelege, Präferenzen und Schaltfreigaben dürfen nicht vermischt werden.

## Bewusst später

Adaptive Komfortvorschläge erst bei einem messbaren Vorteil gegenüber festen Regeln.
Keine erfundenen Vertrauensprozente, keine Belohnungsschleife durch eigene Aktionen.
LLM, RAG, native Zusatzintegration und Sprache nur bei belegtem Zusatznutzen;
der Grundbetrieb bleibt lokal und unabhängig davon. HA Assist wird wiederverwendet.

Freigegebene Änderungen brauchen einen konkreten Plan, erneute Vorbedingungen,
erforderliche Sicherung, Verifikation und aktionsspezifische Wiederherstellung.
Weniger sichtbare Komplexität darf diese Schutzmaßnahmen nicht entfernen.

[ARCHITECTURE.md](ARCHITECTURE.md) benennt vorhandene Besitzer und Altlasten;
[ROADMAP.md](ROADMAP.md) begrenzt die nächste Umsetzung auf überprüfbare Nutzerpakete.
