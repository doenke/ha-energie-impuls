from homeassistant.components.select import SelectEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
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

# Automatiklabel
AM_SCHNELLLADEN = SCHNELLLADEN
AM_UEBERSCHUSS = UEBERSCHUSS
AM_HYBRIDAUTOMATIK = "Hybridautomatik"
AM_UEBERSCHUSS_NACHT = "Überschuss, über Nacht voll"
AM_HYBRIDAUTOMATIK_NACHT = "Hybrid, über Nacht voll"
AM_MANUAL = "Manuell"

WALLBOX_MODES = [
    SCHNELLLADEN,
    UEBERSCHUSS,
    HYBRID,
    NICHTLADEN,
    ERROR
]

AUTOMATIC_MODES = [
  AM_SCHNELLLADEN,
  AM_UEBERSCHUSS,
  AM_HYBRIDAUTOMATIK,
  AM_UEBERSCHUSS_NACHT,
  AM_HYBRIDAUTOMATIK_NACHT,
  AM_MANUAL
]

MIN_HYBRID = 1.5
MIN_HYBRID_MINUTES = 10


async def async_setup_entry(hass, entry, async_add_entities):
    wallbox_coordinator = hass.data[DOMAIN]["coordinator_wallbox"]
    entities = [
          WallboxModeSelect(hass,wallbox_coordinator),
          AutomaticModeActiveSwitch(hass),
          WallboxAutomaticModeSelect(hass,wallbox_coordinator)
          ]

    async_add_entities(entities, update_before_add=True)

class WallboxAutomaticModeSelect(CoordinatorEntity, RestoreEntity, SelectEntity):
    def __init__(self, hass, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Wallbox Automatikmodus"
        self._attr_unique_id = "energie_impuls_automatic_mode"
        self._attr_options = AUTOMATIC_MODES
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
        
    #async def async_select_option(self, option: str):
    #    if option == AM_SCHNELLLADEN:
    #        payload = SCHNELLLADEN_JSON
    #    elif option == AM_UEBERSCHUSS:
    #        payload = UEBERSCHUSS_JSON
    #    elif option == AM_HYBRIDAUTOMATIK:
    #        payload = HYBRID_JSON
    #    elif option == AM_UEBERSCHUSS_NACHT:
    #        payload = NICHTLADEN_JSON
    #    else:
    #      return

    #    try:
    #        await self.coordinator.async_set_wallbox_mode(payload)
    #        self._attr_current_option = option
    #        self.async_write_ha_state()
    #    except Exception as e:
    #       _LOGGER.error(f"Fehler beim Setzen des Lademodus: {e}")
           
    @property
    def device_info(self):
         return EnergieImpulsWallboxDevice(self.hass).device_info

class AutomaticModeActiveSwitch(RestoreEntity, SwitchEntity):
    def __init__(self, hass):
        self.hass = hass
        self._state = False
        self._attr_name = "Automatik"
        self._attr_unique_id = "energie_impuls_automatic_status"
        self._attr_icon = "mdi:weather-night"
        hass.data[DOMAIN][CONF_AUTO_SWITCH_ENTITY] = self

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        old_state = await self.async_get_last_state()
        if old_state is not None:
            self._state = old_state.state == "on"
            _LOGGER.info(f"Zustand wiederhergestellt: {self._state}")

    @property
    def is_on(self):
        return self._state

    @property
    def device_info(self):
        return EnergieImpulsWallboxDevice(self.hass).device_info

    async def async_turn_on(self, **kwargs):
        _LOGGER.info("Ladeautomatik aktiviert")
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        _LOGGER.info("Ladeautomatik deaktiviert")
        self._state = False
        self.async_write_ha_state()

    async def async_update(self):
        pass

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
                if (self.coordinator.data["_set_point"].get("hybrid_charging_current") or 0) == 0:
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
            await self.coordinator.async_set_wallbox_mode(payload)
        except Exception as e:
           _LOGGER.error(f"Fehler beim Setzen des Lademodus: {e}")
           
    @property
    def device_info(self):
         return EnergieImpulsWallboxDevice(self.hass).device_info
