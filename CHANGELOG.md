# Changelog

## [0.1.0-alpha.53] - 2026-09-27

### Ruhige Zonenansicht beim Hintergrundabgleich
- Unveränderte Antworten behalten die bestehende Darstellung; bei geänderten
  Live-Daten bleibt die Leseposition erhalten.
- Bedienelemente, Fokus und geöffnete Quell- und Musterhinweise überleben
  automatische Aktualisierungen. Aktuelle Quellen und Sitzungsverlauf sind
  für eine kürzere Zonenansicht einklappbar.
- Der synthetische Browserlauf prüft den zweimaligen passiven Abgleich und
  trennt sichtbare historische Charts von eingeklappten Live-Verläufen.
- Keine HA-Konfiguration, Zustimmung, Automation oder Geräteaktion wird verändert.

## [0.1.0-alpha.52] - 2026-09-27

### Aktivierungsstatus in der Automations-Detailprüfung
- Deaktivierte oder dynamisch aktivierte Auslöser und Dienstaufrufe bleiben als
  Fundstellen sichtbar, erfüllen aber nicht länger einen bestätigten direkten
  Quellen- oder Zielbezug. Quellen-/Ziellücken bleiben dadurch offen, statt von
  einem Schritt geschlossen zu werden, der strukturell nicht sicher aktiv ist.
- Der Status wird durch verschachtelte `choose`-, `if`-, `repeat`-,
  `parallel`-, Bedingungs- und Wartezweige vererbt. Ein aktiver unabhängiger
  Geschwisterschritt bleibt weiterhin ein bestätigter Bezug.
- Die bestehende Oberfläche unterscheidet strukturell aktive, deaktivierte und
  dynamisch/unbekannte Fundstellen. Der Laufzeitstatus der gesamten Automation
  bleibt ausdrücklich ungeprüft.
- Die Präsenz-Übernahmeanalyse verwendet dieselbe bestätigte Projektion; ältere
  synthetische Verträge bleiben kompatibel.

### Grenzen und Prüfung
- Rein lesende, flüchtige Auswertung bereits ausdrücklich gelesener
  Automationskonfigurationen. Keine HA-Automation wird aktiviert, deaktiviert,
  geändert oder ausgeführt; allgemeines Apply und produktive Übernahme bleiben zu.
- Synthetische Einheits-, API- und Browserregressionen decken deaktivierte,
  dynamische, verschachtelte und konkurrierende Fundstellen ab.
- Lokal bestehen 567 Python-, 68 JavaScript- und 62 API-/Repository-Verträge;
  der vollständige gepinnte Chromium-Lauf bleibt zusätzlich verbindliches CI-Gate.

## [0.1.0-alpha.51] - 2026-09-27

### Vollständige statische Ereignisfilter im Automationsvergleich
- Der bestehende Strukturprüfer erkennt einen literalen `entity_id`-Filter unter
  `event_data` eines Ereignistriggers als direkte Quellenreferenz. Eine passende
  Bestandsautomation wird dadurch nicht länger gleichzeitig gefunden und fälschlich
  mit einer Quellenlücke erklärt.
- Ereignisnutzdaten einer Aktion bleiben absichtlich opak und werden nicht als Ziel
  ausgegeben. Dynamische oder ungültige Filter bleiben unbekannt, öffnen die
  Quellenprüfung und geben keinen privaten Vorlageninhalt zurück.
- Der Paket-Hinweis in der App-Dokumentation nennt nur noch seine eigene Version und
  verweist für Installationsbelege auf `RELEASE_STATE`, statt nach Auslieferung einen
  veralteten Kandidatenstatus zu behaupten.

### Grenzen und Prüfung
- Ausschließlich read-only Auswertung bereits ausdrücklich gelesener
  Automationskonfigurationen; keine Automation, Zone, Entität, Zustimmung oder
  Geräteausführung wird geändert. Allgemeines Apply bleibt geschlossen.
- Zwei synthetische Regressionen erhöhen den lokalen Stand auf 562 Python-Tests;
  68 JavaScript- und 62 API-/Repository-Verträge bleiben grün.

## [0.1.0-alpha.50] - 2026-09-27

### Wiederanlaufsichere eigene Ausgangspakete
- Helfer-Anlagebelege bewahren Erstellungsantwort und unabhängige Registry-Identität
  gemeinsam auf. Ein späterer Read-back überschreibt den stabilen Ursprungsbeleg nicht.
- Nach Prozessabbruch kann ein bestätigtes Paket exakt belegte eigene Ausgaben erneut
  lesen, als vorhanden bestätigen und noch nicht begonnene Schritte fortsetzen. Bereits
  vollständig angelegte Pakete werden ohne erneute HA-Anlage an die Zone gebunden.
- Namen, technische Ziel-IDs oder ähnliche Konfiguration allein beweisen kein Eigentum.
  Fehlender oder mehrdeutiger Beleg bleibt `unknown`; der Schreibschritt wird nicht
  wiederholt. Zonenrevision und alle Identitäten werden vor der Bindung erneut geprüft.

### Grenzen und Prüfung
- Keine bestehende Entität wird adoptiert, umbenannt oder gelöscht. Erstellung schaltet
  den Publisher nicht ein und erteilt weder Geräte- noch allgemeines Apply-Recht.
- Vier neue synthetische Neustart-/Belegregressionen erhöhen den vollständigen lokalen
  Stand auf 560 Python-Tests; 68 JavaScript-Vertragstests bleiben grün. Haushalt und
  installierte Alpha.49 blieben bei der Entwicklung unverändert.

## [0.1.0-alpha.49] - 2026-09-27

### Zoneninstanz, Daten und Ordnung — Entwicklungskandidat
- Neuer Zonen-Konfigurator auf dem vorhandenen Präsenzkern: Dauerpräsenz, Impulse,
  optionale Nutzungsindizien, explizite Abdeckungsgruppen, Start-/Haltewirkung und
  zeitlich begrenzte Nachläufe. Keine unabhängige zweite Sensorwahrheit.
- Relevanz autorisiert die neue Live- und Recorder-Zustandsauswertung ohne zusätzliche
  Lern- oder Historienzustimmung. Automatisch zunächst 24 Stunden in begrenzten Paketen;
  ältere Intervalle sind bis 31 Tage je Abruf direkt auswertbar. Aufzeichnungslücken
  werden nicht als Abwesenheit oder Nullwerte ausgegeben.
