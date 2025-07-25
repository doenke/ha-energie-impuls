from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfPower,
)
from .const import DOMAIN
from .api import EnergyImpulsSession
from .devices import EnergieImpulsWallboxDeviceInfoMixin, EnergieImpulsDeviceInfoMixin
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    energie_coordinator = hass.data[DOMAIN]["coordinator_energie"]
    wallbox_coordinator = hass.data[DOMAIN]["coordinator_wallbox"]
    sensors = [
        EnergieImpulsSensor(hass, energie_coordinator,"PV-Erzeugung", "pv", UnitOfPower.KILO_WATT,"mdi:solar-power-variant",SensorDeviceClass.POWER), 
        EnergieImpulsSensor(hass, energie_coordinator,"Netzeinspeisung", "to_grid", UnitOfPower.KILO_WATT,"mdi:transmission-tower",SensorDeviceClass.POWER), 
        EnergieImpulsSensor(hass, energie_coordinator,"Batterie-Ladung", "to_battery", UnitOfPower.KILO_WATT,"mdi:battery-charging",SensorDeviceClass.POWER), 
        EnergieImpulsSensor(hass, energie_coordinator,"Haushalt", "household", UnitOfPower.KILO_WATT,"mdi:home",SensorDeviceClass.POWER), 
        EnergieImpulsSensor(hass, energie_coordinator,"Batterie Ladezustand", "battery_soc", "%","mdi:battery-charging",SensorDeviceClass.BATTERY), 
        WallboxSensor(hass, wallbox_coordinator, "Wallbox Modus", "wallbox_mode_str", lambda d: d["_state"]["mode_str"], None, "mdi:ev-plug-type2",SensorDeviceClass.ENUM),
        WallboxSensor(hass, wallbox_coordinator, "Wallbox Moduscode", "wallbox_mode", lambda d: d["_state"]["mode"],SensorDeviceClass.ENUM),
        WallboxSensor(hass, wallbox_coordinator, "Wallbox Verbrauch", "wallbox_consumption", lambda d: d["_state"]["consumption"], UnitOfPower.KILO_WATT, "mdi:ev-station",SensorDeviceClass.POWER),
        #WallboxSensor(hass, wallbox_coordinator, "Wallbox Zeitstempel", "wallbox_timestamp", lambda d: d["_state"]["timestamp"]),
        #WallboxSensor(hass, wallbox_coordinator, "Wallbox Seit Modus aktiv", "wallbox_mode_since", lambda d: d["_state"]["mode_since"]),
        #WallboxSensor(hass, wallbox_coordinator, "Wallbox Standort-ID", "wallbox_location", lambda d: d["location"]),
        ShortWallboxModeSensor(hass, wallbox_coordinator, "KNX Wallbox Modus", "wallbox_mode_knx", lambda d: d["_state"]["mode_str"], None, "mdi:cog-outline",SensorDeviceClass.ENUM),
    ]

    async_add_entities(sensors, update_before_add=True)


class EnergieImpulsSensor(EnergieImpulsDeviceInfoMixin,CoordinatorEntity,SensorEntity):
    def __init__(self, hass, coordinator, name, key, unit,icon,device_class):
        super().__init__(coordinator)
        self.hass = hass
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"energie_impuls_{key}"
        self._attr_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._state = None

    @property
    def native_value(self):
        data = self.coordinator.data
        if data is None:
            return None
        value = data.get("flow", {}).get(self._key) or data.get("state", {}).get(self._key) 

        try:
            return 0 if value is None else float(value)
        except Exception as e:
            return 0 if value is None else value


class WallboxSensor(EnergieImpulsWallboxDeviceInfoMixin,CoordinatorEntity,SensorEntity):
    def __init__(self, hass, coordinator, name, unique_id, extract_func, unit=None, icon=None,device_class=None):
        super().__init__(coordinator)
        self.hass = hass
       
        self._extract_func = extract_func
        self._attr_name = name
        self._attr_unique_id = f"energie_impuls_{unique_id}"
        self._attr_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT
        if key == "wallbox_mode":
            _attr_entity_registry_visible_default = False
        
        self._state = None

    @property
    def native_value(self):
        self._state = self._extract_func(self.coordinator.data)
        
        if self.device_class == SensorDeviceClass.POWER:
            try:
                return 0 if self._state is None else float(self._state)
            except Exception as e:
                return 0 if self._state is None else self._state
        else:
            return 0 if self._state is None else self._state

class ShortWallboxModeSensor(WallboxSensor):
    @property
    def native_value(self):
        value = self._extract_func(self.coordinator.data)
        if isinstance(value, str):
            value = value.replace("Fahrzeug", "").strip()
        self._state = value
        return "" if self._state is None else self._state
