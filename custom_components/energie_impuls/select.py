from homeassistant.components.select import SelectEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .devices import EnergieImpulsWallboxDeviceInfoMixin
from .const import DOMAIN, CONF_AUTO_SWITCH_ENTITY, CONF_MODE_ENTITY, PAYLOADS
from .const import SOFORTLADEN, UEBERSCHUSS, HYBRID, NICHTLADEN, ERROR 
from .const import AM_SOFORTLADEN, AM_UEBERSCHUSS, AM_HYBRIDAUTOMATIK, AM_UEBERSCHUSS_NACHT, AM_HYBRIDAUTOMATIK_NACHT, AM_MANUAL

import logging
_LOGGER = logging.getLogger(__name__)

WALLBOX_MODES = [
    SOFORTLADEN,
    UEBERSCHUSS,
    HYBRID,
    NICHTLADEN,
    ERROR
]

AUTOMATIC_MODES = [
  AM_SOFORTLADEN,
  AM_UEBERSCHUSS,
  AM_HYBRIDAUTOMATIK,
  AM_UEBERSCHUSS_NACHT,
  AM_HYBRIDAUTOMATIK_NACHT,
  AM_MANUAL
]


async def async_setup_entry(hass, entry, async_add_entities):
    wallbox_coordinator = hass.data[DOMAIN]["coordinator_wallbox"]
    entities = [
          WallboxModeSelect(hass,wallbox_coordinator),
          WallboxAutomaticModeSelect(hass)
          ]

    async_add_entities(entities, update_before_add=True)



class WallboxModeSelect(EnergieImpulsWallboxDeviceInfoMixin,CoordinatorEntity, SelectEntity):
    def __init__(self, hass, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Wallbox Lademodus"
        self._attr_unique_id = "energie_impuls_wallbox_mode"
        self._attr_options = WALLBOX_MODES
        self._attr_icon = "mdi:ev-plug-type2"
        self.hass = hass
    
    async def async_update(self):
        await self.coordinator.async_request_refresh()

    @property
    def current_option(self):
        try:
            if self.coordinator.data["_set_point"]["locked"] == True:
                return NICHTLADEN
            if self.coordinator.data["_set_point"]["surplus_charging"] == True:
                if (self.coordinator.data["_set_point"].get("hybrid_charging_current") or 0) == 0:
                    return UEBERSCHUSS
                else:
                    return HYBRID
            else:
                return SOFORTLADEN
        except:
            return ERROR
        
    async def async_select_option(self, option: str):
        self._attr_current_option = option
        try:
            await self.hass.data[DOMAIN][CONF_AUTO_SWITCH_ENTITY].async_turn_off()
            await self.coordinator.async_set_wallbox_mode(PAYLOADS[option])
        except KeyError as e:
            pass
        except Exception as e:
           _LOGGER.error(f"Fehler beim Setzen des Lademodus: {e}")

class WallboxAutomaticModeSelect(EnergieImpulsWallboxDeviceInfoMixin,RestoreEntity, SelectEntity):
    def __init__(self, hass):
        super().__init__()
        self._attr_name = "Wallbox Automatikmodus"
        self._attr_unique_id = "energie_impuls_automatic_mode"
        self._attr_options = AUTOMATIC_MODES
        self._attr_icon = "mdi:auto-mode"
        self.hass = hass
        self._key = AM_MANUAL
        hass.data[DOMAIN][CONF_MODE_ENTITY] = self

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._attr_current_option = last_state.state
            _LOGGER.debug(f"[{self._key}] Wiederhergestellter Zustand: {self._attr_current_option}")
        else:
            self._attr_current_option = AM_MANUAL  # Optionaler Fallback
            _LOGGER.debug(f"[{self._key}] Kein gespeicherter Zustand gefunden – Manuell gesetzt")
        self.async_write_ha_state()

    @property
    def current_option(self):
        return self._attr_current_option
        
    async def async_select_option(self, option: str):
        self._attr_current_option = option
        await self.hass.data[DOMAIN][CONF_AUTO_SWITCH_ENTITY].async_turn_on()
        self.async_write_ha_state()
        controller = self.hass.data[DOMAIN].get("automatik_controller")
        if controller:
            await controller.async_update()
