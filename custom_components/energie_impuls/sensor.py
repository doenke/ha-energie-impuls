from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .api import EnergyImpulsSession
from .devices import EnergieImpulsWallboxDeviceInfoMixin, EnergieImpulsDeviceInfoMixin
import logging

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "pv": {"name": "PV-Erzeugung", "unit": "kW", "icon": "mdi:solar-power-variant","device_class": "power"},
    "to_grid": {"name": "Netzeinspeisung", "unit": "kW", "icon": "mdi:transmission-tower","device_class": "power"},
    "to_battery": {"name": "Batterie-Ladung", "unit": "kW", "icon": "mdi:battery-charging","device_class": "power"},
    "household": {"name": "Haushalt", "unit": "kW", "icon": "mdi:home","device_class": "power"},
    "battery_soc": {"name": "Batterie Ladezustand", "unit": "%", "icon": "mdi:battery-charging","device_class": None}
}

async def async_setup_entry(hass, entry, async_add_entities):
    energie_coordinator = hass.data[DOMAIN]["coordinator_energie"]
    wallbox_coordinator = hass.data[DOMAIN]["coordinator_wallbox"]
    sensors = [EnergieImpulsSensor(hass, energie_coordinator, key) for key in SENSOR_TYPES]

    sensors.extend([
        WallboxSensor(hass, wallbox_coordinator, "Wallbox Modus", "wallbox_mode_str", lambda d: d["_state"]["mode_str"], None, "mdi:ev-plug-type2"),
        WallboxSensor(hass, wallbox_coordinator, "Wallbox Moduscode", "wallbox_mode", lambda d: d["_state"]["mode"]),
        WallboxSensor(hass, wallbox_coordinator, "Wallbox Verbrauch", "wallbox_consumption", lambda d: d["_state"]["consumption"], "kW", "mdi:ev-station"),
        #WallboxSensor(hass, wallbox_coordinator, "Wallbox Zeitstempel", "wallbox_timestamp", lambda d: d["_state"]["timestamp"]),
        #WallboxSensor(hass, wallbox_coordinator, "Wallbox Seit Modus aktiv", "wallbox_mode_since", lambda d: d["_state"]["mode_since"]),
        #WallboxSensor(hass, wallbox_coordinator, "Wallbox Standort-ID", "wallbox_location", lambda d: d["location"]),
        ShortWallboxModeSensor(hass, wallbox_coordinator, "KNX Wallbox Modus", "wallbox_mode_knx", lambda d: d["_state"]["mode_str"], None, "mdi:cog-outline"),
    ])

    async_add_entities(sensors, update_before_add=True)


class EnergieImpulsSensor(EnergieImpulsDeviceInfoMixin,CoordinatorEntity,SensorEntity):
    def __init__(self, hass, coordinator, key):
        self.hass = hass
        super().__init__(coordinator)
        self._key = key
        self._attr_name = SENSOR_TYPES[key]['name']
        self._attr_unique_id = f"energie_impuls_{key}"
        self._attr_unit_of_measurement = SENSOR_TYPES[key].get("unit")
        self._attr_icon = SENSOR_TYPES[key].get("icon")
        self._attr_device_class = SENSOR_TYPES[key].get("device_class")
        self._state = None

    @property
    def state(self):
        data = self.coordinator.data
        if data is None:
            return None
        value = data.get("flow", {}).get(self._key) or data.get("state", {}).get(self._key) 
        return 0 if value is None else value


class WallboxSensor(EnergieImpulsWallboxDeviceInfoMixin,CoordinatorEntity,SensorEntity):
    def __init__(self, hass, coordinator, name, unique_id, extract_func, unit=None, icon=None):
        super().__init__(coordinator)
        self.hass = hass
       
        self._extract_func = extract_func
        self._attr_name = name
        self._attr_unique_id = f"energie_impuls_{unique_id}"
        self._attr_icon = icon
        self._state = None

    @property
    def state(self):
        self._state = self._extract_func(self.coordinator.data)
        return "" if self._state is None else self._state


class ShortWallboxModeSensor(WallboxSensor):
    @property
    def state(self):
        value = self._extract_func(self.coordinator.data)
        if isinstance(value, str):
            value = value.replace("Fahrzeug", "").strip()
        self._state = value
        return 0 if self._state is None else self._state