- Aktuelle Quellen, Sitzungsverlauf und historische Mess-/Zustandsreihen mit Einheiten,
  Datenlücken, Tabellen und getrennten kategorialen Zuständen. Keine erfundenen Kurven.
- Dauerhafte Pläne für neue eigene Boolean-/Timer-/Gültigkeitshelfer und einen öffentlichen
  Template-Anwesenheitssensor. Erstellung aktiviert die Veröffentlichung nicht. Der
  Publisher prüft Identitäten und Rückleseergebnisse; unklare Ausgänge werden ausgesetzt.
- Anzeigenamen und sechs Habitus-Rollenlabels in einem bestätigten Plan vereinheitlichen,
  mit Vorherzustand, unabhängiger Prüfung und expliziter konfliktsicherer Rücknahme.
  Physische Bereiche und fremde Labels bleiben erhalten; vorhandene Zonenanker blockieren
  eine doppelte Ausgangsanlage. Technische ID-Migration bleibt gesondert gesperrt.
- Neue synthetische Store-/HTTP-/Transporttests und eine zusätzliche tatsächliche
  Anwendungs-Browsersuite (deren lokale Navigation administrativ blockiert war).
- Ein bestehender Test nahm zufällig an, dass zwei aktuelle Zeitpunkte im gleichen
  Zweistundenfenster liegen. Auf unveränderter Alpha.48 reproduziert; deterministisch
  fixiert und eine zusätzliche Grenzprüfung ergänzt, keine Produktionslogik abgeschwächt.

### Grenzen
- Kandidat, nicht installiert. Keine Hauskonfiguration oder Entität in dieser Entwicklung
  verändert. Browser-, Container-, exakte Remote-CI und echte HA-Protokollabnahme fehlen.
- Bestehende Automationszuständigkeit wird nicht automatisch übernommen. Vorhandene
  Ausgangshelfer werden nicht nach Namen adoptiert, technische ID-Referenzen nicht blind
  migriert. Legacy-Lernfelder bleiben für ältere Ansichten kompatibel, sind aber keine
  Freigabesperre des neuen Zonenpfads. Ein vollständiger adaptiver Lerner folgt separat.

## [0.1.0-alpha.48] - 2026-09-27

### Live-Schattenvergleich und Lichtbedarf
- Expliziter Start und Stopp je bestehender Habitus-Zone. Bestätigte Rohquellen
  treiben den vorhandenen Präsenzkern; der HA-Raumstatus dient nur zum Vergleich.
- Getrennte Signaltypen für Dauerpräsenz und Bewegungsimpulse, gespeicherter
  Nachlaufzeitpunkt und Wiederanlauf ohne stillschweigende Verlängerung.
- Quellenalter, unbekannte Zustände, geänderte Identitäten und manuelle Sperren
  bleiben sichtbar. Eine geänderte Grundlage erfordert erneute Bestätigung.
- Lichtbedarf verwendet die vorhandene begrenzte Richtlinie, ausdrücklich erklärte
  Außenhelligkeit und gewählte Atmosphäre. Alle Stellwerte bleiben Vorschläge.
- Einstellungen und letzter Betriebszwischenstand liegen im bestehenden ContextStore.
  Keine neue Historie, Lernerlaubnis, HA-Geräteaktion oder Automationsübernahme.
- Neue API-/Store- und Browserregressionen ergänzen alle vorhandenen Prüfungen.
  Der historische Herkunftsfix aus PR102 bleibt erhalten.

## [0.1.0-alpha.47] - 2026-09-27

### Herkunft historischer Belege
- Eine Historienzeile zählt nur noch, wenn ihr Entity tatsächlich zu den freigegebenen
  Quellen des zugehörigen Importbelegs gehört und ihr Zeitpunkt strikt innerhalb des
  autorisierten Importfensters liegt.
- Selbst formal gültige zusätzliche Herkunftszeilen können die bestätigte Anzahl eines
  Imports nicht überschreiten. Die aktuell erhaltene Zahl wird aus gültiger Herkunft
  abgeleitet, statt einem möglicherweise veralteten Zähler im Beleg zu vertrauen.
- Ausgeschlossene Herkunft und abgeleitete Zähler erscheinen in den bestehenden festen
  Integritätszählern. Die Meldung unterscheidet diese Lesebegrenzung von der normalen
  14-Tage-Aufbewahrung.

### Grenzen
- Keine Schemaänderung, neue Historienabfrage, Sammlung, Zustimmung, Präferenz,
  HA-Konfiguration oder Geräteausführung. Allgemeines Apply bleibt gesperrt.

## [0.1.0-alpha.46] - 2026-09-27

### Integrität des vollständigen Lernberichts
- Aktivierungs-, Historien-, Import-, Abdeckungs-, Feedback- und Kontextzeilen werden
  beim Lesen erneut auf ihren jeweiligen Vertrag und Zeitraum begrenzt. Beschädigte
  Importbelege können den Bericht weder abbrechen noch `NaN` oder unbekannte Felder
  in JSON-Ausgaben tragen.
- Nicht zuordenbare Historienherkunft zählt nicht als historischer Beleg. Unbekannte
  Herkunft wird konservativ als `unknown` normalisiert; unbrauchbare Zeilen werden
  nicht als Beobachtung oder Präferenz gewertet.
- Der Bericht weist ausgeschlossene oder normalisierte Zeilen mit festen Zählern aus.
  Die Oberfläche erklärt diesen Zustand, ohne die Integritätsmeldung als Reparatur
  auszugeben; die normale Aufbewahrungsgrenze bleibt davon getrennt wirksam.

### Grenzen
- Keine Schemaänderung, neue Sammlung, Zustimmung, Feedbackänderung, HA-Konfiguration
  oder Geräteausführung. Allgemeines Apply bleibt gesperrt.

## [0.1.0-alpha.45] - 2026-09-27

### Begrenzter Export gespeicherter Kontextbelege
- Einzelne ältere Kontextbelege werden beim Lesen auf den dokumentierten Licht- und
  Helligkeitsvertrag projiziert. Unbekannte Zusatzfelder gelangen nicht mehr in den
  Export; Quellen, Status und optionale Erfassungszeit werden streng geprüft.
