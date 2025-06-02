from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
import requests
import logging
from .const import DOMAIN, LOGIN_URL, DATA_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    session = EnergyImpulsSession(username, password)
    sensor = EnergieImpulsFlowSensor(session)
    async_add_entities([sensor], update_before_add=True)

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
            self.token = response.json().get("token")
        else:
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
        else:
            raise Exception(f"Fehler: {response.status_code}")

class EnergieImpulsFlowSensor(Entity):
    def __init__(self, session: EnergyImpulsSession):
        self._session = session
        self._state = None
        self._attr_name = "Energie Impuls Flow"
        self._attr_unit_of_measurement = "l/min"

    def update(self):
        try:
            data = self._session.get_data()
            self._state = data["data"][0]["flow"]
        except Exception as e:
            _LOGGER.error(f"Fehler beim Abrufen der Daten: {e}")
            self._state = None

    @property
    def state(self):
        return self._state
