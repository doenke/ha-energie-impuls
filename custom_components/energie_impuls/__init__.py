
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .automation_nightfull import VollladenAutomatik
from .const import DOMAIN, WALLBOX_NAME, WALLBOX_ID

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    
    session = EnergyImpulsSession(entry.data["username"], entry.data["password"])

    try:
        wallbox_data = session.get_wallbox_data()
        device_name = wallbox_data.get("name", WALLBOX_NAME)
        device_id = str(wallbox_data.get("id", "wallbox"))
    except Exception as e:
        _LOGGER.warning(f"Konnte Wallbox-Daten nicht abrufen: {e}")
        wb_device_name = WALLBOX_NAME
        wb_device_id = WALLBOX_ID

    hass.data[DOMAIN]["wb_device_name"] = wb_device_name
    hass.data[DOMAIN]["wb_device_id"] = wb_device_id
    hass.data[DOMAIN]["session"] = session
    
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch", "number", "select"])

    hass.data[DOMAIN]["automatik"] = VollladenAutomatik(hass)
    await hass.data[DOMAIN]["automatik"].async_initialize()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
