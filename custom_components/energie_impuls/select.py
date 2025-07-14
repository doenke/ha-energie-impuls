from homeassistant.components.select import SelectEntity
from .devices import EnergieImpulsWallboxDevice, EnergieImpulsDevice
from .const import DOMAIN
from .api import EnergyImpulsSession
import logging

_LOGGER = logging.getLogger(__name__)

WALLBOX_MODES = [
    "Schnellladen",
    "reines Überschussladen",
    "Hybridladen",
    "Nicht laden"
]

async def async_setup_entry(hass, entry, async_add_entities):
    session =  hass.data[DOMAIN]["session"]
    async_add_entities([WallboxModeSelect(hass,session)], update_before_add=True)

class WallboxModeSelect(SelectEntity):
    def __init__(self, hass, session):
        self._session = session
        self._attr_name = "Wallbox Lademodus"
        self._attr_unique_id = "energie_impuls_wallbox_mode"
        self._attr_options = WALLBOX_MODES
        self._attr_current_option = None
        self.hass = hass
    #def update(self):
    #    try:
    #        #data = self._session.get_wallbox_data()
    #        # Mapping der internen Modus-Codes zu benutzerfreundlichen Labels
    #        mode_code = data["_state"].get("mode")
    #        self._attr_current_option = self._map_code_to_label(mode_code)
    #    except Exception as e:
    #        _LOGGER.error(f"Fehler beim Lesen des Wallbox-Modus: {e}")

    def select_option(self, option: str):
        _LOGGER.info(f"Lademodus wird gesetzt auf: {option}")
        # Optional: sende API-Aufruf zur Modusumschaltung
        # Hier z. B. Session PUT auf /setpoint mit gewünschtem Modus
        self._attr_current_option = option
        

    def _map_code_to_label(self, code):
        # Optional: Mapping von internen Werten auf Labels
        mapping = {
            0: "nicht laden",
            1: "Schnellladen",
            2: "reines Überschussladen",
            3: "Hybridladen"
        }
        return mapping.get(code, "Unbekannt")
    @property
    def device_info(self):
         return EnergieImpulsWallboxDevice(self.hass).device_info
