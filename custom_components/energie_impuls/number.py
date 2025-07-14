from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .devices import EnergieImpulsWallboxDevice
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN]["coordinator_wallbox"]
    entity = HybridChargingCurrentNumber(hass, coordinator)
    async_add_entities([entity], update_before_add=True)


class HybridChargingCurrentNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, hass, coordinator):
        super().__init__(coordinator)
        self.hass = hass
        self.coordinator = coordinator
        self._attr_name = "Hybrid Charging Current"
        self._attr_unique_id = "energie_impuls_hybrid_current"
        self._attr_unit_of_measurement = "A"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 16
        self._attr_native_step = 1
        self._attr_icon = "mdi:battery-plus"
        self._state = None

    @property
    def native_value(self):
        try:
            return self.coordinator.data["_set_point"].get("hybrid_charging_current", 0)
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

            response = await self.coordinator.session.async_put_wallbox_setpoint(payload)
            #if response.status in (200, 201, 204):
            #    _LOGGER.info(f"Hybridwert erfolgreich gesetzt auf {payload['hybrid_charging_current']}")
            #    await self.coordinator.async_request_refresh()
            #else:
            #    text = await response.text()
            #    raise Exception(f"Fehler beim Setzen: {response.status} → {text}")
        except Exception as e:
            _LOGGER.error(f"Fehler beim Setzen von hybrid_charging_current: {e}")

    @property
    def device_info(self):
        return EnergieImpulsWallboxDevice(self.hass).device_info
