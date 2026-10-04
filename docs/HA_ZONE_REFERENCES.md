# Bestehende HA-Zonen als PilotSuite-Referenz — 04.10.2026

Dies ist ein datierter Abgleich des laufenden HA-Registers und der Sound-Cloud-
Konfiguration, kein festes Zonenschema. Vor einer tatsächlichen Übernahme alle
IDs und Mitglieder erneut lesen. PilotSuite speichert diese Beziehungen als
stabile, lesende Strukturverknüpfungen; HA bleibt für jede Schaltung zuständig.
Das Label `habitus_zone` kennzeichnet je Zone genau einen öffentlichen
Anwesenheitsanker und gehört nicht an Geräte oder Lichtgruppen.

| Zone | Lichtgruppe | Lichtautomatik | Shutdown |
| --- | --- | --- | --- |
| Erdkellerbereich | `light.beleuchtung_erdkeller` | `input_boolean.erdkellerbereich_lichtautomatik` | `script.habitus_shutdown_erdkellerbereich` |
| Badbereich | `light.bad_beleuchtung_badbereich` | `input_boolean.badbereich_lichtautomatik` | `script.habitus_shutdown_badbereich` |
| Gangbereich | `light.beleuchtung_gangbereich` | `input_boolean.gangbereich_lichtautomatik` | `script.habitus_shutdown_gangbereich` |
| Kochbereich | `light.kuche_beleuchtung_kuche` | `input_boolean.kochbereich_lichtautomatik` | `script.habitus_shutdown_kochbereich` |
| Wohnbereich | `light.wohnzimmer_beleuchtung_wohnzimmer` | `input_boolean.wohnbereich_lichtautomatik` | `script.habitus_shutdown_wohnbereich` |
| Eingangsbereich | `light.beleuchtung_eingangsbereich` | Teilraum-Freigaben für Vorder- und Hintereingang; keine bestätigte globale Freigabe | `script.habitus_shutdown_eingangsbereich` |

| Zone | Nativer Sonos-Player | Präsenzfreigabe | Bedienbarer Sound-Cloud-Schalter | Favorit | Tageszeit-Lautstärke |
| --- | --- | --- | --- | --- | --- |
| Badbereich | `media_player.toilette_badbereich` | `input_boolean.badbereich_sound_cloud_bei_prasenz` | `switch.sound_cloud_badbereich_2` | `input_select.sound_cloud_badbereich_favorit` | `input_boolean.sound_cloud_badbereich_sonos_daytime_volumen_automatisierung` |
| Gangbereich | `media_player.gang_gangbereich` | `input_boolean.gangbereich_sound_cloud_bei_prasenz` | `switch.sound_cloud_gangbereich_2` | `input_select.sound_cloud_gangbereich_favorit` | `input_boolean.sound_cloud_gangbereich_sonos_daytime_volumen_automatisierung` |
| Kochbereich | `media_player.kuche_kochbereich` | `input_boolean.kochbereich_sound_cloud_bei_prasenz` | `switch.sound_cloud_kochbereich_2` | `input_select.sound_cloud_kochbereich_favorit` | `input_boolean.sound_cloud_kochbereich_sonos_daytime_volumen_automatisierung` |
| Wohnbereich | `media_player.wohnzimmer_wohnbereich` | `input_boolean.wohnbereich_sound_cloud_bei_prasenz` | `switch.sound_cloud_wohnbereich_2` | `input_select.sound_cloud_wohnbereich_favorit` | `input_boolean.sound_cloud_wohnbereich_sonos_daytime_volumen_automatisierung` |

Erdkeller- und Eingangsbereich haben keinen bestätigten zugehörigen Sonos-Player;
deren Sound-Cloud-Verknüpfung bleibt leer. Ähnlich benannte Music-Assistant-
Entitäten sind kein Ersatz für den nativen Sonos-Gruppenplayer. Die `_2`-IDs der
vier Schalter wurden im Registry-Readback bestätigt; das `default_entity_id` in
YAML ist nach einer früheren Umbenennung nicht die aktuelle Entity-ID. Das
interne `input_boolean.sound_cloud_*_aktiv` ist ein Besitzmarker, kein
Bedienungsschalter.

Licht: vorhandene Gruppen, optionale positive Freigabe, Präsenz und Szenen
bleiben HA-Verantwortung; manuelle Bedienung hat Vorrang. PilotSuite bildet den
Bezug ab, ohne eine zweite Lichtentscheidung zu starten. Sound: der bestehende
Controller gruppiert native Sonos-Player, beachtet opt-in und Besitzmarker,
verwendet zonale Favoriten und behält bei ausgeschalteter Tageszeit-Automatik
die letzte manuelle Lautstärke. Eine Zuordnung hier aktiviert nichts.

Der angemeldete PilotSuite-Abgleich vom 04.10.2026 hat Gangbereich und
Eingangsbereich ergänzt. Für alle sechs Zonen sind die geprüften, lesenden
Referenzen gespeichert und frisch aus der Anwendung gelesen. Nur Eingangsbereich
meldet eine vollständig passende HA-Struktur. Bei Erdkellerbereich,
Gangbereich und Wohnbereich bleiben zusätzliche,
vorwiegend deaktivierte HA-Labelmitglieder als Abweichung sichtbar. Die 234
ausgewählten Gangbereich-Mitglieder wurden aus 294 Vorschlägen kuratiert; die
übrigen 60 wurden nicht still für Analyse oder Steuerung freigegeben.

Alpha.77 wurde nach PR #161 und exakter CI installiert. Der authentifizierte
Ingress zeigte die acht geprüften Verknüpfungen je Bad, Gang, Küche und Wohnen
sowie drei Licht-/Shutdown-Verknüpfungen für Erdkeller und zwei für Eingang.
Kochbereich behält 419 alte Mitglieder, darunter mindestens eine nach der
Massenumbenennung ersetzte Identität. Ein normaler Struktur-Save wurde zu Recht
abgelehnt. Der revisionsgebundene **Link-only-Save** speicherte dort nur die acht
validierten HA-Referenzen; Mitglieder, Rollen und Auswertungsentscheidungen
blieben unverändert. Die alten Identitäten benötigen eine gesonderte, belegte
Migration.

Badbereichs Label lieferte 858 Kandidaten im HA-Bestand und überschritt die
500er Vollimportgrenze. Der bereichsgebundene Import aus Bad und Toilette zeigte
281 Kandidaten; 145 aktiv wählbare Mitglieder wurden mit ihren vorhandenen
HA-Darstellungsrollen gespeichert. Die acht realen Licht-/Sonos-Verknüpfungen
sind ebenfalls gespeichert und frisch lesbar. Der HA-Abgleich meldet weiterhin
zusätzliche Labelmitglieder außerhalb dieses bewusst engeren Bereichs. Weder
das breite Label noch die Küchen-Renames dürfen als vollständige strukturelle
Synchronisierung oder als übernommene Geräteautomatik dargestellt werden.

Diese sechs Zonen sind eine **Momentaufnahme und Referenz**, keine feste
Anzahlgrenze. Neue Zonen aus aktuellem HA- und PilotSuite-Bestand entdecken,
stabile Identitäten und Rollen einzeln prüfen und nur bestätigte Licht-/Sonos-
Beziehungen dokumentieren. Eine Strukturzuordnung beweist weder Anwesenheit
noch physische Licht- oder Musikwirkung und aktiviert keine PilotSuite-Steuerung.
