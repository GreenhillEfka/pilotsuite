# Ereignisherkunft: begrenzte Kontextkorrelation

## Zweck und Grenze

PilotSuite soll eigene Aktionen später nicht als Nutzergewohnheit zurücklernen und
vorhandene Automationen bei Vorschlägen berücksichtigen. Home Assistant übermittelt
bei Ereignissen `id`, `parent_id` und `user_id`. Diese Felder verbinden Vorgänge,
benennen aber nicht zuverlässig eine konkrete Person, Automation oder ein Skript.
PilotSuite behandelt sie daher als Herkunftshinweis, nie als Kausalitätsbeweis.

## Datenfluss

Der HA-WebSocket abonniert `state_changed` und `call_service` getrennt. Nur wenn
mindestens eine aktive Zone eine ausdrückliche Lernfreigabe und eine auswertbare
Präsenzquelle besitzt, werden Service-Kontexte kurzzeitig korreliert:

- ausschließlich im Arbeitsspeicher;
- höchstens 120 Sekunden und 2.048 Einträge;
- ohne Speicherung von Service-Domain, Service-Daten, Benutzer- oder Context-ID;
- vollständig geleert bei Verbindungsabbruch, App-Neustart oder wenn keine
  freigegebene auswertbare Lernquelle mehr besteht.

Die normale Lernaufbewahrung, Deduplizierung und Quellenprüfung bleibt unverändert.
Es gibt keine neue Zustimmung, keinen historischen Import und keine Aktorfreigabe.

## Gespeicherte Kategorien

| Kategorie | Belegt | Belegt ausdrücklich nicht |
|---|---|---|
| `user_context` | HA meldete einen Nutzerkontext | physische/manuelle Bedienung oder konkrete Person |
| `parented_service_context` | passender, verketteter Serviceaufruf wurde kurz zuvor beobachtet | bestimmte Automation, Skript oder Ursache |
| `service_context` | passender Serviceaufruf ohne belegten Elternkontext | Initiator oder gewünschter Effekt |
| `derived_context` | Elternkontext vorhanden, aber kein passender beobachteter Service | Art der Ableitung |
| `unknown` | keine belastbare Zuordnung | Abwesenheit eines Auslösers |

PilotSuite ist weiterhin hart read-only. Deshalb existiert aktuell keine Kategorie
für eigene ausgeführte Aktionen. Ein späterer Transaktionspfad muss eigene Kontexte
explizit markieren und aus Lernbelegen ausschließen; heuristisches Erraten ist
unzulässig.

## Darstellung und Export

Musterstatistiken zählen Kategorien getrennt von Regelschwelle, Konfidenz, Risiko
und Nutzerpräferenz. Die UI erläutert parented service context nur als mögliche
Automation/Skript-Kette. Exporte enthalten dieselben Kategorien, keine Roh-IDs.
Feedback verändert weiterhin weder Herkunft noch Beobachtungszähler.

## Abnahme

Synthetische Tests prüfen beide Abonnements, Weitergabe des vollständigen
Servicekontexts, Korrelation über `id`/`parent_id`, Ablauf, Größenlimit, Leeren bei
Disconnect, Zustimmungsschranke, Persistenz erlaubter Kategorien und das Fehlen
privater IDs in Exporten. Reale HA-Abnahme darf nur mit bereits ausdrücklich
freigegebenem Lernen erfolgen; Lernfreigabe wird nicht zu Testzwecken aktiviert.
