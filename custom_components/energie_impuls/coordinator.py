from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class EnergieImpulsCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session):
        super().__init__(
            hass,
            _LOGGER,
            name="energie_impuls_data",
            update_interval=timedelta(seconds=30),
        )
        self.session = session

    async def _async_update_data(self):
        try:
            return await self.session.async_get_data()
        except Exception as err:
            raise UpdateFailed(f"Fehler beim Abrufen der Energiedaten: {err}") from err

class WallboxCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session):
        super().__init__(
            hass,
            _LOGGER,
            name="energie_impuls_wallbox",
            update_interval=timedelta(seconds=15),
        )
        self.session = session

    async def _async_update_data(self):
        try:
            return await self.session.async_get_wallbox_data()
        except Exception as err:
            raise UpdateFailed(f"Fehler beim Abrufen der Wallbox-Daten: {err}") from err