- Nicht-endliche oder typfremde Werte bleiben auch im Rohbeleg unbekannt. Beschädigte
  JSON-Zeilen und ungültige Zeitstempel brechen weder Zonenbericht noch Export ab.
- Gültige ältere Belege ohne historisches Statusfeld bleiben nutzbar. Es findet keine
  Löschung oder stille Umschreibung der gespeicherten Daten statt.

### Grenzen
- Keine neue Datensammlung, Migration, Zustimmung, Präferenzänderung oder
  Geräteausführung. Allgemeines Apply bleibt gesperrt.

## [0.1.0-alpha.44] - 2026-09-27

### Integrität historischer Lernkontexte
- Nicht-endliche, negative oder typfremde Luxwerte können weder beim aktuellen
  Lernkontext noch in vorhandenen Kontextfenstern als bekannter Wert oder Median
  erscheinen. Die Projektion bleibt strikt JSON-konform.
- Ungültige Zeitstempel und beschädigte Quellenlisten werden an der Berichtsgrenze
  kontrolliert verworfen, statt den gesamten Zonenbericht abzubrechen oder beliebige
  Werte als Quellen zu übernehmen.
- Ein gültiges Präsenzereignis bleibt erhalten, wenn ausschließlich sein optionaler
  Kontext unbrauchbar ist; der fehlerhafte Kontext wird nicht gespeichert.

### Grenzen
- Keine neue Sammlung, Migration, Lernfreigabe oder Geräteausführung. Vorhandene
  gültige Evidenz, Nutzerfeedback, Rollen und Home-Assistant-Konfiguration bleiben
  unverändert.

## [0.1.0-alpha.43] - 2026-09-27

### Integrität numerischer Beobachtungen
- Nicht-endliche Zahlen sowie unmögliche Temperatur-, Feuchte- und Luxwerte werden
  auch an der Zonenzusammenfassung erneut als ungültig behandelt. Sie können weder
  einen verfügbaren Messwert noch eine scheinbar nutzbare Lichtquelle ergeben.
- Ungültige Einzel- und Vergleichsmessungen werden als `null` mit ungültiger Qualität
  projiziert. Dadurch bleiben API-Antworten standardkonformes JSON, ohne einen
  fehlenden Wert als Null oder unauffällig umzudeuten.
- Der aktuelle Lichtcheck gibt für eine inkonsistente Helligkeitszusammenfassung
  ausdrücklich „nicht verfügbar“ aus und führt zur Quellenprüfung.

### Grenzen
- Keine neue Datenerhebung, Speicherung, Lernfreigabe oder Geräteausführung. Rollen,
  Automationen und Home-Assistant-Konfiguration bleiben unverändert.

## [0.1.0-alpha.42] - 2026-09-27

### Aktueller Licht-Entscheidungscheck
- Verbindet erst nach einem ausdrücklichen Klick den aktuellen kanonischen Zonenstand
  mit tatsächlich gelesenen, passenden Home-Assistant-Automationsstrukturen.
- Trennt konfigurierte von aktuell nutzbaren Quellen, Innen-Helligkeit von nicht
  bestätigter Außenhelligkeit sowie Transport-Aktualität von physischer Messaktualität.
- Zeigt genau einen sicheren nächsten Schritt. Geänderte Revisionen oder Rollen
  verwerfen das Ergebnis; Reload, GET und verspätete Antworten lösen keine Prüfung aus.

### Grenzen und Prüfung
- Das Ergebnis wird nicht gespeichert, bewertet weder Duplikat noch Sicherheit und
  gewährt keine Ausführung. Es ändert keine HA-Konfiguration, Automation, Rolle,
  Lernfreigabe oder Geräteaktion.

## [0.1.0-alpha.41] - 2026-09-27

### Integrität der Lichtvorschau
- Weist zugeordnete und aktuell nutzbare Leuchten, Innen-Luxquellen und binäre
  Helligkeitssignale getrennt aus. Keine dieser Quellen wird ohne eigenen
  Herkunftsnachweis als Außen-/Tageslichtreferenz bestätigt.
- Die Oberfläche erklärt sichtbar, dass Szenario-Luxwerte synthetisch sind und
  Innen-Lux oder Eigenlicht keine Außenhelligkeit belegen.
- Fehlende aktuelle Leuchtenhelligkeit hält die Vorschau jetzt an, statt den Fall
  fälschlich als fehlende Gerätefähigkeit zu bezeichnen. Inkonsistente oder
  rückwärts laufende Zwischenstände werden abgewiesen.

### Grenzen
- Weiterhin keine Haushaltsmessung, Persistenz, HA-Konfigurationsänderung,
  Lernfreigabe oder Geräteausführung. Bestehende Automationen bleiben unangetastet.

## [0.1.0-alpha.40] - 2026-09-27

### Tageslicht- und Stimmungsvorschau
- Erweitert den vorhandenen reinen Licht-Policy-Besitzer um stabile Tageslichtbänder,
  Totzone, Mindestintervall und begrenzte Helligkeitsschritte. Lux und Prozentwerte
  bleiben unterschiedliche Größen; fehlendes Lux wird nicht als Dunkelheit gedeutet.
- Sechs fest definierte synthetische Szenarien erklären Tageslichtwechsel,
  Grenzschwankungen, manuelle Bedienung, fehlende Referenz, nächtliches Verlassen
  und eingeschränkte Leuchtenfähigkeiten.
- Die bestehende Zonenoberfläche zeigt die Vorschau nur nach einem ausdrücklichen
  Klick. Antworten sind an Zone und Revision gebunden; Reload führt nichts aus.

### Grenzen und Prüfung
- Kein Haushaltswert wird für die Vorschau gelesen oder gespeichert. Die API gibt
  ausschließlich Eigenschaften wie `on`, Helligkeitsprozent und Farbtemperatur aus,
  niemals Dienstnamen oder Ausführungsrecht.
- Public Presence Runtime und allgemeines Apply bleiben geschlossen. Keine HA-
  Konfiguration, Automation, Rolle, Lernfreigabe oder Geräteaktion wird geändert.

## [0.1.0-alpha.39] - 2026-09-27

