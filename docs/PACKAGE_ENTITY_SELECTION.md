# Paket: Habitus-Zonen und bewusste Entitätenauswahl

Status: `0.1.0-alpha.5` veröffentlicht und installiert; PR #1 zusammengeführt.
Ausgangsinstallation: 0.1.0-alpha.4; Live-Stand siehe CURRENT_STATE.md.

## Verbindliches Konzept

[HABITUS_ZONES.md](HABITUS_ZONES.md) und ADR-015 beschreiben das implementierte
Zonenmodell, seine Grenzen und die Migration. Die frühere Beschränkung auf
einzelne HA-Bereiche ist aufgehoben.

## Implementiert

- Logische Zonen mit stabiler ID, Name, mehreren Bereichsquellen und zusätzlichen
  Entitäten; Anlegen, Bearbeiten und reversibles Deaktivieren im Ingress-Editor.
- Dauerhafte Auswahl relevant/ignoriert/ungeprüft, Suche, Empfehlungen ohne
  automatische Zustimmung und Konfliktschutz für Definition und Auswahl.
- Neutrales Beobachtungsprofil für neue Zonen; Erdkellerregeln ausdrücklich
  auswählbar. Neue Zonen starten im UI deaktiviert mit bestätigter Auswahl.
- Getrennte Moods/Vorschläge je aktiver Zone; globale Entitätszahlen dedupliziert.
- SQLite-Schema 3, Sicherung vor Migration, einmalige Übernahme bestehender
  Zonen und Entscheidungen. Keine Änderung der HA-Zuordnungen.
- JSON-Export und auf 5.000 Transaktionen begrenztes Änderungsjournal.

## Verifikation und Release

46 Python-Tests, vier JavaScript-Modelltests, Syntaxprüfung und
Repository-Vertragsprüfung lokal erfolgreich. GitHub CI prüft zusätzlich die
mobile Oberfläche einschließlich Zonenerstellung sowie den amd64-Container.
CI-Nachweise werden im PR und CURRENT_STATE.md festgehalten.

Release-CI 35787425872 erfolgreich. App-Backup ec38dcca bestätigt; alpha.5
installiert, Start und Betriebsbereitschaft durch Laufzeitprotokoll geprüft.
Interaktive Prüfung des neuen Editors in der tatsächlichen HA-Sitzung bleibt offen.
Nachweise und nächste Schritte: CURRENT_STATE.md.

Noch nicht enthalten: bestätigte kontextuelle Rollenprioritäten, Import,
endgültiges Löschen, Gewohnheitslernen oder Aktorfreigaben.
