from homeassistant.components.number import NumberEntity
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .const import WALLBOX_SETPOINT_URL
from .sensor import EnergyImpulsSession
import requests
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    session = EnergyImpulsSession(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    entity = HybridChargingCurrentNumber(session)
    async_add_entities([entity], update_before_add=True)

class HybridChargingCurrentNumber(NumberEntity):
    def __init__(self, session):
        self._session = session
        self._attr_name = "Hybrid Charging Current"
        self._attr_unique_id = "energie_impuls_hybrid_current"
        self._attr_unit_of_measurement = "A"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 11
        self._attr_native_step = 1
        self._state = None

    def update(self):
        try:
            data = self._session.get_wallbox_data()
            self._state = data["_set_point"].get("hybrid_charging_current", 0)
        except Exception as e:
            _LOGGER.error(f"Fehler beim Abrufen der Hybrid-Ladestromstärke: {e}")
            self._state = None
    
    def set_native_value(self, value: float) -> None:
        try:
            self._session.get_token()
            headers = {
                "Authorization": f"Bearer {self._session.token}",
                "Content-Type": "application/json"
            }
    
            # 💡 0 in HA soll null in der API werden
            payload = {
                "hybrid_charging_current": None if int(value) == 0 else int(value)
            }
    
            response = requests.put(WALLBOX_SETPOINT_URL, headers=headers, json=payload)
            if response.status_code in (200, 201, 204):
                self._state = None if int(value) == 0 else int(value)
            else:
                raise Exception(f"Fehler beim Setzen: {response.status_code} → {response.text}")
        except Exception as e:
            _LOGGER.error(f"Fehler beim Setzen von hybrid_charging_current: {e}")
    
    
