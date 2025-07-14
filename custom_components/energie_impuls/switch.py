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
        NightFullChargeSwitch(hass),
    ]
    async_add_entities(switches, update_before_add=True)

class EnergieImpulsSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, hass, coordinator, name, key, icon=None):
        super().__init__(coordinator)
        self.hass = hass
        self._coordinator = coordinator
        self._name = name
        self._key = key
        self._attr_unique_id = f"energie_impuls_switch_{key}"
        self._attr_icon = icon

    @property
    def is_on(self):
        return self._coordinator.data["_set_point"].get(self._key, False)

    @property
    def name(self):
        return self._name

    @property
    def device_info(self):
        return EnergieImpulsWallboxDevice(self.hass).device_info

    async def async_turn_on(self, **kwargs):
        try:
            await self._coordinator.session.async_get_token()
            await self._async_set_state(True)
            self._coordinator.data["_set_point"].set(self._key, True)
            await self._coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Fehler beim Aktivieren von {self._key}: {e}")

    async def async_turn_off(self, **kwargs):
        try:
            await self._coordinator.session.async_get_token()
            await self._async_set_state(False)
            self._coordinator.data["_set_point"].set(self._key, False)
            await self._coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Fehler beim Deaktivieren von {self._key}: {e}")

    async def _async_set_state(self, value):
        response = await self._coordinator.session.async_put_wallbox_setpoint({self._key: value})
        if response.status in (200, 201, 204):
            await self._coordinator.async_request_refresh()
        else:
            raise Exception(f"Fehler bei API: {response.status}")

    async def async_update(self):
        await self._coordinator.async_request_refresh()

class NightFullChargeSwitch(RestoreEntity, SwitchEntity):
    def __init__(self, hass):
        self.hass = hass
        self._state = False
        self._attr_name = "Vollladen über Nacht"
        self._attr_unique_id = "energie_impuls_night_fullcharge"
        self._attr_icon = "mdi:weather-night"

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
        _LOGGER.info("Vollladen über Nacht aktiviert")
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        _LOGGER.info("Vollladen über Nacht deaktiviert")
        self._state = False
        self.async_write_ha_state()

    async def async_update(self):
        pass
