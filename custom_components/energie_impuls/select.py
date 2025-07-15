from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .devices import EnergieImpulsWallboxDevice, EnergieImpulsDevice
from .const import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)

SCHNELLLADEN = "Schnellladen"
UEBERSCHUSS = "reines Überschussladen"
HYBRID = "Hybridladen"
NICHTLADEN = "nicht laden"
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
        self.coordinator = coordinator
        self._attr_name = "Wallbox Lademodus"
        self._attr_unique_id = "energie_impuls_wallbox_mode"
        self._attr_options = WALLBOX_MODES
        self._attr_current_option = None
        self.hass = hass
    
    async def async_update(self):
        await self.coordinator.async_request_refresh()

    @property
    def current_option(self):
        try:
            if self.coordinator.data["_set_point"]["locked"] == True:
                return NICHTLADEN
            if self.coordinator.data["_set_point"]["surplus_charging"] == True:
                if self.coordinator.data["_set_point"]get("hybrid_charging_current", 0) == 0:
                    return UEBERSCHUSS
                else:
                    return HYBRID
            else:
                return SCHNELLLADEN
        except:
            return ERROR
        
    def select_option(self, option: str):
        if option == SCHNELLLADEN:
        elif option == UEBERSCHUSS:
        elif option == HYBRID:
        elif option == NICHTLADEN:

        payload = {
                "hybrid_charging_current": 6
            }

            response = await self.coordinator.session.async_put_wallbox_setpoint(payload)

    @property
    def device_info(self):
         return EnergieImpulsWallboxDevice(self.hass).device_info
