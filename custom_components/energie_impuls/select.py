from homeassistant.components.select import SelectEntity
from .const import DOMAIN
from .api import EnergyImpulsSession
import logging

_LOGGER = logging.getLogger(__name__)

WALLBOX_MODES = [
    "Schnellladen",
    "reines Überschussladen",
    "Schnelles Überschussladen",
    "Nicht laden"
]

async def async_setup_entry(hass, entry, async_add_entities):
    session = EnergyImpulsSession()
    async_add_entities([WallboxModeSelect(session)], update_before_add=True)

class WallboxModeSelect(SelectEntity):
    def __init__(self, session):
        self._session = session
        self._attr_name = "Wallbox Lademodus"
        self._attr_unique_id = "energie_impuls_wallbox_mode"
        self._attr_options = WALLBOX_MODES
        self._attr_current_option = None

    def update(self):
        try:
            data = self._session.get_wallbox_data()
            # Mapping der internen Modus-Codes zu benutzerfreundlichen Labels
            mode_code = data["_state"].get("mode")
            self._attr_current_option = self._map_code_to_label(mode_code)
        except Exception as e:
            _LOGGER.error(f"Fehler beim Lesen des Wallbox-Modus: {e}")

    def select_option(self, option: str):
        _LOGGER.info(f"Lademodus wird gesetzt auf: {option}")
        # Optional: sende API-Aufruf zur Modusumschaltung
        # Hier z. B. Session PUT auf /setpoint mit gewünschtem Modus
        self._attr_current_option = option
        self.async_write_ha_state()

    def _map_code_to_label(self, code):
        # Optional: Mapping von internen Werten auf Labels
        mapping = {
            0: "nicht laden",
            1: "Schnellladen",
            2: "reines Überschussladen",
            3: "schnelles Überschussladen"
        }
        return mapping.get(code, "Unbekannt")
    @property
    def device_info(self):
         return {
            "identifiers": {(DOMAIN, f"wallbox_{hass.data[DOMAIN]["wb_device_id"]}")},
            "name": "Energie Impuls Wallbox",
            "manufacturer": "ABB",
            "model": hass.data[DOMAIN]["wb_device_name"],
            "configuration_url": "https://energie-impuls.site",
        }
