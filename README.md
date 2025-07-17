# Energie Impuls Integration für Home Assistant

Diese benutzerdefinierte Home Assistant-Integration verbindet dein Smart Home mit dem [Energie Impuls](https://energie-impuls.site). Sie liest Energiedaten aus und ermöglicht das Steuern der Wallbox direkt über Home Assistant. Ausserdem stellt sie intelligente Ladeautomatiken zur Verfügung.

## ⚙️ Funktionen

- **Live-Sensoren**:
  - PV-Erzeugung, Netzeinspeisung, Haushaltsverbrauch,...
  - Batterie-SOC (State of Charge)
  - Wallbox-Verbrauch & -Modus
- **Wallbox-Steuerung, wie in der Energie-Impuls App**
- **Logik-Elemente**:
  - Lademodus statt einzelne Wallbox-Schalter
  - Ladeautomatik um bei maximiertem Eigenverbrauch trotzdem morgens das Auto voll geladen zu haben

---

## 🔧 Installation über HACS (empfohlen)

1. Öffne HACS → **Integrationen**
2. Klicke auf das Menü (⋮) → **Benutzerdefiniertes Repository hinzufügen**
3. Gib folgendes ein: https://github.com/doenke/ha-energie-impuls, Wähle **Integration** als Typ.
4. Nach Installation: Home Assistant neustarten
5. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**
6. Wähle **Energie Impuls**, trage Benutzername und Passwort ein

---

## 🧾 Manuelle Installation (alternativ)

1. Lade das [ZIP-Archiv](https://github.com/doenke/ha-energie-impuls/archive/refs/heads/main.zip) herunter
2. Entpacke es und kopiere den Ordner `custom_components/energie_impuls/` nach: config/custom_components/energie_impuls/
3. Starte Home Assistant neu

---

## ⚙️ Konfiguration (über UI)

Die Integration wird komplett über das Home Assistant-UI konfiguriert. Es sind folgende Angaben notwendig:

- `Benutzername`: Dein Login bei energie-impuls.site
- `Passwort`: Dein Passwort

Nach erfolgreichem Login wird ein Zugriffstoken gespeichert und automatisch erneuert, falls nötig.

---

## 📊 Verfügbare Entitäten

### 🔍 Sensoren

| Entity ID                             | Beschreibung                  | Einheit |
|--------------------------------------|-------------------------------|---------|
| `sensor.energie_impuls_pv`           | PV-Erzeugung                  | kW      |
| `sensor.energie_impuls_to_grid`      | Einspeisung ins Netz          | kW      |
| `sensor.energie_impuls_to_battery`   | Batterie wird geladen         | kW      |
| `sensor.energie_impuls_wallbox`      | Wallbox-Verbrauch             | kW      |
| `sensor.energie_impuls_household`    | Haushaltsverbrauch            | kW      |
| `sensor.energie_impuls_battery_soc`  | Ladezustand der Batterie      | %       |
| `sensor.wallbox_status`              | Statusmeldung der Wallbox     | Text    |
| `sensor.wallbox_consumption`         | Verbrauch der Wallbox         | kW      |

### 🔌 Switches

| Switch Entity ID                       | Funktion                         |
|----------------------------------------|----------------------------------|
| `switch.wallbox_sperre`                | Wallbox sperren/freigeben       |
| `switch.wallbox_ueberschussladen`      | Überschussladen aktivieren      |

---

# 🔄 Automatikmodus
Die Integration bietet einen leistungsfähigen Automatikmodus, der die Wallbox je nach PV-Erzeugung und gewähltem Modus automatisch steuert.

## 🧠 Funktionsweise
Die Automatik analysiert regelmäßig die aktuelle PV-Erzeugung und entscheidet abhängig vom gewählten Modus, ob und wie die Wallbox laden soll. Dabei kommen verschiedene Strategien zum Einsatz, zum Beispiel:

- Hybrid-Automatik: Wallbox lädt nur dann im Hybrid-Modus (mit mind. 6A), wenn die PV-Erzeugung über einem konfigurierbaren Schwellenwert liegt (z. B. 1.5 kW) und dies für eine gewisse Zeitspanne (z. B. 10 Minuten) konstant bleibt. Andernfalls wird der Ladevorgang beendet. Somit kann auch bei geringerer Sonneneinstrahlung der ins Auto geladene Strom maximiert werden.

- Überschuss-Automatik: Es wird nur geladen, wenn tatsächlich ein PV-Überschuss vorhanden ist.

- Schnellladen-Automatik: Die Wallbox wird dauerhaft auf Schnellladen gesetzt, unabhängig von der PV-Erzeugung.

- Nachtmodi: Varianten der Hybrid-/Überschussmodi, die bei unzureichender PV-Leistung auf Schnellladen umschalten. Damit ist sichergestellt, dass das Auto am nächsten Morgen auf jeden Fall voll geladen ist.

- Manuell: Diese Einstellung macht nichts und erlaub eine dauerhafte manuelle Bedienung
 
Diese Modi lassen sich bequem über das select.wallbox_automatikmodus-Entity auswählen.
## Überschreiben der Automatik
Sobald irgendein Parameter von Hand umgestellt wird, so schaltet sich die Automatik ab. Wenn der Wallbox-Zustand sich auf "Fahrzeug nicht verbunden" (Auto wurde abgeklemmt) ändert, dann aktiviert sich die Automatik von selbst wieder, um den nächsten Ladevorgang wieder über die Automatik zu steuern. Wer das nicht möchte, der sollte den Automatik-Modus "Manuell" auswählen.

# 🧑‍💻 Wünsche an Planville
- Bereitstellung der Gesamt-Zählerwerte über die API, um das HA Energie Dashboard auch ohne die unzuverlässige China Cloud nutzen zu können
- Zugriff auf den Wechselrichter, um den Modus einstellen zu könnn, ob Last zuerst aus dem Netz oder aus der Batterie genommen wird, um eine Schonfunktion für die Batterie zu bauen
- Eine lokale API, um den Umweg über das Internet unnötig zu machen
- Zugriff auf die API über einen festen Token

# TODO
- Alle Parameter konfigurierbar machen
- Solarprognose einbauen
   - Strombedarf Auto
   - Solarprognose
   - Automatisch Modus bestimmen, um morgen früh voll zu sein 

## 🧑‍💻 Mitwirken

Pull Requests, Bug Reports und Verbesserungsvorschläge sind willkommen. Bitte beschreibe deine Änderungen klar und verständlich.

---

## 📜 Lizenz

MIT License – siehe [LICENSE](LICENSE)

