from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .devices import EnergieImpulsWallboxDevice, EnergieImpulsDevice
from .const import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)

WALLBOX_MODES = [
    "Schnellladen",
    "reines Überschussladen",
    "Hybridladen",
    "Nicht laden",
    "Fehler"
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
    def current_option(self)
        try:
            if self.coordinator.data["_set_point"]["locked"] == True:
                return 0
            if self.coordinator.data["_set_point"]["surplus_charging"] == True:
                if self.coordinator.data["_set_point"]get("hybrid_charging_current", 0) == 0:
                    return 2
                else:
                    return 3
            else:
                return 1
        except:
            return 4
        
    def select_option(self, option: str):
        if option == "1":
        elif option == "2":
        elif option == "3":
        elif option == "4":

        payload = {
                "hybrid_charging_current": None if int(value) == 0 else int(value)
            }

            response = await self.coordinator.session.async_put_wallbox_setpoint(payload)
    def _map_code_to_label(self, code):
        # Optional: Mapping von internen Werten auf Labels
        mapping = {
            0: "nicht laden",
            1: "Schnellladen",
            2: "reines Überschussladen",
            3: "Hybridladen"
            4: "Fehler"
        }
        return mapping.get(code, "Unbekannt")
    @property
    def device_info(self):
         return EnergieImpulsWallboxDevice(self.hass).device_info
