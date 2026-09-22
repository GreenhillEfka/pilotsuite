# Nächstes Paket: bewusste Entitätenauswahl

Erweitert um eigenständige Habitus-Zonen: siehe [HABITUS_ZONES.md](HABITUS_ZONES.md).
Der dort dokumentierte Schema-3-Vertrag ersetzt die frühere Bindung an einzelne
HA-Bereiche sowie die folgenden historischen Inkrementbeschreibungen.
Zoneneditor, separate Auswertung, Export und begrenztes Journal sind implementiert.

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

Der Entwicklungszweig enthält Auswahlspeicher, Inventar-API, Backendtests und
die erste Auswahloberfläche: Checkboxen, Suche, Statusfilter, Zonenwahl,
Empfehlungsvorschau, Speichern/Verwerfen und Konfliktanzeige. Entwürfe bleiben
bei Dashboard-Abgleichen erhalten; ein Zonenwechsel ist bei Änderungen gesperrt.
Empfehlungen überschreiben keine explizit ignorierten Entscheidungen.
Die Auswertung ist jetzt über einen gemeinsamen Filter angebunden.
`applied_to_inference` zeigt den gespeicherten Aktivierungsmodus der Zone.
Standard ist weiterhin der bisherige automatische Umfang. Erst ein explizit
bestätigtes Speichern mit `active: true` schließt ungeprüfte und ignorierte
Entitäten aus Neuronen, Moods und Vorschlägen aus. Eine leere Auswahl verändert
nicht die HA-Verbindungsbereitschaft. Rückkehr zu `active: false` braucht in der
Oberfläche ebenfalls eine Bestätigung. Inventar bleibt ungefiltert sichtbar.
Browserabnahme, Export und Journal-Aufbewahrung sind noch offen. Nicht als fertige
Checkbox-Funktion veröffentlichen oder auf HA installieren.

SQLite-Schema 2 wird neu angelegt. Beim Upgrade von Schema 1 wird zuerst eine
eindeutige SQLite-Sicherung `selections.v1.<id>.bak` im Datenverzeichnis erzeugt,
dann die Modustabelle transaktional ergänzt. Bestehende Entscheidungen und
Revisionen bleiben erhalten; keine Zone wird durch Migration aktiviert.
Unbekannte oder neuere Schemata werden abgewiesen statt überschrieben.
Ein Downgrade des Entwicklungszweigs braucht die passende Datenbanksicherung;
ältere Entwicklungsstände können Schema 2 nicht lesen.
Journal und Entscheidungen werden in derselben Transaktion gespeichert.
Keine echten Haushaltsdaten gehören in Tests oder öffentliche Dokumentation.

## API-Vertrag des ersten Inkrements

GET liefert `zone_id`, `revision`, `items`, `missing`, `resolved` und
`applied_to_inference`. Empfehlungen sind unverbindliche Domain-/Kategorie-
Heuristiken, keine Zustimmung. Diagnose-/Konfigurationsentitäten und Buttons
werden nicht empfohlen. Fehlende Zustände dürfen trotzdem überprüft werden.

PATCH erwartet `revision`, `changes` und optional den booleschen Wert `active`, etwa:

```json
{"revision": 0, "changes": {"sensor.example_temperature": "relevant"}}
```

Maximal 500 Entscheidungen pro Patch; falsche Nutzdaten ergeben 400,
Eine reine Modusänderung erlaubt `changes: {}`. Aktivierung und Entscheidungen
teilen Revision und Transaktion, inklusive Änderungsjournal.
Revisionskonflikte 409. Wiederholungen ohne Änderung erhöhen die Revision nicht.
Entscheidungen gelten nur für diese Zone.

## Verifikation des zweiten Inkrements

- 39 Python-Tests und Repository-Vertragsprüfung erfolgreich, einschließlich
  Mehrzonen-Isolation und Zustandsereignissen bei aktiver Auswahl.
- Vier JavaScript-Modelltests erfolgreich; in CI aufgenommen.
- Optionaler Browsertest: `node scripts/test_selection_browser.cjs` (benötigt
  Playwright mit Chromium). Lokal blockiert: Browserdownload lieferte kein
  gültiges ZIP-Archiv. Eigener CI-Browserjob mit Playwright 1.62.1 ergänzt. Deckt nach
  erfolgreichem Start Entwurf, Speichern, Konflikt, Verwerfen, Suche, schmale
  Ansicht und Ingress-Prefix ab. Keine Behauptung einer bestandenen Browserabnahme.
- Keine Installation, kein Versionssprung. Nächste Schritte: CI-Browserabnahme,
  Export/Aufbewahrung und Release-Härtung.
