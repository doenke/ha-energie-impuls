from homeassistant.helpers.entity import Entity
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN
from .api import EnergyImpulsSession
import requests
import logging

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "pv": {"name": "PV-Erzeugung", "unit": "kW","icon": "mdi:solar-power-variant"},
    "to_grid": {"name": "Netzeinspeisung", "unit": "kW","icon": "mdi:transmission-tower"},
    "to_battery": {"name": "Batterie-Ladung", "unit": "kW","icon": "mdi:battery-charging"},
    "household": {"name": "Haushalt", "unit": "kW","icon": "mdi:home"},
    "battery_soc": {"name": "Batterie Ladezustand", "unit": "%","icon": "mdi:battery-charging"}
}

async def async_setup_entry(hass, entry, async_add_entities):
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    session = EnergyImpulsSession()

    sensors = [EnergieImpulsSensor(session, key) for key in SENSOR_TYPES]

    # Zusätzliche Wallbox-Sensoren
    sensors.extend([
        WallboxSensor(session, "Wallbox Modus", "wallbox_mode_str", lambda d: d["_state"]["mode_str"],None,"mdi:ev-plug-type2"),
        WallboxSensor(session, "Wallbox Moduscode", "wallbox_mode", lambda d: d["_state"]["mode"]),
        WallboxSensor(session, "Wallbox Verbrauch", "wallbox_consumption", lambda d: d["_state"]["consumption"], "kW","mdi:ev-station"),
        WallboxSensor(session, "Wallbox Zeitstempel", "wallbox_timestamp", lambda d: d["_state"]["timestamp"]),
        WallboxSensor(session, "Wallbox Seit Modus aktiv", "wallbox_mode_since", lambda d: d["_state"]["mode_since"]),
        #WallboxSensor(session, "Wallbox Name", "wallbox_name", lambda d: d["name"]),
        WallboxSensor(session, "Wallbox Standort-ID", "wallbox_location", lambda d: d["location"]),
        VollladenStatusSensor(),
        
    ])

    async_add_entities(sensors, update_before_add=True)


class EnergieImpulsSensor(Entity):
    def __init__(self, session, key):
        self._session = session
        self._key = key
        self._attr_name = SENSOR_TYPES[key]['name']
        self._attr_unique_id = f"energie_impuls_{key}"
        self._attr_unit_of_measurement = SENSOR_TYPES[key].get("unit")
        self._attr_icon = SENSOR_TYPES[key].get("icon")
        self._state = None

    def update(self):
        try:
            data = self._session.get_data()
            self._state = data["flow"].get(self._key) or data["state"].get(self._key)
        except Exception as e:
            _LOGGER.error(f"Sensorfehler ({self._key}): {e}")
            self._state = None

    @property
    def state(self):
        return self._state


    @property
    def device_info(self):
         return {
            "identifiers": {(DOMAIN,"Myid")},
            "name": "Energie Impuls",
            "manufacturer": "Planville",
            "model": "Energie Impuls",
            "configuration_url": "https://energie-impuls.site",
        }
class WallboxSensor(Entity):
    def __init__(self, session, name, unique_id, extract_func, unit=None, icon=None):
        self._session = session
        self._extract_func = extract_func
        self._attr_name = name
        self._attr_unique_id = f"energie_impuls_{unique_id}"
        self._attr_unit_of_measurement = unit
        self._attr_icon = icon
        
        self._state = None

    def update(self):
        try:
            data = self._session.get_wallbox_data()
            self._state = self._extract_func(data)
        except Exception as e:
            _LOGGER.error(f"Fehler beim Abrufen von {self._attr_unique_id}: {e}")
            self._state = None

    @property
    def state(self):
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
        
class VollladenStatusSensor(RestoreEntity, Entity):
    def __init__(self):
        self._attr_name = "Vollladen über Nacht jetzt aktiv"
        self._attr_unique_id = "vollladen_status_sensor"
        self._state = False
        self.entity_id = "binary_sensor.vollladen_uber_nacht_status"
        self._icon = "mdi:weather-night"

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        old_state = await self.async_get_last_state()
        self._state = old_state and old_state.state == "on"

    @property
    def is_on(self):
        return self._state

    @property
    def state(self):
        return "on" if self._state else "off"

    @property
    def device_class(self):
        return "running"

    async def async_turn_on(self):
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self):
        self._state = False
        self.async_write_ha_state()