### Deterministic presence kernel and explanation replay
- Persist the bounded presence checkpoint in the existing zone context: state,
  generation, grace deadline, last activity time and reason. Source changes and
  resets discard this operational basis; savepoints still exclude it.
- Distinguish motion pulses from continuous presence. A restart preserves the
  existing deadline instead of extending it; unknown sources or dependencies never
  become vacancy, and a cold all-clear start does not invent a grace interval.
- Add an allowlisted synthetic scenario replay to the existing presence workspace.
  It runs only after an explicit click, stores nothing, reads no household history
  and cannot grant or invoke execution.
- Prevent non-activation learning events from skipping the dormant runtime
  reconciliation path. The public runtime activation and general Apply gates remain
  closed.

### Validation boundaries
- Synthetic kernel, persistence, revision, API and browser regressions cover restart,
  expiry, pulses, unknowns, invalid values, stale revisions and zero replay mutations.
- No HA configuration, automation, actor, role, consent or productive learning change.

## [0.1.0-alpha.38] - 2026-09-27

### Presence evidence and configuration clarity
- Propagate stream-frame acceptance from WorldModel to the existing learning path.
  Older/equal/duplicate, misaddressed and malformed frames cannot create activity
  records after the projection refused them. Guard stale removal frames as well.
- Keep a valid delayed activation, but withhold each light/lux context channel if
  its projected source timestamps are missing or newer than the activation.
  This checks event-time consistency, not physical simultaneity or causality.
- Use effective roles consistently for workspace counts and source diagrams;
  label derived defaults and preserve their derived status when an unrelated setting
  is saved. Only an explicit edit can persist such a group as manually confirmed.
- Display optional external comparison temperatures separately, with a difference
  only for valid, same-unit, independent measurements and a complete zone aggregate.
- Record the presence-first light/mood/media and bounded-adaptation architecture.
  It is a roadmap, not an implemented autonomous controller or new learner.

### Boundaries
- No new HA action, control activation, consent, collector, database or migration.
- Existing household entities and automations remain unchanged while the user
  organizes them. Existing evidence is not rewritten or retroactively certified.

## [0.1.0-alpha.37] - 2026-09-27

- Die bestehende Bestandsanalyse erkennt zwei strukturelle Präsenzfragen: Ein Türschluss kann einen bidirektional gesetzten Raumstatus ausschalten, und ein Nachlauftimer wird möglicherweise nur beim Bewegungsbeginn erneuert.
- Hinweise beruhen ausschließlich auf statischen Trigger-Zweigen, Geräteklassen und direkten Dienstaufrufen. Dynamische, deaktivierte, veraltete oder mehrdeutige Strukturen werden nicht als Befund ausgegeben.
- Ein eigener Filter und verständliche Fundstellen führen zur fachlichen Prüfung der vorhandenen HA-Automation. Keine Reparatur, Speicherung, Lernfreigabe oder Haussteuerung.
- Neun neue Python-Regressionsfälle plus ein vollständiges Browser-Szenario prüfen Datenschutz, Mehrdeutigkeit, doppelte IDs, veraltete Snapshots und ausbleibende Mutationen.

## [0.1.0-alpha.36] - 2026-09-26

- Bestandsprüfungen werten einen alten Snapshot nach einem Reconnect nicht mehr als frisch auf. Verbindungsverlust während eines Pakets entwertet sämtliche Referenzbefunde dieses Pakets, auch bei zwischenzeitlich nicht lesbaren Automationen.
- Änderungen an Verfügbarkeit, Deaktivierung, Bereich, Einheit oder Registerdaten liefern einen Konflikt statt veralteter Ersatzempfehlungen. Normale verfügbare Messwertwechsel bleiben zulässig.
- Reparaturentwürfe benötigen vor und nach dem Konfigurationsabruf einen frischen, unveränderten Bestand; bei Konflikten wird kein Entwurf gespeichert. Keine automatische Reparatur oder neue Ausführungsberechtigung.
- Sieben neue synthetische Regressionstests für Verbindungswechsel, gemischte Pakete, Metadatenänderungen, HTTP-Konflikte und ausbleibende Persistenz/HA-Schreibaufrufe.

## [0.1.0-alpha.35] - 2026-09-26

- Der globale Automationsscan führt die ausdrücklich angeforderten Achterpakete zu einer abgeleiteten Gesamtübersicht der aktuellen Prüfsitzung zusammen, statt ältere Ergebnisse zu ersetzen.
- Fortschritt und getrennte Filter zeigen Referenzhinweise, Auslöserhinweise, nicht lesbare Konfigurationen und alle gelesenen Ergebnisse in stabiler Reihenfolge.
- Ausgewählte Ersatzkandidaten bleiben bei weiteren Paketen und Filterwechseln erhalten; Zonenwechsel, Revision, Neuladen oder Invalidierung verwerfen den flüchtigen Lesestand konservativ.
- Keine neue Persistenz, automatische Vollabfrage, Reparaturausführung oder HA-Schreibberechtigung. Synthetische Browserregressionen prüfen zwei Pakete, eine Leselücke, Auswahlkontinuität und ausbleibende Mutationen.

## [0.1.0-alpha.34] - 2026-09-26

- Bestand und Routine-Detailprüfung gleichen statische Auslöserkennungen mit Bedingungszweigen ab. Fehlende, teilweise passende, deaktivierte und unklare Bezüge bleiben getrennt.
- Eine gemeinsame begrenzte Projektion liefert Fundstellen ohne private Triggernamen oder Rohkonfiguration; keine Ablauf- oder Sicherheitsgarantie.
- Gemeinsame Textausgabe mit Tastaturbedienung; explizite Analyse erhält ungespeicherte Eingaben und führt keine Reparatur aus.
- Synthetische Regressionen für implizite Indizes, gemeinsame IDs, deaktivierte Zweige, Templates, Warteauslöser, Datenpayloads und unveränderte Schreibgrenzen.

## [0.1.0-alpha.33] - 2026-09-26

### Recoverable inventory editing
- Bind name, repair, status and undo-preview responses to the requesting zone,
  revision and invalidation generation. Late plans cannot revive old confirmations.
- Keep manual assignments visible after failed post-save reloads or lost PATCH
  acknowledgements. Lock write replay and provide an explicit read-only recovery.
