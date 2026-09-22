# Habitus-Zonen: Konzept und Implementierung

Eine Zone beschreibt einen sinnvollen Beobachtungskontext, keinen zusätzlichen
Home-Assistant-Raum. Beispiel: „Wohnbereich“ kann mehrere HA-Bereiche und einen
Präsenzsensor außerhalb dieser Bereiche enthalten. HA-Zuordnungen bleiben erhalten.

## Kleinstes tragfähiges Modell

| Feld | Bedeutung |
|---|---|
| zone_id | Unveränderliche Identität; neue Zonen erhalten hz_ plus UUID |
| name | Änderbarer Anzeigename, niemals Schlüssel für Entscheidungen |
| area_ids | Referenzen auf HA-Bereiche; liefern dynamisch Kandidaten |
| extra_entity_ids | Explizite zusätzliche Kandidaten, auch ohne HA-Bereich |
| enabled | Zone wird ausgewertet oder pausiert; kein Löschen der Auswahl |
| profile | observe: neutrale Beobachtung; cellar: bestehende Erdkellerregeln |
| revision | Gemeinsamer Versionsstand von Definition und Entitätenauswahl |
| selection | Relevante, ignorierte und ungeprüfte Kandidaten; eigener Aktivierungsmodus |

Ein Speicher, ein Resolver und eine Auswertungskette. Kein zusätzlicher Dienst,
keine HA-Custom-Integration und keine neue parallele Konfiguration erforderlich.
Alle eigenen Definitionen liegen zusammen mit den Entscheidungen in SQLite.

## Mitgliedschaft und Auswertung

1. Kandidaten = Entitäten aus referenzierten Bereichen plus zusätzliche Entitäten.
   HA-Gerätezuordnung wird berücksichtigt; deaktivierte HA-Entitäten werden nicht
   ausgewertet. IDs werden innerhalb der Zone dedupliziert.
2. Neue Zonen starten in der Oberfläche pausiert, mit neutralem Profil und
   bestätigter Auswahl. Eine zusätzliche Entität ist zunächst nur Kandidat.
3. Mit aktivierter Auswahl werden ausschließlich `relevant` markierte Kandidaten
   ausgewertet. Neue Entitäten bleiben ungeprüft. `ignored` wird durch Empfehlungen
   nicht überschrieben. Leere Auswahl ist zulässig und kein HA-Verbindungsfehler.
4. Jede aktive Zone berechnet eigene Moods und Vorschläge. Sensoren verschiedener
   Zonen werden nicht zu einem scheinbaren Raumklima zusammengemittelt.
5. Dieselbe Entität darf mehreren Zonen angehören. Globale Beobachtungszahlen
   zählen ihre ID einmal. Zonenbezogene Vorschläge bleiben getrennt und tragen
   eine stabile Identität aus Regel und Zonen-ID. Sie sind keine Schaltaufträge.

Das neutrale Profil bewertet Verbindungs- und beobachtete Klimadatenqualität,
behauptet aber keine allgemeingültigen Temperatur-/Feuchte-Komfortgrenzen.
Das Erdkellerprofil ist ausdrücklich auswählbar. Physikalische Sensortypen werden
nicht durch freie Rollen überschrieben. Rollen-Vorschläge aus device_class sind
heute sichtbar; bestätigte kontextuelle Rollen wie Referenzsensor oder Hauptsensor
und Gewichtungen sind eine spätere, separat zu prüfende Erweiterung.

## Änderungen und Wiederherstellung

- Definition und Auswahl teilen eine Revision. Konkurrierende Änderungen ergeben
  HTTP 409; kein stilles Überschreiben oder automatisches Zusammenführen.
- Umbenennen behält die Zonen-ID. Entfernte Quellen, fehlende Entitäten und
  deaktivierte Zonen behalten Entscheidungen. Wiederaufnahme derselben ID nutzt
  diese Entscheidungen; fremde oder umbenannte IDs werden nicht automatisch übernommen.
- Deaktivieren ist die reversible Entfernung aus der Auswertung. Endgültiges
  Löschen und Import eines Exports sind bewusst noch nicht implementiert.
- Die Oberfläche bietet JSON-Export aller Definitionen und Entscheidungen,
  ohne aktuelle Zustände, Token oder vollständige HA-Historie.
- Das gemeinsame Änderungsjournal ist auf die letzten 5.000 Transaktionen begrenzt;
  aktuelle Definitionen und Entscheidungen werden durch die Begrenzung nicht gelöscht.

## Migration und Kompatibilität

Schema 3 ergänzt Zonendefinitionen und einen einmaligen Übernahmemarker. Vor einer
Migration von Schema 1 oder 2 erstellt die SQLite-Backup-API eine eindeutig
benannte Sicherung im Add-on-Datenverzeichnis. Änderungen am Schema sind atomar.
Neuere Schemata werden abgewiesen. Ein Downgrade braucht die passende Sicherung.

Die bisherigen `golden_zone_area_ids` werden einmalig in Zonen überführt. Dabei
bleiben ihre IDs, Entscheidungen, Revisionen und Auswahlmodi erhalten; Profil ist
das bisherige Erdkellerprofil. Mehrere bisherige Bereiche werden nun getrennt
ausgewertet. Nach Übernahme ist die Zonenverwaltung maßgeblich: spätere Änderungen
dieser Bootstrap-Option legen keine Zonen neu an und überschreiben keine Definition.
Das gilt auch nach Neustarts. Bestehende HA-Konfiguration wird nicht geschrieben.

## API

- GET /api/v1/zones: Definitionen und letzte zonenbezogene Auswertung
- POST /api/v1/zones: neue Definition, zunächst leere bestätigte Auswahl
- PATCH /api/v1/zones/{zone_id}: Definition ersetzen mit Revision
- GET /api/v1/entity-catalog: Suchkatalog mit HA-Zuordnung und Deaktivierungsstatus
- GET /api/v1/zones/export: Definitionen und Entscheidungen als JSON-Download
- GET/PATCH /api/v1/selections/{zone_id}: vorhandene Auswahl-API, jetzt mit logischer Zonen-ID

Alle Endpunkte unterliegen demselben Ingress-Schutz. Limits: 100 Zonen, 100
Bereichsreferenzen und 500 zusätzliche Entitäten je Definition, 500 Entscheidungen
pro Patch. Neue Referenzen müssen im aktuellen HA-Inventar vorhanden sein;
bestehende fehlende Referenzen dürfen zur späteren Wiederherstellung erhalten bleiben.

## Abnahme und nächste Grenze

Backendtests prüfen Migration, Revisionen, Zonenisolation, überlappende Entitäten,
Neutralprofil, Umbenennen, Deaktivieren, Export und Journalbegrenzung. Der
Browser-Prüflauf prüft zusätzlich Erstellen einer Zone über die Oberfläche.
Dieser Zweig bleibt ein Entwicklungspaket bis CI und Release-Abnahme abgeschlossen
sind. Echte Gewohnheitserkennung, Rollenprioritäten und autonome Aktionen sind
damit nicht implementiert und werden nicht als solche angezeigt.
