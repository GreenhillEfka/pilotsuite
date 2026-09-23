# Prüfnotizen für Routineentwürfe

Entwicklungsstand: separat geprüfter Kandidat; nicht veröffentlicht oder installiert.
Die letzte dokumentierte Installation ist alpha.21. Diese Fortsetzung konnte HA-MCP
nicht aufrufen; keine neue Live-Abnahme oder Sicherung wird behauptet.

## Bedienung

Beim Routineentwurf bestehende Automationen vergleichen, einen Treffer im Detail
prüfen und **Bewertung festhalten** wählen. Die drei Bewertungen sind **Offen**,
**Änderungsbedarf** und **Manuell geprüft – keine Freigabe**. Ein optionaler Text
beschreibt die eigene Einschätzung; maximal 2000 Zeichen, keine Zugangsdaten.

Bewertung und Aktualität sind unabhängig. Nach dem Neuladen ist der gespeicherte
Automationsstand zunächst **noch nicht erneut geprüft**. Eine explizite aktuelle
Detailprüfung kann nur bestätigen, dass die Bewertung zum zuletzt gelesenen Stand
passt. Sie beweist weder laufende Unverändertheit noch Gleichwertigkeit, Sicherheit
oder Autorisierung. Die abgeleiteten fachlichen Prüfpunkte bleiben offen.

Beim Speichern wird dieselbe ausgewählte Automation erneut über den bestehenden,
begrenzten Prüfpfad gelesen. Hat sich ihr Fingerabdruck geändert, wird nicht
überschrieben. Der Text bleibt im Editor erhalten. **Prüfstand neu laden (Text
behalten)** zeigt die aktuelle Detailprüfung; nach erneuter fachlicher Bewertung
kann ausdrücklich gespeichert werden. Bei konkurrierenden Bewertungen wird nicht
still automatisch zusammengeführt. Die Oberfläche warnt vor einem bewussten
Ersetzen; die Revision muss dafür erneut geladen werden.

Notizen bleiben bei Änderungen am Entwurf, Quellenwechsel, Musterablauf und
Lernreset erhalten, aber ihr Bezug wird als veraltet gekennzeichnet. Löschen ist
ein eigener bestätigter Schritt; es verändert weder HA noch Lernbelege. Das Löschen
des ganzen Entwurfs löscht auch seine Notizen und prüft zusätzlich deren Revision.

## Ein Besitzer, begrenzte Daten

PlanStore besitzt die Notizen. Das ReviewNotesMixin ist nur eine Aufteilung seiner
Implementierung, keine zweite Instanz, Datenbank, Lernengine oder Freigabelogik.
Die bestehende SQLite-Initialisierung migriert Schema 7 auf 8 und legt vorher eine
`.bak` über die SQLite-Backup-API an. Die zusätzliche Tabelle
`routine_review_notes(draft_id, revision, records)` hält bis zu 20 ausgewählte
Automationsbewertungen pro Entwurf; das bestehende Limit von 100 Entwürfen bleibt.
Keine stille Verdrängung. Die letzte Notiz wird pro ausgewählter Automation
ersetzt; dies ist kein unbegrenztes historisches Bewertungsjournal.

Gespeichert werden eigene Bewertung/Text, Entwurfs-/Zonenrevision, Automations-ID,
Konfigurationsfingerabdruck, ein Fingerabdruck von Muster-ID/Quellen/Zielen und
Zeitpunkte. Keine Rohkonfiguration, Templates, HA-Kontext-/Benutzer-IDs oder
kopierten statistischen Belege. Die Arbeitsfläche ist gemeinsam genutzt; eine
Notiz belegt keine authentifizierte persönliche Autorenschaft. Eigene Texte können
private Routinen enthalten und sind im expliziten Entwurfs-/Kontextexport enthalten.

`review_revision` ist unabhängig von der Entwurfsrevision. Validierung und Schreiben
verwenden eine SQLite-Transaktion mit Schreibsperre. Eine leere Restzeile behält die
Review-Revision nach dem Löschen der letzten Notiz: ein alter Tab kann nicht mit
Revision 0 nach Löschen/Neuanlage versehentlich wieder gültig werden.

## HTTP-Vertrag

Bestehender Ingress-Schutz unverändert; keine neue Berechtigung und kein offener Port.

