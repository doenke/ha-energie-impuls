from homeassistant.components.number import NumberEntity
from .devices import EnergieImpulsWallboxDevice, EnergieImpulsDevice
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    session = hass.data[DOMAIN]["session"]
    entity = HybridChargingCurrentNumber(hass, session)
    async_add_entities([entity], update_before_add=True)


class HybridChargingCurrentNumber(NumberEntity):
    def __init__(self, hass, session):
        self.hass = hass
        self._session = session
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
        return self._state

    async def async_update(self):
        try:
            data = await self._session.async_get_wallbox_data()
            _LOGGER.debug(f"Wallboxdaten für hybrid_charging_current: {data}")
            self._state = data["_set_point"].get("hybrid_charging_current", 0)
            if self._state is None:
                self._state = 0
            _LOGGER.info(f"Aktueller Hybridwert: {self._state}")
        except Exception as e:
            _LOGGER.error(f"Fehler beim Abrufen der Hybrid-Ladestromstärke: {e}")
            self._state = None

    async def async_set_native_value(self, value: float):
        if int(value) in (1, 2, 3, 4, 5):
            _LOGGER.warning(f"Wert {value} ist nicht erlaubt – wird ignoriert.")
            return

        try:
            payload = {
                "hybrid_charging_current": None if int(value) == 0 else int(value)
            }

            response = await self._session.async_put_wallbox_setpoint(payload)
            if response.status == 200:
                self._state = payload["hybrid_charging_current"]
                _LOGGER.info(f"Hybridwert erfolgreich gesetzt auf {self._state}")
            else:
                text = await response.text()
                raise Exception(f"Fehler beim Setzen: {response.status} → {text}")
        except Exception as e:
            _LOGGER.error(f"Fehler beim Setzen von hybrid_charging_current: {e}")