- Historical previews remain readable but cannot be applied at a newer revision.
- Add full-application browser regressions for invalidation, cross-zone responses,
  failed canonical reload and lost write acknowledgement. No new HA execution path.

## [0.1.0-alpha.32] - 2026-09-26

### Bestand & Ordnung
- Global manually confirmed function bindings for presence sources, existing room
  status, timer, duration parameter, manual override, automation blocker and existing
  automations. Use stable domain/platform/unique_id identity, not names as ownership.
- Explicit automation-first inspection without requiring a preconfigured owner/timer:
  nested direct references, timer event_data and literal template dependencies,
  inherited disabled/dynamic branches, for/timer mechanisms and bounded replacement
  suggestions with reasons. Unknown coverage stays explicit; no template execution.
- Existing ContextStore persists bindings under the shared zone revision, preserving
  learning roles, evidence, consent and unknown configuration keys. Savepoints include
  optional bindings with backward-compatible validation. No database schema migration.
- Foundation and helper inspection consume manually bound existing helpers, including
  area-less identities; existing for logic no longer forces a duplicate PilotSuite timer.
- PlanStore owns confirmed helper display-name cleanup and guarded undo, with durable
  before-images, independent native registry readback and no blind replay after restart
  or lost response. Shared-zone helpers and identity/name conflicts block unilateral edits.
- Configuration workspace includes search, manual selection, structural findings,
  candidate repair previews, standard naming proposals, plan status and explicit apply.

### Consistent maintenance and completed integration
- Bring the previously separate Alpha.32 package's maintenance presentation into this
  existing implementation: shared light/dark/system theme and density, responsive
  cards/navigation, explicit distinction between local savepoints and unverified native
  HA backups. No second inventory store or competing governance workspace.
- Global automation browsing is explicit and bounded to eight configurations per
  batch, with coverage and unread results; manual mappings remain authoritative.
- Preserve the successful binding-save acknowledgement after the canonical zone
  refresh. The existing browser regression still requires the confirmed saved state.

### Safety and boundaries
- Repair previews are stored but cannot write automation configuration. Technical
  Entity-ID migration is blocked until consumer coverage can be established. No labels,
  areas, values, generic HA service proxy, new helper or learning grant is introduced.
- Fail-close legacy helper provisioning as well as the older presence activation
  endpoint until transport, identity, recovery, timer event and authority
  takeover behavior is separately accepted. HA timer expiry is not a `finished` state.
- Name updates are not cross-system atomic or an HA compare-and-swap. Partial/unknown
  results remain visible; previous names can only be restored after a separate preview.

## [0.1.0-alpha.31] - 2026-09-26

### Workspace redesign
- Six explicit workspaces replace the default long page: Cockpit, zone modules,
  configuration, history, workbench and system. The full-page view remains available.
- Searchable zone cockpit with measured values, confirmed selection counts and
  disconnected/unknown states; no invented health score or decorative history.
- Presence, lighting, climate and media module cards plus source/reference/implementation
  diagrams. Configuration, current source usability and action authority stay separate.
- Existing canonical role editor gains module filters, source search, retained hidden
  selections and a before/after preview of roles, learning consent and detector settings.
- Local light/dark/system theme, compact/comfortable density and optional technical IDs.
  Desktop side navigation and mobile bottom navigation use the same workspaces.
- Explicit existing presence-automation structural review is reachable from the module
  view. It calls the existing read-only review API, never activates or takes over control.
- Guard dirty configuration, selection, routine and review-note drafts on navigation;
  preserve focus and invalidate stale diagrams after failed reads or a zone change.

### Boundaries
- Reuse the one original document, forms, handlers and canonical stores. No data migration,
  new execution capability, household configuration change or inferred learning consent.
- Dependency and state diagrams are labelled structural models, not proof of a running
  presence controller. Timer/provisioning correctness is not certified by this UX change.
- Existing recorder charts remain explicitly requested, not auto-fetched by navigation.

## [0.1.0-alpha.30] - 2026-09-26

### Added
- Controlled Presence Adoption review: derives the exact presence owner, raw sources
  and PilotSuite timer for a zone, asks Home Assistant for related automations, reads
  each related configuration and produces a fresh fingerprint-bound structural plan.
- Existing automations that directly write the logical owner or PilotSuite timer are
  classified as conflicts. Templates, indirect targets, blueprints and unsupported
  structures remain explicit blockers rather than guessed semantics.
- Adoption output is read-only and execution-closed. It never enables, disables,
  edits or deletes an automation and never treats configuration structure as runtime
  proof. A later takeover requires a separate backup-bound approval and fresh recheck.

### Boundaries
- Alpha.30 does not activate Presence Runtime automatically and does not remove the
  existing automation authority. No lighting/media/climate control is introduced.

## [0.1.0-alpha.29] - 2026-09-26

### Added
- Opt-in Presence Runtime Core per Habitus zone with exactly one explicitly selected
  logical input_boolean owner, confirmed raw presence sources and the PilotSuite timer.
- Deterministic occupied → grace → vacant / unknown reconciliation. Timer expiry only
  permits vacancy when every configured raw source is independently clear in the same
  evaluation; unknown/unavailable fails safe to unknown.
- Reconciliation on source/timer events and stream reconnect, plus a tiny allowlist
  limited to timer start/cancel and logical-owner on/off.
- Revision-bound explicit enable/disable API. Runtime remains disabled by default.

### Boundaries
- Existing household automations remain authoritative until separately inspected,
  backed up and explicitly adopted. Alpha.29 does not disable or rewrite them.
- Lighting, media and climate are not consumers yet. No learning consent is inferred.

## [0.1.0-alpha.28] - 2026-09-25

### Added
- One bounded helper executor in the existing PlanStore path: explicit revision-bound
  approval can create or exactly reuse only the planned PilotSuite presence-delay
  timer. Generic plans, automations, actuators and learning permissions remain closed.
- Before-image helper collection read, durable transaction journal, independent
  post-write read-back and no blind retry after a lost/timeout response.
- Action-specific recovery deletes only a timer whose creation response was positively
  confirmed in the same transaction and whose pre-image proved the identity absent.
  Pre-existing or foreign helpers are never deleted, renamed or adopted by name.