`GET /api/v1/zones/{zone_id}/drafts/{draft_id}/review-notes` liest nur eigene
PilotSuite-Daten. Antwortschema `pilotsuite-review-notes-v1`: `revision`, `items`,
`limit`, `execution`. Items haben `stale`, `stale_reasons` und stets
`config_status: not_rechecked`. GET löst keinen HA-Scan aus. HEAD ist schreibfrei.

`PUT` an dieselbe Route erfordert genau:

```json
{
  "revision": 2,
  "zone_revision": 3,
  "review_revision": 0,
  "automation_id": "automation.synthetic",
  "config_fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "disposition": "needs_change",
  "text": "Manuellen Vorrang noch klären."
}
```

IDs und Werte im Beispiel sind synthetisch, keine Haushaltszuordnung. Unbekannte
Felder, Bool-Werte als Revisionen, unsichere Ganzzahlen, ungültige IDs/Fingerprints,
zu lange Texte, Steuerzeichen und ungültige Unicode-Surrogate werden abgewiesen.
Revisionen sind nichtnegative sichere Ganzzahlen; Entwurfsrevision mindestens 1.

Vor Netzverkehr bekannte Revisionskonflikte ablehnen. Danach bestehenden
`compare_automations(..., inspection=True)` verwenden; er prüft aktuelle direkte
Bezüge, genau die gewählte Automation sowie den Entwurfs-/Zonenbezug. Keine
Netzwerkoperation hält die Projektionssperre. Unmittelbar beim SQL-Schreiben werden
alle Revisionen, Quellen/Ziele, Fingerprint und maximal 30 Sekunden seit Beginn der
erneuten Prüfung kontrolliert, einschließlich Wartezeit auf die Schreibsperre.
Der Prüfbericht stammt vom Server, niemals aus dem PUT-Body. Erfolgsantwort:
`review_notes` plus der aktuelle transiente `automation_review`.

HA und SQLite bilden keine gemeinsame Transaktion: Änderungen direkt nach dem
HA-Lesen bleiben möglich. Daher stets nur Bezug auf den **zuletzt gelesenen Stand**,
keine zeitlich unbegrenzte Verifikation oder Ausführungsentscheidung.

`DELETE` derselben Route erfordert genau `revision`, `zone_revision`,
`review_revision`, `automation_id`. Kein HA-Konfigurationslesen nötig. Die
Review-Revision steigt auch beim Löschen. Entwurfs-DELETE akzeptiert zusätzlich
`review_revision`; alte Clients ohne diesen Wert dürfen nur Entwürfe ohne bisherige
Bewertungen löschen. Sonst 409 statt stiller Datenverlust.

400: ungültige Eingabe/Scope/Limit; 409: geänderte oder abgelaufene Prüfgrundlage;
503: erneute HA-Prüfung nicht verfügbar. Keine privaten Upstream-Fehler ausgeben.
Erfolgreiche Notizantworten und kontrollierte 503-Antworten verwenden `no-store`.
Keine Endlosschleife, automatische Wiederholung oder Berechtigungsanhebung.

## Tests und Liefergrenze

Synthetische Unit-, API-, SQLite-Migrations-/Konflikt- und Browserfälle prüfen
Persistenz, Ablauf, Scope, Löschen, unveränderte Lernbelege, dauerhaft gesperrtes
Apply, Eingaben, Textverlust und sichere DOM-Ausgabe. Der separate Editor-Browsertest
verwendet einen synthetischen Shell-/API-Harness; die bestehende komplette
Selection-Browsersuite prüft zusätzlich das Laden in der tatsächlichen App-Oberfläche.
Testläufe, vollständige CI und Live-Ingress-Abnahme werden getrennt dokumentiert.

Vor Veröffentlichung: Live-Version und Quellenbezug erneut lesen, frische
PilotSuite-only-Sicherung von alpha.21 samt Daten/Optionen abschließen und Details
prüfen, neue Release-Version vergeben, Versionsmarker/Changelogs/Release-Preflight
und exakte PR-/Main-CI prüfen. Wegen aktivierter automatischer App-Updates nicht
vor dem Sicherungsschritt auf `main` veröffentlichen. Kein Live-Restore-Test.
Die Schema-8-Datei nicht mit alpha.21 überschreiben oder ungeprüft zurückkopieren;
Regressionserholung nur über den zuvor verifizierten PilotSuite-Teilrestore.
