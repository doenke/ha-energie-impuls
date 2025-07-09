import aiohttp
import async_timeout
import logging

from .const import LOGIN_URL, DATA_URL, WALLBOX_URL, WALLBOX_SETPOINT_URL ,DOMAIN, CONF_WB_DEVICE_ID

_LOGGER = logging.getLogger(__name__)

class EnergyImpulsSession:
    def __init__(self, hass, username, password):
        self.hass = hass
        self.username = username
        self.password = password
        self.token = None
        self._client = aiohttp.ClientSession()

    async def async_get_token(self):
        """Fetch a new token from the login endpoint."""
        try:
            async with async_timeout.timeout(10):
                async with self._client.post(LOGIN_URL, json={
                    "username": self.username,
                    "password": self.password
                }) as response:
                    if response.status in (200, 201, 204):
                        json_data = await response.json()
                        self.token = json_data.get("access")
                        if self.token:
                            _LOGGER.debug("Neuer Token erhalten.")
                            return self.token
                        raise Exception(f"Antwort ohne Token: {json_data}")
                    raise Exception(f"Login fehlgeschlagen ({response.status})")
        except Exception as e:
            raise Exception(f"Fehler bei Tokenabfrage: {e}") from e

    async def _authorized_get(self, url):
        """Generic helper for GET requests with token management."""
        if not self.token:
            await self.async_get_token()
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with self._client.get(url, headers=headers) as response:
                if response.status == 401:
                    _LOGGER.warning("Token ungültig – versuche erneute Anmeldung.")
                    await self.async_get_token()
                    headers["Authorization"] = f"Bearer {self.token}"
                    async with self._client.get(url, headers=headers) as retry_response:
                        return await retry_response.json()
                elif response.status in (200, 201, 204):
                    return await response.json()
                raise Exception(f"Fehler bei GET {url}: {response.status}")
        except Exception as e:
            raise Exception(f"Fehler bei GET {url}: {e}") from e

    async def async_get_data(self):
        """Ruft Energiedaten ab (PV, Haushalt, etc.)."""
        return await self._authorized_get(DATA_URL)

    async def async_get_wallbox_data(self):
        """Ruft Wallboxdaten ab."""
        data = await self._authorized_get(WALLBOX_URL)
        if isinstance(data, list) and data:
            return data[0]
        raise Exception("Wallbox-Antwort leer oder ungültig")

    async def async_put_wallbox_setpoint(self, payload: dict):
        """Sendet Steuerbefehle an die Wallbox."""
        if not self.token:
            await self.async_get_token()
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        try:
            async with self._client.put(WALLBOX_SETPOINT_URL+self.hass.data[DOMAIN][CONF_WB_DEVICE_ID], headers=headers, json=payload) as response:
                if response.status not in (200, 201, 204):
                    raise Exception(f"Fehler beim PUT: {response.status} → {await response.text()}")
                return True
        except Exception as e:
            raise Exception(f"Fehler beim PUT an Wallbox: {e}") from e

    async def async_close(self):
        """Beende die HTTP-Session sauber."""
        await self._client.close()