- Zonenbasis UI exposes the single timer action with a second explicit confirmation.

### Tested
- Explicit confirmation, stale revisions, concurrent edits, pre-existing conflicts,
  lost responses, verified rollback, journal recreation and allowlisted WS writes.

## [0.1.0-alpha.27] - 2026-09-25

### Added
- Integrated maintenance page and installed-version card: last three bundled
  release notes, cached identity-checked HA update status, and explicit native HA
  installation handoff. No silent self-update or new Supervisor privileges.
- Verified local zone-configuration savepoints through the existing PlanStore.
  Preview-bound, idempotent restore captures a before-point, preserves newer extra
  zones and leaves restored zones paused with learning disabled. No HA config or
  app binary is restored; evidence/review text are not part of a savepoint.
- Ingress-protected rescue page remains available on detected database startup
  failure; no automatic overwrite/restore. Full app recovery stays with native HA.
- Explicit existing-helper inspection: stable registry/storage ID matching handles
  renamed input helpers. Timer restore/default duration, number bounds and select
  options are shown without adoption or writes. Flow helpers remain visible as
  requiring separate configuration inspection.

### Clarified
- Historical golden_zone_area_ids means bootstrap areas only. Existing Habitus
  zones are managed in the app, not by changing this first-start option.
- Local configuration points are not full app backups, off-device backups,
  database repair, old-version installers or learning-history recovery.

## [0.1.0-alpha.26] - 2026-09-25

### Added
- German zone-foundation preparation view with explicit missing-source and
  helper-inspection states. Configuration readiness is not live control readiness.
- Explicit, transient API read of an existing automation with bounded source
  fingerprint, detached original configuration and static reference coverage.
- Preparatory import/mapping/diff/transform, helper and comfort-policy primitives.
  These are not a running presence timer, adaptive controller or migration executor.

### Fixed
- Reproduce and fix the literal-newline import-test failure and the metadata-vs-
  unknown-field diff error; compile test sources as well as application sources.
- Do not authorize helper reuse or creation from registry names/absence. Inspect
  the global registry, not just a zone's selected candidates, without HA I/O on GET.
- Exclude ignored, missing, unavailable and mistyped sources from preparation;
  prevent normalized/truncated zone keys from colliding in proposed helper IDs.
- Bound automation import size/depth, reject nonfinite JSON, isolate mutable views,
  share review concurrency, and recheck zone revision/inventory after the read.
- Do not silently discard unsupported transformation edits or verify identity from
  configuration equality alone. Preserve unknown original metadata.
- Remove stale setup displays during errors, zone changes and unsaved edits;
  translate internal status labels. Add actual-app foundation browser regression.
- Restore release-note history and the Alpha.25 published-source baseline.

### Boundaries
- All HA execution remains hard-read-only. No helper creation, automation takeover,
  persisted migration ledger, new learning consent or device control is introduced.
- Correlation rows are input plans, not new learned/validated correlations. Comfort
  policy functions are isolated examples, not connected media/heating controllers.
- Live Ingress acceptance, physical sensor quality and real comfort gain remain
  distinct from CI, source identity and native app-runtime checks.

## [0.1.0-alpha.25] - 2026-09-25

- Explicit opt-in logical presence helpers and multi-source role selection.
- Separate ambient-light binary indicators from controllable light state.
- Climate/media/atmosphere roles and initial read-only foundation projection.
- No PilotSuite helper provisioning or actuation. This entry restores the missing
  historical heading; the earlier Alpha.24 notes below are preserved verbatim.

## [0.1.0-alpha.24] - 2026-09-25

### Added
- Read-only Alltagsbrief in the existing zone context and UI: one retained review
  candidate, bounded inventory summary, evidence limits and explicit withholding.
- Same-zone/revision/source validation; rejected or deferred patterns stay excluded.
  Coverage and chronological evidence are checked before candidate selection.
- Real-store API regression tests and a full-application browser CI flow for
  navigation, reload races, errors, zone isolation and unsaved draft preservation.

### Fixed
- Clear stale daily candidates on same-zone reload, zone change and failed reads;
  recheck navigation basis at activation without saving or discarding user edits.
- Preserve keyboard focus and open explanations when equal projections refresh;
  validate bounded Unicode text consistently across Python and JavaScript.
- Daily-brief tests now run under the repository's unittest discovery; correct a
  missing zone_id in a synthetic inventory without weakening production checks.
- CI compares against the last published source, not an older installation receipt,
  and rejects a changed application tree that reuses a published version.

### Boundaries
- No new store, learner, collection, HA configuration scan, consent or execution.
- Retained evidence is not today's forecast, causal proof or verified comfort gain.
- Local component tests, full CI, scoped backup, installation and authenticated
  household acceptance remain distinct gates. Apply remains denied.

## [0.1.0-alpha.23] - 2026-09-24

### Added
- Derived review compass in the existing routine workbench: five independent
  source/evidence/intent/automation/note sections, provenance and one next step.
- Zone-scoped transient filters and sorting, accessible explanation panels and
  current-basis navigation without another store, learner or execution permission.
- Same-basis, age-bounded presentation of explicit automation inspection and note
  results; source and evidence sections always use the latest canonical projection.
- Synthetic Python, JavaScript and full-application browser regression contracts;
  source-only CI evidence for reproducible tests.

### Fixed
- HEAD requests for routine drafts follow the read-only GET path instead of being
  parsed as mutation requests.
- Review-note deletion refreshes the derived workbench basis without losing user
  text; keyboard focus survives background projection updates.

### Boundaries
- No autosave, background automation scan, inferred learning consent or HA writes.
- Assessment, freshness, evidence, risk and execution permission remain separate.
- Apply remains denied. CI does not certify authenticated household UI acceptance.

## [0.1.0-alpha.22] - 2026-09-24

