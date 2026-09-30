# Habituszonen: zuerst die Struktur

Verbindliche Produktrichtung vom 30.09.2026, nach Abschluss von Alpha.72.
Nutzerauftrag: PilotSuite vollständig auf saubere Erstellung, Darstellung und
Dokumentation von Habituszonen reduzieren; alles Weitere vorerst ausblenden,
ausdrücklich auch Vergleiche. Alpha.73 ist nach PR #155 und exakter CI installiert;
Releasebeleg: RELEASE_STATE.json. Die reale Abnahme benötigt weiterhin die Anmeldung. Aktueller Umfang: der Nutzer beauftragt ausdrücklich
Entwicklung bis zur realen strukturellen Zonenabnahme/Übernahme. HA und PilotSuite
sollen dieselben Mitglieder und Habitus-Rollen haben. Das erlaubt den geprüften
konkreten Labelabgleich, keine Übernahme von Licht-/Präsenzsteuerung.

## Ein klarer Einstieg

**Zonenübersicht → Zone bearbeiten → Zonendokumentation.**

- **Übersicht:** bestehende Zonen, verständlicher Name, zugeordnete Bereiche,
  Mitglieder und strukturell offene Punkte. Neue Zone anlegen, vorhandene öffnen.
  Kein Anwesenheitsurteil, Vorschlagszähler oder Analyse-Cockpit.
- **Bearbeiten:** HA-Bereiche, Geräte und Entitäten auswählen; vorhandene manuelle
  Zonenlabels einlesen, zusätzliche Mitglieder ergänzen und Habitus-Anzeigerollen
  zuordnen. Herkunft, Mehrfachzuordnung und fehlende Identitäten verständlich zeigen.
  Gemeinsam speichern; HA-Metadatenänderungen vorher konkret bestätigen.
- **Dokumentation:** lesbarer Zonensteckbrief aus derselben gespeicherten Struktur:
  Identität, Bereiche, Mitgliedschaft samt Herkunft, Labelbindung, Rollen,
  bekannte Abweichungen, Änderungsnachweise und offene Strukturfragen. Export und
  Erklärung der Begriffe direkt erreichbar. Keine parallel gepflegte Zonenliste.

Ein Zonenanker kann als vorhandene Rolle dokumentiert werden. Ein neuer Präsenzsensor
oder ein eigenes Helferpaket ist keine Voraussetzung, um die Struktur anzulegen.
„Struktur geprüft“ darf nicht „Präsenz funktioniert“ oder „Steuerung freigegeben“ heißen.
Die konkrete Benennung/Anordnung der Ansichten ist ein Umsetzungsvorschlag; der
verbindliche Umfang ist die Beschränkung auf Struktur, Darstellung und Dokumentation.

## Jetzt aus der Oberfläche nehmen

Präsenzberechnung/-konfiguration, Schatten- und Lichtvergleiche, Replays,
Automationsübernahme, Helferbereitstellung, Licht-/Klima-/Medienmodule, Lernen,
Muster, Routinen, Alltagsbrief und deren Analysekennzahlen. Keine ausgeblendeten
Module über „Alle Bereiche“, alte Deep Links oder gespeicherte Ansichten wieder
zugänglich machen. Alte Links verständlich auf den Zonenweg umlenken; keine
Navigation darf eine Konfiguration oder Betriebsart verändern.

Die konkrete Vorher-/Nachher-Vorschau für einen beauftragten Labelabgleich bleibt
erhalten: Sie erklärt eine Strukturänderung und ist kein Betriebsvergleich.
Verbindungsfehler, strukturelle Konflikte und nötige Wiederherstellung bleiben
zugänglich. Allgemeine Diagnosen dominieren die Zonenoberfläche nicht.

## Bestehendes bewahren, Bedienung neu ordnen

Vorhandene Zone-/Selection-/Context-Stores, stabile IDs und den Plan-/Transaktionsweg
weiterverwenden. Vier gespeicherte Zonen, manuelle Tags, fremde Labels, physische
Bereiche, gespeicherte Modulkonfigurationen und Belege bleiben erhalten. Keine
Datenlöschung, pauschale Migration, neue Engine oder zweite UI mit eigenem Zustand.

Mitgliedschaft, Habitus-Anzeigerolle, Analyse-Relevanz und Schaltrecht bleiben
verschieden. Eine neue strukturelle Zuordnung aktiviert keine Analyse, Publikation
oder Steuerung. Bestehende Rechte werden nicht durch das Ausblenden umgeschrieben.

Ausblenden beendet laufende Hintergrundprozesse nicht. Vor dem Code-Umbau die
bestehenden Laufzeit-/Publikationsabhängigkeiten prüfen. Unbenötigte Frontend-
Abfragen und Renderpfade sollen entfallen. Eine Änderung laufender Ausgabeprozesse
ist ein eigener wirkungsrelevanter Schritt; keine verdeckten Helferzustandswechsel
oder falsche Behauptung, der gesamte Backendbetrieb sei bereits auf Struktur reduziert.

## Abnahme des nächsten Umsetzungspakets

