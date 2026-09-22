# Nächstes Paket: bewusste Entitätenauswahl

Status: in Entwicklung, kein Release und keine Installationsfreigabe.
Ausgangspunkt: 0.1.0-alpha.4. Bestehende Installation bleibt unverändert.

## Ziel und Grenzen

Pro konfigurierter Zone entscheidet der Nutzer, welche erkannten Entitäten
PilotSuite auswerten soll. Home Assistant bleibt Quelle für Zustände und
Zuordnungen. Relevanz ist niemals eine Schaltfreigabe. Keine HA-Registry,
Automationen oder Geräte werden verändert. Kein neues paralleles Projekt.

## Arbeitspakete und Abnahme

1. **Persistenz und API (begonnen):** SQLite im Add-on-Datenverzeichnis;
   Entscheidungen `relevant`, `ignored`, `unreviewed`; Revision je Zone;
   atomare Teiländerungen mit Journal; veraltete Revision ergibt HTTP 409.
   GET/PATCH `/api/v1/selections/{area_id}` nur hinter bestehendem Ingress-Schutz.
   Unbekannte Zonen und fremde Entitäten dürfen nicht beschrieben werden.
2. **Auswahloberfläche:** Checkbox je Entität, sichtbarer Prüfstatus, Suche,
   Filter und Zonenwahl. Name, ID, Zustand und Rollen-Vorschlag anzeigen.
   „Empfohlene auswählen“ ist eine Vorschau, kein automatisches Speichern.
   Änderungen explizit speichern oder verwerfen; Konflikte verständlich anzeigen.
   Neue Entitäten bleiben ungeprüft, nicht stillschweigend relevant.
3. **Einheitliche Auswertung:** bestätigte Auswahl steuert Neuronen, Moods und
   Vorschläge über genau einen Filter. HA-Verbindungsstatus bleibt unabhängig.
   Umstieg vom bisherigen automatischen Umfang braucht eine explizite Bestätigung
   je Zone; keine unbemerkte Änderung bestehender Ergebnisse. Leere Auswahl ist
   ein verständlicher Zustand, kein vermeintlicher HA-Ausfall.
4. **Lebenszyklus:** Entscheidungen bleiben nach Neustart erhalten. Verschwundene
   oder deaktivierte Entitäten werden separat angezeigt, nicht gelöscht.
   Wiederkehr derselben ID übernimmt die Entscheidung; Umbenennungen brauchen
   Bestätigung und werden nicht automatisch einer neuen ID zugeordnet.
   Rollen zunächst nur Vorschläge, keine vermeintlich trainierte Klassifikation.
5. **Release-Härtung:** UI- und Integrationstests, Schema-/Rollback-Prüfung,
   Journal-Aufbewahrung und Export festlegen, Dokumentation synchronisieren.
   Erst vollständiges Paket versionieren, CI inklusive Container-Build prüfen,
   app-eigenes Backup verifizieren, dann Update und HA-Ingress-Smoke-Test.

## Aktueller Implementierungsstand

Dieser erste Inkrement enthält Auswahlspeicher, Inventar-API und Backendtests.
`applied_to_inference: false` kennzeichnet ausdrücklich, dass gespeicherte
Entscheidungen noch nicht die Auswertung verändern. Oberfläche, Anbindung der
Auswertung, Export und Journal-Aufbewahrung sind noch offen. Nicht als fertige
Checkbox-Funktion veröffentlichen oder auf HA installieren.

SQLite-Schema 1 wird neu angelegt; unbekannte oder neuere Schemata werden
abgewiesen statt überschrieben. Das ist noch kein allgemeines Migrationssystem.
Journal und Entscheidungen werden in derselben Transaktion gespeichert.
Keine echten Haushaltsdaten gehören in Tests oder öffentliche Dokumentation.

## API-Vertrag des ersten Inkrements

GET liefert `zone_id`, `revision`, `items`, `missing`, `resolved` und
`applied_to_inference`. Empfehlungen sind unverbindliche Domain-/Kategorie-
Heuristiken, keine Zustimmung. Diagnose-/Konfigurationsentitäten und Buttons
werden nicht empfohlen. Fehlende Zustände dürfen trotzdem überprüft werden.

PATCH erwartet ausschließlich `revision` und `changes`, etwa:

```json
{"revision": 0, "changes": {"sensor.example_temperature": "relevant"}}
```

Maximal 500 Entscheidungen pro Patch; falsche Nutzdaten ergeben 400,
Revisionskonflikte 409. Wiederholungen ohne Änderung erhöhen die Revision nicht.
Entscheidungen gelten nur für diese Zone. Der nächste konkrete Schritt ist die
Auswahloberfläche mit Speichern/Verwerfen auf diesem Vertrag.
