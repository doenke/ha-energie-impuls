from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .devices import EnergieImpulsWallboxDevice
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN]["coordinator_wallbox"]
    switches = [
        EnergieImpulsSwitch(hass, coordinator, "Wallbox Sperre", "locked", "mdi:lock"),
        EnergieImpulsSwitch(hass, coordinator, "Überschussladen", "surplus_charging", "mdi:octagram-plus"),
    ]
    async_add_entities(switches, update_before_add=True)

class EnergieImpulsSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, hass, coordinator, name, key, icon=None):
        super().__init__(coordinator)
        self.hass = hass
        self._name = name
        self._key = key
        self._attr_unique_id = f"energie_impuls_switch_{key}"
        self._attr_icon = icon

    @property
    def is_on(self):
        return self.coordinator.data["_set_point"].get(self._key, False)

    @property
    def name(self):
        return self._name

    @property
    def device_info(self):
        return EnergieImpulsWallboxDevice(self.hass).device_info

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
        await self.coordinator.async_set_wallbox_mode({self._key: value})
        
    async def async_update(self):
        await self.coordinator.async_request_refresh()