1. Standardstart, bestehende Ansichtspräferenz, alte Deep Links, Vor/Zurück und
   Reload führen nur zu Strukturansichten; kein „Alle Bereiche“-Rückweg.
2. Vorhandene Zone bearbeiten und neue Zone aus Bereichen/manuellen Tags anlegen:
   Mitglieder und Rollen aus demselben Speicher, keine doppelte Dateneingabe.
3. Importwiederholung erhält Abwahlen und Entwürfe. Fehlende/umbenannte/mehrdeutige
   Identitäten bleiben erklärbar; kein stiller Ersatz oder Verlust bei Speichern.
4. Konflikte, HA-Abgleich mit konkreter Bestätigung, Teilfehler und Rückweg bleiben
   im bestehenden Planweg. Navigation allein erzeugt keine Haushaltsänderung.
5. Dokumentation zeigt den tatsächlich gespeicherten Stand; fehlende Informationen
   bleiben offen. Keine Analyseabnahme aus Strukturvollständigkeit ableiten.
6. Browserprüfungen für Mobil/Desktop, Hell/Dunkel, Tastatur, Entwurfserhalt,
   leeren Bestand und Verbindungsverlust; Screenshots tatsächlich ansehen.
   Unnötige Analyseanfragen über Netzwerkmitschnitt im synthetischen Test erkennen.

## Reale Abnahme als aktuelles Ziel, Module nachgelagert

- Angemeldete Abnahme der realen gespeicherten Zonen ist jetzt beauftragt und noch
  offen. Zuerst reale gespeicherte Bereiche, Tags, Rollen und stabile Mitgliedschaft
  lesen, konkrete Abweichungen im bestehenden Plan abgleichen, danach frisch prüfen.
  Zusätzliche HA-Mitglieder nicht still entfernen oder nur durch Rollenähnlichkeit
  zuordnen. Ungeklärte Identitäten bleiben ein benannter Restpunkt.
- Präsenzlogik und Helfer/Sensoren erst nach akzeptierter Zonenstruktur wieder
  einführen, danach Licht. Aktive Lichtsteuerung und Automationsübernahme sind
  weiterhin nicht implementiert oder freigegeben.
- Klima, Multimedia und Mustererkennung bleiben spätere Schritte. Kein Modul
  allein aufgrund vorhandenen Codes wieder sichtbar machen.

Der beendete Nachtlauf bleibt pausiert. Alpha.72 und sein Auslieferungsbeleg bleiben
unverändert. Entwicklung, Veröffentlichung, Installation und Haushaltsabnahme
werden beim kommenden Umbau separat belegt.

## Lokaler Umsetzungspfad und Prüfvertrag

`/api/v1/zones?structure=1` liefert eine leichte Projektion der vorhandenen Stores
für die Übersicht. `/structure` liefert Profil, Identitäten und Strukturplanbelege.
Mit `verify=1` werden die vier nativen HA-Register frisch gelesen, danach die
Zonenrevision und gemeinsame Rollen erneut geprüft. Es gibt keinen zweiten
Abnahmespeicher: der datierte Prüfstand ist lesbar und als JSON exportierbar.
Spätere externe Änderungen erfordern eine neue Prüfung.

`structure_only` am bestehenden Zonenspeichern verhindert Betriebsartänderungen
und erhält frühere Relevanzentscheidungen. Neue Mitglieder werden ignoriert,
bis sie in einer späteren Phase ausdrücklich zur Analyse freigegeben werden.
Entfernung aus der Darstellungsstruktur widerruft bestehende Analyseentscheidungen
nicht still. Jede bestehende Modulkonfiguration bleibt unverändert gespeichert.

Die Produktions-Browserprüfung ist nun `scripts/test_structure_browser.cjs`:
Altlinks, nur strukturelle Hintergrundabfragen, Import/Abwahl/Rollenentwurf,
Navigation/Abbrechen, bestätigter Plan, unabhängiges Rücklesen, Export,
Umbenennung/Verbindungsfehler, neues Label, verlorene Antwort und Rücknahme.
Maintenance/Rescue sowie Auswahl, Review-Notizen und Alltagsbrief als isolierte
Komponenten bleiben in CI. Die früheren sieben vollständigen Modul-UI-Skripte
sind historische Tests des bewusst entfernten Alpha.72-Produkts; ihre alten
Navigationsannahmen gehören nicht zur aktuellen CI. Sie bleiben für späteren
gezielten Wiedereinbau erhalten. Backend-, Modell- und native Protokollregressionen
laufen weiterhin vollständig.

Live-Referenzprüfung am 30.09.2026: Die bestehende HA-Vorlage vererbt sowohl
Zonen- als auch Rollenlabels von Geräten. Rollen bevorzugt explizit an Entitäten
pflegen, aber vorhandene Geräte-Rollen beim Import und Prüfen mitrechnen.
Ein Gerätetagg kann nicht durch Entfernen eines Entitätentags aufgehoben werden.
Widersprechende geerbte Rollen und zusätzliche geerbte Zonenanker blockieren den
Plan bereits vor einer Mutation. Das HA-Template selbst wurde nicht geändert.
