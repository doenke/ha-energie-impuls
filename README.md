# Energie Impuls Integration für Home Assistant

Diese benutzerdefinierte Home Assistant-Integration verbindet dein Smart Home mit dem Portal [energie-impuls.site](https://energie-impuls.site). Sie liest Energiedaten aus und ermöglicht das Steuern der Wallbox direkt über Home Assistant.

## ⚙️ Funktionen

- Authentifizierung über API-Login (Token-Handling integriert)
- Automatische Abfrage der Energieflüsse:
  - PV-Produktion
  - Netzeinspeisung
  - Batterieladung
  - Wallbox-Verbrauch
  - Haushaltsverbrauch
  - Batterie-Ladezustand (SoC)
- Auslesen des Wallbox-Status und Verbrauchs
- Steuerung der Wallbox:
  - **Wallbox sperren/freigeben**
  - **Überschussladen aktivieren/deaktivieren**

---

## 🧰 Voraussetzungen

- Home Assistant ≥ 2023.0
- Aktiver Account bei [energie-impuls.site](https://energie-impuls.site)
- Internetzugang vom Home Assistant Core aus

---

## 🔧 Installation über HACS (empfohlen)

1. Öffne HACS → **Integrationen**
2. Klicke auf das Menü (⋮) → **Benutzerdefiniertes Repository hinzufügen**
3. Gib folgendes ein: https://github.com/doenke/ha-energie-impuls


Wähle **Integration** als Typ.
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

## 🛠️ Entwicklung

Diese Integration befindet sich im Aufbau und wird weiterentwickelt. Geplante Features:

- Unterstützung mehrerer Wallboxen
- Automatische Ladeplanung
- Energie-Diagramme & Optimierung

---

## 🧑‍💻 Mitwirken

Pull Requests, Bug Reports und Verbesserungsvorschläge sind willkommen. Bitte beschreibe deine Änderungen klar und verständlich.

---

## 📜 Lizenz

MIT License – siehe [LICENSE](LICENSE)

---

## 🙏 Danke

An die Energie-Impuls-Community für die API und an das Home Assistant-Team für die Plattform ❤️
