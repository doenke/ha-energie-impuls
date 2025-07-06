
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .automation_nightfull import VollladenAutomatik
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch", "number"])
    hass.data[DOMAIN]["automatik"] = VollladenAutomatik(hass)
    await hass.data[DOMAIN]["automatik"].async_initialize()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