- Dauerhafte Prüfnotizen zu ausgewählten Automationen im bestehenden PlanStore: Offen, Änderungsbedarf oder Manuell geprüft – keine Freigabe.
- Bewertungen an Entwurfs-/Zonenrevision, Quellen-/Zielbezug und Konfigurationsfingerabdruck binden; veraltete und nicht erneut geprüfte Stände getrennt anzeigen.
- Vor dem Speichern erneut lesend prüfen; konkurrierende Änderungen und abgelaufene Prüfstände ohne Überschreiben zurückweisen.
- Editor erhält Texte bei Fehlern und beim Neuladen der Prüfgrundlage; expliziter Export und revisionsgeschütztes Löschen.
- Additive SQLite-Migration 8 mit vorgelagerter Datenbanksicherung. Vor dem App-Update weiterhin PilotSuite samt Daten sichern.
- Keine neue Lernfreigabe, Rohkonfigurationsspeicherung, HA-Automationsänderung oder Ausführung.

## [0.1.0-alpha.21] - 2026-09-23

- Eine ausdrücklich gewählte passende HA-Automation rein lesend in Auslöser, Bedingungen und Aktionen aufschlüsseln.
- Verschachtelte Abläufe und Quellen-/Zielbezüge sichtbar machen; Templates, indirekte Aufrufe und unbekanntes Verhalten offen kennzeichnen.
- Offenen Prüfplan für Komfortziel, Zeitverhalten, manuellen Vorrang, Aktivierungsstatus und Risiko ableiten.
- Bei erneuter Prüfung Konfigurationsänderungen erkennen; Entwurf, Strukturprüfung und Prüfplan gemeinsam exportieren.
- Keine Rohkonfiguration speichern/exportieren, keine neue Datensammlung, Ausführung oder Automationsänderung.

## [0.1.0-alpha.20] - 2026-09-23

- Gespeicherte Routine-Entwürfe auf Klick mit Entitätsbezügen bestehender HA-Automationen vergleichen.
- Quellen- und Zielbezüge getrennt anzeigen; Grenzen bei Templates, indirekten Aufrufen und Geräte-/Bereichszielen ausdrücklich sichtbar.
- Kein Treffer bedeutet keine Entwarnung: Duplikate, Aktivierungsstatus, Verhalten und Risiko bleiben fachlich ungeprüft.
- Begrenzte rein lesende Abfrage, Revisionsprüfung vor/nach dem Abruf und kontrollierte Fehler; keine neue Sammlung, Persistenz oder Ausführung.
- Zeitgestempeltes Prüfergebnis optional im vorhandenen JSON-Export.

## [0.1.0-alpha.19] - 2026-09-23

- Routine-Entwürfe aus Mustern anlegen, dauerhaft bearbeiten, exportieren und gezielt löschen.
- Komfortziel, bestätigte Zielgeräte, Auslöser, Bedingungen, Ausnahmen und manuellen Vorrang festhalten.
- Revisionen schützen Änderungen; geänderte Zonen, fehlende Belege und nicht mehr verfügbare Ziele bleiben sichtbar.
- SQLite-Migration 7 mit Sicherung; keine kopierten Lernbelege, neue Sammlung oder Ausführung. Automationsvergleich und Risiko bleiben ungeprüft.

## [0.1.0-alpha.18] - 2026-09-23

- Musterfeedback prüft Gültigkeit und speichert die Rückmeldung in einer gemeinsamen SQLite-Transaktion.
- Gleichzeitiger Lern-Reset, Quellenwechsel, neue Erkennungsschwellen oder abgelaufene Belege können keine veraltete Rückmeldung mehr einschleusen.
- Vorhandene gültige Muster bleiben bei ausgeschaltetem Lernen bewertbar; Beobachtungen, Regelstärke und Konfidenz bleiben unverändert.

## [0.1.0-alpha.17] - 2026-09-23

- Zeitlich getrennte Musterprüfung direkt in Werkbank und JSON-Prüfbericht.
- Frühere Musterbildung und spätere Wiederbeobachtung verwenden getrennte Belege im gleichen lokalen Zeitfenster und in derselben Tagesgruppe.
- Unzureichende frühere oder fehlende spätere Belege bleiben ausdrücklich sichtbar; keine Genauigkeitsquote oder Ausführungserlaubnis.
- Gemeinsame Rückblicklogik für Historie und vorhandenen Lernspeicher; keine neue Datensammlung oder Migration.

## [0.1.0-alpha.16] - 2026-09-23

- Zonen-Assistent mit konkretem nächsten Schritt und aufklappbarer Einrichtungsprüfung.
- Unterscheidet fehlende Quellen, pausierte Auswertung, Verbindung und freiwillige Lernfreigabe.
- Zeigt fehlende Belege je Zeitfenster ohne Zeitfenster zu vermischen oder Fertigdatum vorherzusagen.
- Direkte Navigation zu bestehenden Einstellungen; keine automatische Aktivierung oder neue Datensammlung.

## [0.1.0-alpha.15] - 2026-09-23

- Direkte Bereichsnavigation, konsistente deutsche Begriffe und mobile Formulare.
- Bearbeitungs- und Feedbackbestätigungen, Importgründe und klare Datumsvalidierung.
- Keine fremden Lernangaben nach Zonenwechsel; Tastaturfokus besser erhalten.
- Erweiterte Browserregression für Navigation und drei Bildschirmbreiten.
- Verspätete Kontextantworten überschreiben keine neueren Anzeigen oder Feedbacks.
- Konsistente Versionsmarker; verbindlicher Release-Ablauf und lesende Quellprüfung.

