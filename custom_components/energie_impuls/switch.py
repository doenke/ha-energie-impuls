from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .devices import EnergieImpulsWallboxDeviceInfoMixin
from .const import DOMAIN, CONF_AUTO_SWITCH_ENTITY
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN]["coordinator_wallbox"]
    switches = [
        EnergieImpulsSwitch(hass, coordinator, "Wallbox Sperre", "locked", "mdi:lock"),
        EnergieImpulsSwitch(hass, coordinator, "Überschussladen", "surplus_charging", "mdi:octagram-plus"),
        AutomaticModeActiveSwitch(hass),
    ]
    async_add_entities(switches, update_before_add=True)

class EnergieImpulsSwitch(EnergieImpulsWallboxDeviceInfoMixin,CoordinatorEntity, SwitchEntity):
    def __init__(self, hass, coordinator, name, key, icon=None):
        super().__init__(coordinator)
        self.hass = hass
        self._attr_name = name
        self._key = key
        self._attr_unique_id = f"energie_impuls_switch_{key}"
        self._attr_icon = icon

    @property
    def is_on(self):
        return self.coordinator.data.get("_set_point", {}).get(self._key, False)

    async def async_turn_on(self, **kwargs):
        try:
            await self._async_set_state(True)
        except Exception as e:
            _LOGGER.error(f"Fehler beim Aktivieren von {self._key}: {e}")

    async def async_turn_off(self, **kwargs):
        try:
            await self._async_set_state(False)
        except Exception as e:
            _LOGGER.error(f"Fehler beim Deaktivieren von {self._key}: {e}")

    async def _async_set_state(self, value):
        await self.hass.data[DOMAIN][CONF_AUTO_SWITCH_ENTITY].async_turn_off()
        await self.coordinator.async_set_wallbox_mode({self._key: value})
        
    async def async_update(self):
        await self.coordinator.async_request_refresh()

class AutomaticModeActiveSwitch(EnergieImpulsWallboxDeviceInfoMixin,RestoreEntity, SwitchEntity):
    def __init__(self, hass):
        super().__init__()
        self.hass = hass
        self._state = False
        self._attr_name = "Automatik aktiv"
        self._attr_unique_id = "energie_impuls_automatic_status"
        self._attr_icon = "mdi:refresh-auto"
        hass.data[DOMAIN][CONF_AUTO_SWITCH_ENTITY] = self

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        old_state = await self.async_get_last_state()
        if old_state is not None:
            self._state = old_state.state == "on"
            _LOGGER.info(f"Zustand wiederhergestellt: {self._state}")
        else:
            self._state = False
    
    @property
    def is_on(self):
        return self._state

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
