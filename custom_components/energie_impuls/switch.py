
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .const import WALLBOX_SETPOINT_URL
from .sensor import EnergyImpulsSession
import requests
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    session = EnergyImpulsSession(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    switches = [
        EnergieImpulsSwitch(session, "Wallbox Sperre", "locked"),
        EnergieImpulsSwitch(session, "Überschussladen", "surplus_charging"),
    ]
    async_add_entities(switches, update_before_add=True)

class EnergieImpulsSwitch(SwitchEntity):
    def __init__(self, session, name, key):
        self._session = session
        self._name = name
        self._key = key
        self._state = False
        self._attr_unique_id = f"energie_impuls_switch_{key}"

    @property
    def is_on(self):
        return self._state

    @property
    def name(self):
        return self._name

    def turn_on(self, **kwargs):
        try:
            self._session.get_token()
            self._set_state(True)
        except Exception as e:
            _LOGGER.error(f"Fehler beim Aktivieren von {self._key}: {e}")

    def turn_off(self, **kwargs):
        try:
            self._session.get_token()
            self._set_state(False)
        except Exception as e:
            _LOGGER.error(f"Fehler beim Deaktivieren von {self._key}: {e}")

    def _set_state(self, value):
        headers = {
            "Authorization": f"Bearer {self._session.token}",
            "Content-Type": "application/json"
        }
        response = requests.put(WALLBOX_SETPOINT_URL, headers=headers, json={self._key: value})
        if response.status_code in (200, 201, 204):
            self._state = value
        else:
            raise Exception(f"Fehler bei API: {response.status_code}")

    def update(self):
        try:
            data = self._session.get_wallbox_data()
            self._state = data["_set_point"].get(self._key, False)
        except Exception as e:
            _LOGGER.error(f"Updatefehler Switch {self._key}: {e}")
