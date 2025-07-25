from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .devices import EnergieImpulsWallboxDeviceInfoMixin
from .const import DOMAIN,CONF_AUTO_SWITCH_ENTITY
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN]["coordinator_wallbox"]
    entity = HybridChargingCurrentNumber(hass, coordinator)
    async_add_entities([entity], update_before_add=True)


class HybridChargingCurrentNumber(EnergieImpulsWallboxDeviceInfoMixin,CoordinatorEntity, NumberEntity):
    def __init__(self, hass, coordinator):
        super().__init__(coordinator)
        self.hass = hass
        self._attr_name = "Hybridladestrom"
        self._attr_unique_id = "energie_impuls_hybrid_current"
        self._attr_device_class = "current"
        self._attr_unit_of_measurement = "A"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 16
        self._attr_native_step = 1
        self._attr_icon = "mdi:battery-plus"
        self._state = None

    @property
    def native_value(self):
        try:
            return self.coordinator.data["_set_point"].get("hybrid_charging_current") or 0
        except Exception as e:
            _LOGGER.error(f"Hybridwert nicht verfügbar: {e}")
            return 0

    async def async_set_native_value(self, value: float):
        if int(value) in (1, 2, 3, 4, 5):
            _LOGGER.warning(f"Wert {value} ist nicht erlaubt – wird ignoriert.")
            return

        try:
            payload = {
                "hybrid_charging_current": None if int(value) == 0 else int(value)
            }

            await self.coordinator.async_set_wallbox_mode(payload)
            await self.hass.data[DOMAIN][CONF_AUTO_SWITCH_ENTITY].async_turn_off()

        except Exception as e:
            _LOGGER.error(f"Fehler beim Setzen von hybrid_charging_current: {e}")
