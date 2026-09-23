# Lernen, Module und Umsetzung

## Was bereits vorhanden ist

PilotSuite alpha.9 beobachtet bestätigte Entitäten und berechnet typisierte
Zonenreferenzen. Das Lernmodul `activity-v1` erkennt wiederkehrende Aktivierungen
freigegebener Präsenz-/Bewegungsquellen. Es ist eine deterministische
Häufigkeitsanalyse, kein neuronales Netz und kein Nachweis einer menschlichen Routine.
Klima-Vorschläge sind getrennte feste Regeln. Ein LLM ist nicht erforderlich.

PR #9 ergänzt Fortschrittsanzeige, Quellenprüfung, Modulübersicht und dauerhaft
konfigurierbare Mindestbelege. Dies ist Entwicklungsstand, noch kein HA-Release.

## Konfiguration je Habitus-Zone

1. Quellenbereiche und relevante Entitäten auswählen.
2. Hauptsensorgruppen für Temperatur, Feuchte, Helligkeit, Präsenz und Licht setzen.
3. Zone zur Auswertung aktivieren.
4. Unter „Rollen / Lernfreigabe bearbeiten“ optional „Lernalgorithmus einstellen“ öffnen.
5. Mindestaktivierungen (5–100, Standard 5) und verschiedene Beobachtungstage
   (3–14, Standard 3) festlegen. Beides muss im selben Zeitfenster erfüllt sein.
6. Lernen separat freigeben. Speichern ist mit der Zonenrevision gegen paralleles
   Überschreiben geschützt. Die Lernfreigabe ist niemals eine Schaltfreigabe.

In PR #9 sind Zeitzone und Trennung Mo–Fr/Sa–So zusätzlich konfigurierbar;
UTC bleibt der unveränderte Standard. Fest: zwei Stunden pro Fenster, fünf Minuten
Abstand zwischen Aktivierungen, 14 Tage Aufbewahrung und maximal 5.000 Belege.
Hohe Mindestwerte können dazu führen, dass kein Kandidat entsteht; sie sind keine
statistischen Vertrauenswerte. Die zusätzliche Kontextfreigabe speichert Licht
und Helligkeit bei Aktivierungen. Einzelheiten: [RHYTHMS_AND_CONTEXT.md](RHYTHMS_AND_CONTEXT.md).

Parameteränderungen erhalten die Belege und die Lernfreigabe. Muster werden neu
berechnet. Ihre Identität enthält die abweichende Parameterkonfiguration, damit
Feedback nicht auf anders bewertete Muster übertragen wird. Bei Rückkehr zur
identischen Konfiguration kann deren bestehendes Feedback wieder sichtbar sein.
Präsenzgruppenwechsel löscht wie bisher Belege und Feedback nach UI-Bestätigung.
Widerruf stoppt die Erfassung; Reset löscht Lerndaten und widerruft die Freigabe.

## Module statt zweiter Engine

| Modul | Verfahren | Stand / Konfiguration |
|---|---|---|
| Zonenreferenzen | Median bzw. typisierte logische Verknüpfung | Implementiert; Sensorrollen, Zonenpause |
| Aktivitätsmuster v1 | Häufigkeiten pro lokalem Fenster | Implementiert; Freigabe, Quellen; Mindestbelege in PR #9 |
| Klima-Vorschläge | Feste profilspezifische Regeln | Implementiert; Zonenprofil, kein gelerntes Verhalten |
| Lichtkontext bei Aktivierungen | Gemeinsames Auftreten, keine Kausalität | In PR #9; zusätzliche Freigabe und Sensorgruppen |
| Lokale Rhythmen / Beobachtbarkeit | Zeitzone, Tagesgruppen und Prüfstichproben | In PR #9; keine durchgängige Abdeckungsmessung |
| Umsetzung | Typisierte Pläne mit Policy und Verifikation | Nur gesperrte Dry-run-Grenze vorhanden |

