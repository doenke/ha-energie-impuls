
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .const import LOGIN_URL, DATA_URL, WALLBOX_URL
import requests
import logging

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "pv": {"name": "PV-Erzeugung", "unit": "kW"},
    "to_grid": {"name": "Netzeinspeisung", "unit": "kW"},
    "to_battery": {"name": "Batterie-Ladung", "unit": "kW"},
    "wallbox": {"name": "Wallbox", "unit": "kW"},
    "household": {"name": "Haushalt", "unit": "kW"},
    "battery_soc": {"name": "Batterie Ladezustand", "unit": "%"},
}

async def async_setup_entry(hass, entry, async_add_entities):
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    session = EnergyImpulsSession(username, password)
    sensors = [EnergieImpulsSensor(session, key) for key in SENSOR_TYPES]
    async_add_entities(sensors, update_before_add=True)
    sensors.extend([
        WallboxSensorBase(session, "Wallbox Modus", "wallbox_mode_str", lambda d: d["_state"]["mode_str"]),
        WallboxSensorBase(session, "Wallbox Moduscode", "wallbox_mode", lambda d: d["_state"]["mode"]),
        WallboxSensorBase(session, "Wallbox Verbrauch", "wallbox_consumption", lambda d: d["_state"]["consumption"], "kW"),
        WallboxSensorBase(session, "Wallbox Zeitstempel", "wallbox_timestamp", lambda d: d["_state"]["timestamp"]),
        WallboxSensorBase(session, "Wallbox Seit Modus aktiv", "wallbox_mode_since", lambda d: d["_state"]["mode_since"]),
        # WallboxSensorBase(session, "Wallbox Hybridstrom", "wallbox_hybrid_charging", lambda d: d["_set_point"]["hybrid_charging_current"], "A"),
        WallboxSensorBase(session, "Wallbox Name", "wallbox_name", lambda d: d["name"]),
        WallboxSensorBase(session, "Wallbox Standort-ID", "wallbox_location", lambda d: d["location"]),
    ])

class EnergyImpulsSession:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None

    def get_token(self):
        response = requests.post(LOGIN_URL, json={
        "username": self.username,
        "password": self.password
        })

        if response.status_code == 200:
            json_data = response.json()
            self.token = json_data.get("access")
            if self.token:
                _LOGGER.info(f"Neuer Token erhalten: {self.token}")
            else:
                _LOGGER.error(f"Antwort ohne Token: {json_data}")
        else:
            _LOGGER.error(f"Login fehlgeschlagen ({response.status_code}): {response.text}")
            raise Exception("Login fehlgeschlagen")
        
    def get_data(self):
        if not self.token:
            self.get_token()
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(DATA_URL, headers=headers)
        if response.status_code == 401:
            self.get_token()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(DATA_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        raise Exception("Fehler bei API-Antwort")

    def get_wallbox_data(self):
        if not self.token:
            self.get_token()

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(WALLBOX_URL, headers=headers)

        if response.status_code == 401:
            self.get_token()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(WALLBOX_URL, headers=headers)

        if response.status_code == 200:
            try:
                json_data = response.json()
                if isinstance(json_data, list) and json_data:
                    return json_data[0]
                else:
                    raise Exception("Wallbox-Antwort war leer oder kein Array.")
            except Exception as e:
                raise Exception(f"Fehler beim Parsen der Wallbox-Antwort: {e}")
        else:
            raise Exception(f"Wallbox-API Fehler: {response.status_code} → {response.text}")


class EnergieImpulsSensor(Entity):
    def __init__(self, session, key):
        self._session = session
        self._key = key
        self._state = None
        self._attr_name = f"Energie Impuls {SENSOR_TYPES[key]['name']}"
        self._attr_unit_of_measurement = SENSOR_TYPES[key]['unit']
        self._attr_unique_id = f"energie_impuls_{key}"

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

class WallboxSensorBase(Entity):
    def __init__(self, session, name, unique_id, extract_func, unit=None):
        self._session = session
        self._name = name
        self._unique_id = unique_id
        self._extract_func = extract_func
        self._unit = unit
        self._state = None

    def update(self):
        try:
            data = self._session.get_wallbox_data()
            self._state = self._extract_func(data)
        except Exception as e:
            _LOGGER.error(f"Fehler beim Abrufen von {self._unique_id}: {e}")
            self._state = None

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def state(self):
        return self._state