All notable changes follow [Semantic Versioning](https://semver.org/).

## [0.1.0-alpha.14] - 2026-09-23

- Pattern workbench: preference filters, evidence chains, matching light context and JSON review briefs.
- Review exports remain non-executable; feedback grants no action permission.
- Controlled Recorder metadata and history timeout failures.

## [0.1.0-alpha.13] - 2026-09-23

- Convert Home Assistant connection failures during scoped history and statistics
  requests into the existing bounded history error instead of a generic HTTP 500.
- Treat malformed Home Assistant WebSocket text frames as typed protocol errors.
- Preserve successful history responses, SQLite schema 6, consent, roles and the
  hard read-only boundary.

## [0.1.0-alpha.12] - 2026-09-23

- Add consent-gated, memory-only correlation between Home Assistant service and
  state contexts; persist only coarse origin categories without identifiers.
- Add scoped zone-history graphs for recorded states and hourly long-term statistics.
- Show virtual zone references, source ranges, presence/light timelines, weekly
  activity rasters and chronological re-observation checks with explicit gaps.
- Add one-time, interval-scoped retrospective activity consent. Import only
  confirmed presence activations into the existing activity-v1 store; never infer
  historical light context or actuation intent.
- Migrate to SQLite schema 6 with a pre-migration backup, import receipts and
  provenance; deduplicate imported evidence against live and previous evidence.
- Keep learning, historical import and every Home Assistant action disabled unless
  separately authorized. This release remains hard read-only.

## [0.1.0-alpha.11] - 2026-09-23

- Add per-zone activity thresholds, local IANA timezones and weekday/weekend grouping.
- Show source details, learning progress and bounded observation checkpoints.
- Add separately consented light/lux context at activity events, with explicit unknowns.
- Preserve evidence on parameter edits; bind preference to the detector configuration.
- Migrate to SQLite schema 5 with a pre-migration database backup; preserve roles and choices.
- Extend export, reset and retention to the new evidence. Context learning defaults off.
- No HA actuation. Downgrading requires restoring the matching App-and-data backup.

## [0.1.0-alpha.10] - 2026-09-23

- Separate activity observation statistics, deterministic rule-threshold ratios,
  nullable statistical confidence, read-only risk and durable user preference.
- Keep preference feedback independent from evidence counts and rule strength.
- Show every assessment dimension explicitly in the Ingress candidate card.
- Retain earlier flat activity fields as deprecated alpha API compatibility aliases.
- Add synthetic regression coverage; no production learning consent or HA action.

## [0.1.0-alpha.9] - 2026-09-22

- Derive virtual zone references from main sensor groups, including illuminance.
- Use the same explicit presence group for summary and consented learning.
- Preserve empty groups; display effective defaults before editing.
- Validate lux units and values; distinguish external comparison temperatures.
- Add API persistence, role-group and mobile browser regressions.

## [0.1.0-alpha.8] - 2026-09-22

- Fix direct module startup: define all role/learning API handlers before calling main.
- Add a real subprocess entrypoint regression: starts python -m pilotsuite.app and
  checks loopback HTTP health, using isolated data and no Home Assistant credentials.
- alpha.7 failed at route registration on the real App before startup/migration;
  alpha.8 supersedes it. Role groups and opt-in learning otherwise unchanged.

## [0.1.0-alpha.7] - 2026-09-22

- Evaluate confirmed relevant entities only; reject the legacy automatic bypass.
- Show compact per-zone capability cards and separate candidate/decision/evaluation counts.
- Add role groups (up to 20 sources): climate median with min/max, visible missing data,
  separate reference temperatures and presence-any logic without false absence.
- Add opt-in recurring-activity candidates from live off-to-on events, with 5-minute
  zone deduplication, 14-day retention and a global 5,000-evidence limit.
- Persist independent pattern feedback; expose consent, revoke, reset and export.
- SQLite schema 4 backs up older schemas; never infer roles, decisions or learning consent.
- No actor control, person identification, occupancy probability or causal claims.

## [0.1.0-alpha.6] - 2026-09-22

- Add visible tabs per Habitus zone with scoped evaluation, suggestions and observations.
- Add direct start/pause and name/source editing; fetch shared revision before activation.
- Replace HA-area multi-select with checkboxes for composing zones such as Bad + Toilette.
- Separate zone activation from the advanced entity-selection mode; explain unsaved edits.
- Preserve zone definitions, decisions, neutral profiles and the HA read-only boundary.
- Extend browser regression for multi-area creation, activation, rename, pause, conflicts,
  reload and tab isolation. Real HA interactive acceptance remains separate.

## [0.1.0-alpha.5] - 2026-09-22

- Add logical Habitus zones with stable IDs, multiple area sources and extra entities.
- Add zone editor and persistent relevant/ignored/unreviewed entity selection.
- Keep per-zone inference isolated and deduplicate global entity counts.
- Add SQLite schema 3, pre-migration backups, shared revision conflict protection,
  JSON export and a journal bounded to 5,000 transactions.
- New UI-created zones start paused with a neutral profile and curated selection.
- Preserve existing zone behavior on first migration; HA actuation stays disabled.
- Verify with 46 backend tests, four JavaScript tests, browser tests and amd64 CI build.
- Learning, contextual role priorities, import and permanent deletion remain deferred.

## [0.1.0-alpha.4] - 2026-09-22

- Separate transport readiness from zone and capability availability.
- Report missing climate evidence as null / not assessable, not zero.
- Exclude buttons and unrelated diagnostics from climate uncertainty.
- Display capability-specific availability and log safe readiness summaries.
- Add four regression tests (28 total); no HA actuation enabled.

## [0.1.0-alpha.3] - 2026-09-22

### Fixed
- Route repeated Ingress slashes internally without losing the external prefix.
  Omitting the default ingress_entry alone was not a proven fix.
- Normalize climate units and reject invalid readings; missing climate data is not stable.
- Separate severity from unknown confidence; keep proposal identity stable.
- Track event stream health, resynchronize after reconnect and back off on clean close.
- Reject older state updates and exclude disabled entities from the projection.

### Security
- Restrict UI/API to the Ingress TCP peer; allow loopback liveness probes only.
- Home Assistant mutations remain hard-disabled.

### Added
- Reviewed full vision, capability/acceptance ledger and revised learning-first roadmap.
- Regression tests and periodic dashboard refresh.
- Real Supervisor/browser acceptance is still pending.

## [0.1.0-alpha.2] - 2026-09-22

### Fixed

- Raised the bounded Home Assistant WebSocket receive limit to 32 MiB so larger
  state and registry snapshots do not close the connection at `aiohttp`'s
  4 MiB default.
- Report the actual WebSocket message type and transport error when a snapshot
  connection fails.

## [0.1.0-alpha.1] - 2026-09-22

### Added

- Canonical PilotSuite v21 repository and project memory
- Installable Home Assistant Supervisor App skeleton
- REST/WebSocket Home Assistant connector
- Registry-backed world model and area resolver
- Erdkeller Golden Zone configuration
- Deterministic neurons, moods, synapses, and suggestions
- Read-only policy gate and dry-run plans
- Ingress dashboard, API, audit trail, tests, and CI

### Security

- Hard-disabled Home Assistant mutations for the complete alpha release
- No Home Assistant config mounts, host networking, privileged capabilities, or secret persistence
