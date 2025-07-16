from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .devices import EnergieImpulsWallboxDevice, EnergieImpulsDevice
from .const import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)

SCHNELLLADEN = "Schnellladen"
SCHNELLLADEN_JSON = {
                "locked": False,
                "surplus_charging": False
                }
UEBERSCHUSS = "reines Überschussladen"
UEBERSCHUSS_JSON = {
                "locked": False,
                "surplus_charging": True,
                "hybrid_charging_current": None
                }
HYBRID = "Hybridladen"
HYBRID_JSON =  {
                "locked": False,
                "surplus_charging": True,
                "hybrid_charging_current": 6
                }
NICHTLADEN = "nicht laden"
NICHTLADEN_JSON =  {
            "locked": True
            }
ERROR = "Fehler"

WALLBOX_MODES = [
    SCHNELLLADEN,
    UEBERSCHUSS,
    HYBRID,
    NICHTLADEN,
    ERROR
]

async def async_setup_entry(hass, entry, async_add_entities):
    wallbox_coordinator = hass.data[DOMAIN]["coordinator_wallbox"]
    async_add_entities([WallboxModeSelect(hass,wallbox_coordinator)], update_before_add=True)

class WallboxModeSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, hass, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Wallbox Lademodus"
        self._attr_unique_id = "energie_impuls_wallbox_mode"
        self._attr_options = WALLBOX_MODES
        self.hass = hass
    
    async def async_update(self):
        await self.coordinator.async_request_refresh()

    @property
    def current_option(self):
        try:
            if self.coordinator.data["_set_point"]["locked"] == True:
                return NICHTLADEN
            if self.coordinator.data["_set_point"]["surplus_charging"] == True:
                if self.coordinator.data["_set_point"].get("hybrid_charging_current", 0) == 0:
                    return UEBERSCHUSS
                else:
                    return HYBRID
            else:
                return SCHNELLLADEN
        except:
            return ERROR
        
    async def async_select_option(self, option: str):
        if option == SCHNELLLADEN:
            payload = SCHNELLLADEN_JSON
        elif option == UEBERSCHUSS:
            payload = UEBERSCHUSS_JSON
        elif option == HYBRID:
            payload = HYBRID_JSON
        elif option == NICHTLADEN:
            payload = NICHTLADEN_JSON

        try:
            response = await self.coordinator.session.async_set_wallbox_mode(payload)
        except as e::
           _LOGGER.error(f"Fehler beim Setzen des Lademodus: {e}")
           
    @property
    def device_info(self):
         return EnergieImpulsWallboxDevice(self.hass).device_info
