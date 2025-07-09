
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN
from .api import EnergyImpulsSession
import requests
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    session = hass.data[DOMAIN]["session"]
    self.hass = hass
    switches = [
        EnergieImpulsSwitch(session, "Wallbox Sperre", "locked","mdi:lock"),
        EnergieImpulsSwitch(session, "Überschussladen", "surplus_charging","mdi:octagram-plus"),
        NightFullChargeSwitch(hass),
    ]
    async_add_entities(switches, update_before_add=True)

class EnergieImpulsSwitch(SwitchEntity):
    def __init__(self, session, name, key,icon=None):
        self._session = session
        self._name = name
        self._key = key
        self._state = False
        self._attr_unique_id = f"energie_impuls_switch_{key}"
        self._attr_icon = icon

    @property
    def is_on(self):
        return self._state

    @property
    def device_info(self):
         return {
            "identifiers": {(DOMAIN, f"wallbox_{hass.data[DOMAIN]["wb_device_id"]}")},
            "name": "Energie Impuls Wallbox",
            "manufacturer": "ABB",
            "model": hass.data[DOMAIN]["wb_device_name"],
            "configuration_url": "https://energie-impuls.site",
        }

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

class NightFullChargeSwitch(RestoreEntity, SwitchEntity):
    def __init__(self, hass):
        self._state = False
        self._attr_name = "Vollladen über Nacht"
        self._attr_unique_id = "energie_impuls_night_fullcharge"
        self._attr_icon = "mdi:weather-night"
        self.hass = hass
        
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
         return {
            "identifiers": {(DOMAIN, f"wallbox_{hass.data[DOMAIN]["wb_device_id"]}")},
            "name": "Energie Impuls Wallbox",
            "manufacturer": "ABB",
            "model": self.hass.data[DOMAIN]["wb_device_name"],
            "configuration_url": "https://energie-impuls.site",
        }
        
    def turn_on(self, **kwargs):
        _LOGGER.info("Vollladen über Nacht aktiviert")
        self._state = True

    def turn_off(self, **kwargs):
        _LOGGER.info("Vollladen über Nacht deaktiviert")
        self._state = False

    def update(self):
        pass  # Keine Abhängigkeit von externen Daten
