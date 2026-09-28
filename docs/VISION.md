# PilotSuite — ein verständlicher Zonenassistent

Konsolidiertes Zielbild vom 28.09.2026, zur schrittweisen Umsetzung im bestehenden
Projekt. Dies ist kein Nachweis neuer Laufzeitfunktionen. Den Funktionsstand führt
[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md), die Installation
[RELEASE_STATE.json](RELEASE_STATE.json).

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

## Bedienung und Analyse

Im Alltag zuerst Zone, Zustand, Grund, verbleibender Nachlauf und Datenlücke.
Quellenkonfiguration, Verlauf und Diagnose werden bei Bedarf geöffnet. Das Dashboard
„Habituszonen“ bleibt ontologische und gestalterische Referenz, nicht Wahrheitsbeweis.
Alle vier gespeicherten Zonen und laufende Entitätsbereinigung bleiben erhalten.

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