Das Modulregister zeigt implementiert/geplant/gesperrt. Es lädt keinen beliebigen
Python-Code und behauptet keine nachinstallierbaren Plugin-Algorithmen. Die
Aktivitätsanalyse wird über die Lernfreigabe geschaltet; Zonenpause stoppt deren
Auswertung. Künftige Lernmodule sollen denselben Speicher, dieselbe Quellenprüfung
und denselben Feedback-/Freigabevertrag verwenden.

## Wie Erkenntnisse umgesetzt werden sollen

Die folgenden Schritte sind Zielarchitektur, nicht vorhandene Aktorsteuerung:

1. **Musterkarte:** Quellen, Zeitraum, unabhängige Aktivierungen, Lücken,
   Algorithmusversion und Parameter. „Passt“ ist Relevanzfeedback.
2. **Umsetzungsvorschlag:** Gewünschten Komfort mit dem Nutzer klären; aus Aktivität
   allein lässt sich weder gewünschte Helligkeit noch Lüftungsbedarf ableiten.
3. **Bestandsprüfung:** Vorhandene Automationen und Skripte suchen. Wiederverwenden,
   eine konkrete Änderung vorschlagen oder bewusst einen neuen Entwurf erstellen.
4. **Vorschau / Schattenbetrieb:** Trigger und Bedingungen auswerten und anzeigen,
   wann die Aktion erfolgt wäre. Beobachtungsabdeckung und Konflikte sichtbar halten.
5. **Konkreter HA-Entwurf:** Bevorzugt ein natives HA-Skript für eine einzelne Aktion
   oder eine Automation für wiederkehrendes Verhalten. Entwurf mit echten IDs,
   Bedingungen, Schutzregeln und Rückweg; neue Automationen zunächst deaktiviert.
6. **Separate Freigabe:** Freigabe bindet konkrete Planversion, Zone, Zielentitäten,
   Parameter und Gültigkeitsdauer. Jede Planänderung entwertet die Freigabe.
7. **Gesichert anwenden und prüfen:** Erforderliche Sicherung, Voraussetzungen erneut
   prüfen, idempotent anwenden, Ergebnis kontrollieren. Aktionsspezifische
   Wiederherstellung; keine pauschalen Rückgängig-Versprechen.

Beispiel Badbereich: Eine morgens gehäufte Aktivität ist zunächst nur ein Muster.
Erst bestätigte Licht-/Helligkeitsdaten und der gewünschte Komfort erlauben einen
Entwurf wie „Bei Bewegung und ausreichender Dunkelheit Licht auf freigegebenen Wert“.
Eine Ausschaltregel braucht zusätzlich belegbare Abwesenheit bzw. abgestimmte
Nachlaufzeit. Fehlende Sensordaten dürfen nicht als Abwesenheit zählen.

## Spätere Ausführungsformen

- **Vorschläge:** Standard; der Nutzer prüft und entscheidet.
- **HA-Skript/Automation:** Für stabile Regeln bevorzugt, nachvollziehbar in HA und
  nach Einrichtung ohne laufende PilotSuite-Ausführung nutzbar.
- **Begrenzter PilotSuite-Betrieb:** Später optional für dynamische Zusammenhänge;
  nur erlaubte Dienste/Ziele, Zeit-/Wertgrenzen, Sperrzeiten, Konfliktprüfung,
  manuelle Vorrangschaltung, Protokoll und jederzeitiger Widerruf.

Keiner dieser späteren Ausführungswege wird durch „Lernen aktivieren“ oder „Passt“
freigeschaltet. Die aktuelle Alpha verweigert weiterhin sämtliche Apply-Aufrufe.
Die reine Konfiguration eines Algorithmus erweitert keine HA-Berechtigung.

## Nächste fachliche Schritte

Zuerst reale Quellen und Lernbelege in Erdkeller und Badbereich abnehmen.
Lokale Zeit, Prüfstichproben und Aktivierungs-Kontext sind im Entwicklungszweig
umgesetzt. Danach zeitliche Schaltfolgen und Entwurfsvorschau ergänzen. Aktorfreigabe erst mit geprüfter
Konflikt-, Sicherungs-, Ausführungs- und Wiederherstellungskette. Keine scheinbare
Wahrscheinlichkeit allein aus Mindestzählwerten ableiten.
