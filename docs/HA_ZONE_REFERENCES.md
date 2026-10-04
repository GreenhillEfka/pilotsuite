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

PilotSuite zeigte beim angemeldeten Lesen vier gespeicherte Zonen; Gangbereich
und Eingangsbereich fehlten. Vor Vollübernahme müssen bestehende Mitgliedschaften,
physische Bereiche und Rollen gegen HA geprüft werden. Der Gangbereich-Labelimport
schlug 294 Mitglieder einschließlich Konfigurationsentitäten und Automationen
vor; das ist ein Prüfbestand, keine pauschale Freigabe. Zusätzliche Zonen sind
offen vorgesehen und werden künftig aus HA und PilotSuite dynamisch ermittelt.
