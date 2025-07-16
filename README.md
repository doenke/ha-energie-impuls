# Energie Impuls Integration für Home Assistant

Diese benutzerdefinierte Home Assistant-Integration verbindet dein Smart Home mit dem Portal [energie-impuls.site](https://energie-impuls.site). Sie liest Energiedaten aus und ermöglicht das Steuern der Wallbox direkt über Home Assistant.

## ⚙️ Funktionen

- **Live-Sensoren**:
  - PV-Erzeugung, Netzeinspeisung, Haushaltsverbrauch,...
  - Batterie-SOC (State of Charge)
  - Wallbox-Verbrauch & -Modus
- **Steuerbare Entitäten**:
  - Wallbox-Sperre (`locked`)
  - Überschussladen (`surplus_charging`)
  - Ladestrom (`hybrid_charging_current`) in Ampere
- **Logik-Elemente**:
  - Automatik: „Vollladen über Nacht“
    - aktiviert bei PV-Erzeugung = 0 über 10 Minuten
    - Gibt Wallbox frei und läd mit voller Geschwindigkeit
    - speichert und stellt Zustände automatisch wieder her, wenn der Ladestrom auf 0 abgesunken ist
       - Wallbox-Sperre (`locked`)
       - Überschussladen (`surplus_charging`)
       - Ladestrom (`hybrid_charging_current`)

    


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

## 🔁 Automatisierungen

### 💤 Vollladen über Nacht

- Wird aktiviert, wenn:
  - PV – Haushalt > 2 kW für 10 Minuten
- Aktionen:
  - Schaltet `surplus_charging` und `wallbox_sperre` aus
  - Setzt `hybrid_charging_current` auf 6 A
- Beendet, wenn:
  - Verbrauch = 0 für 10 Minuten
  - oder `switch.vollladen_uber_nacht` deaktiviert wird
- Stellt dann ursprüngliche Werte wieder her

## 🧑‍💻 Wünsche an Planville
- Bereitstellung der Gesamt-Zählerwerte über die API, um das HA Energie Dashboard auch ohne die unzuverlässige China Cloud nutzen zu können
- Zugriff auf den Wechselrichter, um den Modus einstellen zu könnn, ob Last zuerst aus dem Netz oder aus der Batterie genommen wird, um eine Schonfunktion für die Batterie zu bauen
- Eine lokale API, um den Umweg über das Internet unnötig zu machen
- Zugriff auf die API über einen festen Token

## TODO
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

