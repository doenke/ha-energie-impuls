from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
from .const import PAYLOADS
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class EnergieImpulsCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session):
        super().__init__(
            hass,
            _LOGGER,
            name="energie_impuls_data",
            update_interval=timedelta(seconds=15),
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

    async def async_set_mode(self, mode_name):
        try:
            await self.async_set_wallbox_mode(PAYLOADS.get(mode_name))
            _LOGGER.info(f"Wallbox-Modus gesetzt auf: {mode_name}")
        except Exception as e:
            _LOGGER.error(f"Fehler beim Setzen des Modus {mode_name}: {e}")

    async def async_set_wallbox_mode(self, payload: dict):
            """Setze den Wallbox-Modus und aktualisiere die Koordinatordaten."""
            try:
                updated_setpoint = await self.session.async_put_wallbox_setpoint(payload)
                if not isinstance(updated_setpoint, dict):
                    raise ValueError("Erwartete Antwort ist ein Dict mit Wallbox-Setpoint")

                # Füge die neuen Setpoint-Daten ein:
                if "_set_point" not in self.data:
                    self.data["_set_point"] = {}
                
                self.data["_set_point"].update(updated_setpoint)
                self.async_set_updated_data(self.data)  # Triggert Entities zur Aktualisierung
            except Exception as e:
                _LOGGER.error(f"Fehler beim Setzen des Wallbox-Modus: {e}")
                raise
