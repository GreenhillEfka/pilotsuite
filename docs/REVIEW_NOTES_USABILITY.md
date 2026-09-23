# Prüfnotizen: Übersicht und erneute Bewertung

Stand: 2026-09-24. Ergänzung zum unveröffentlichten Alpha.22-Kandidaten in PR #50.
Dies setzt ADR-030 um, ohne neuen Store, Backend-Endpunkt oder Freigabemechanismus.
Der Vertrag in REVIEW_NOTES.md bleibt bestehen; diese Seite präzisiert die Bedienung.

## Konkrete Verbesserung

Die Prüfzentrale zählt zwei voneinander unabhängige Angaben: eigene Bewertungen
(offen, Änderungsbedarf, manuell geprüft) und Aktualität ihrer Grundlage
(veraltet/geändert, nicht erneut gelesen, passend zum letzten Lesen). Eine manuell
geprüfte Bewertung kann gleichzeitig veraltet sein. Es gibt weder einen
Gesamtstatus „freigegeben“ noch eine erfundene Sicherheitsquote. Leere Listen
sagen nichts über Konfliktfreiheit oder vorhandene Hausautomationen aus.
Die Zähler werden nur aus der aktuellen Ansicht abgeleitet, nicht gespeichert.

Jede vorhandene Bewertung hat jetzt **Erneut prüfen**. Der Knopf ruft den bestehenden
`compareRoutine(draft, automation_id)`-Pfad auf. Dieser validiert serverseitig erneut
aktuelle direkte Bezüge und liest nur die ausdrücklich ausgewählte Konfiguration.
Kein Stapelscan, kein automatisches Speichern. Bei fehlendem Musterbezug oder nicht
bestätigten Zielgeräten ist diese Nachprüfung gesperrt; die gespeicherte Notiz bleibt.
Die Hinweise nennen dann die Entwurfsgrundlage statt einer nicht ausführbaren Prüfung.

## Behobene unklare Vorbelegung

Vor dieser Korrektur übernahm der Editor die alte Bewertung auch nach einem Wechsel
der Prüfgrundlage unverändert. „Manuell geprüft“ konnte daher beim erneuten Speichern
unauffällig auf einen geänderten Stand übertragen werden, obwohl die API korrekte
Revisions- und Fingerabdruckprüfungen ausführte.

Nun gilt beim Öffnen: Nur eine zum gerade geprüften Stand passende Bewertung wird
vorbelegt. Andernfalls steht die Auswahl auf **Offen**; der alte Text bleibt als
Ausgangspunkt erhalten. Die bisher gespeicherte Bewertung wird nicht umgeschrieben.
Beim Nachladen im Editor setzen geänderte Entwurfs-/Zonen-/Quellen-/Ziel-/Automations-
grundlagen oder eine geänderte Review-Revision die Auswahl ebenfalls auf **Offen**.
Unverändertes Nachladen behält eine bewusst gewählte Bewertung bei. Reine Änderungen
an Beobachtungszählern oder Präferenzen sind keine neue Prüfgrundlage.

Der Editor zeigt die zuletzt gelesene gespeicherte Bewertung zum Vergleich. Bei
konkurrierenden Änderungen klappt dieser Vergleich automatisch auf. Eigener Text
bleibt erhalten; es findet weder automatisches Zusammenführen noch Überschreiben
statt. Erst ein ausdrücklicher Speichervorgang schreibt über den bestehenden
revisionsgeschützten API-Pfad. Ein weiterer Konflikt bleibt ein Konflikt.

Programmatisch zurückgesetzte Auswahl wird als ungespeicherte Änderung behandelt;
der vorhandene Abbruch-/Seitenverlassen-Schutz bleibt wirksam. Er ist keine
plattformübergreifende Wiederherstellung geschlossener Browser-Tabs. Texte werden
weiterhin mit `textContent` ausgegeben; auch die Vergleichsansicht interpretiert
weder HTML noch Vorlagen. Statushinweise bleiben im vorhandenen `role=status`-Bereich.
Die neue Übersicht löst selbst keine Anfragen und keine Live-Region-Meldungsflut aus.

## Prüfung und Liefergrenze

Zwölf zusätzliche JavaScript-Tests prüfen getrennte Zähler, konservative Defaults,
Unveränderlichkeit der Quelldaten und die Bindung der Vorbelegung. Der vorhandene
synthetische Browser-Editor-Test prüft jetzt außerdem die direkte Nachprüfung,
beide Rücksetzungen, konkurrierende Bewertungstexte, ausdrücklich ausbleibende
Autosaves, blockierte Nachprüfung bei fehlender Grundlage und sichere Textdarstellung.
Der vollständige App-Shell-Browserlauf bleibt unverändert Teil der CI. Der isolierte
Editor-Harness verwendet einen minimalen Adapterstub und ist keine Live-HA-Abnahme.
Exaktes Endergebnis der vollständigen Kandidaten-CI steht in PR #50.

Diese Runde ändert nur Oberfläche, Tests und Dokumentation. Keine neue Migration,
Backend-Berechtigung, Lernfreigabe, Policy-Änderung oder HA-Ausführung. Alpha.22 war
vor der Änderung nicht veröffentlicht; die Versionsnummer bleibt deshalb gleich.
Vor einer Veröffentlichung bleiben aktuelle Versions-/Sicherungsbelege und die
Release-Gates aus RELEASE_RUNBOOK.md erforderlich. Der fehlende HA-MCP-Aufruf wird
nicht durch eine Veröffentlichung auf main umgangen.

Technische Referenzen für die bestehende Formular-/Statussemantik:
- https://html.spec.whatwg.org/multipage/form-elements.html#dom-select-value
- https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html
