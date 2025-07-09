import aiohttp
import async_timeout
import logging
from .const import LOGIN_URL, DATA_URL, WALLBOX_URL, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

class EnergyImpulsSession:
    def __init__(self, hass):
        self.hass = hass
        self.username = entry.data[CONF_USERNAME]
        self.password = entry.data[CONF_PASSWORD]
        self.token = None

    async def async_get_token(self):
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.post(LOGIN_URL, json={
                        "username": self.username,
                        "password": self.password
                    }) as response:
                        if response.status in (200, 201, 204):
                            json_data = await response.json()
                            self.token = json_data.get("access")
                            if self.token:
                                _LOGGER.debug("Neuer Token erhalten.")
                                return self.token
                            else:
                                raise Exception(f"Antwort ohne Token: {json_data}")
                        else:
                            raise Exception(f"Login fehlgeschlagen ({response.status})")
        except Exception as e:
            raise Exception(f"Fehler bei Tokenabfrage: {e}")

    async def async_get_data(self):
        if not self.token:
            await self.async_get_token()
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(DATA_URL, headers=headers) as response:
                    if response.status == 401:
                        await self.async_get_token()
                        headers = {"Authorization": f"Bearer {self.token}"}
                        async with session.get(DATA_URL, headers=headers) as retry_response:
                            return await retry_response.json()
                    elif response.status in (200, 201, 204):
                        return await response.json()
                    else:
                        raise Exception(f"Fehler bei Datenabruf: {response.status}")
        except Exception as e:
            raise Exception(f"Fehler bei Datenabruf: {e}")

    async def async_get_wallbox_data(self):
        if not self.token:
            await self.async_get_token()
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(WALLBOX_URL, headers=headers) as response:
                    if response.status == 401:
                        await self.async_get_token()
                        headers = {"Authorization": f"Bearer {self.token}"}
                        async with session.get(WALLBOX_URL, headers=headers) as retry_response:
                            json_data = await retry_response.json()
                    elif response.status in (200, 201, 204):
                        json_data = await response.json()
                    else:
                        raise Exception(f"Wallbox-Fehler: {response.status}")

            if isinstance(json_data, list) and json_data:
                return json_data[0]
            else:
                raise Exception("Wallbox-Antwort leer oder ungültig")

        except Exception as e:
            raise Exception(f"Fehler bei Wallboxdaten: {e}")
