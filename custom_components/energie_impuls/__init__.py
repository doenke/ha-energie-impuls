
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .automation_nightfull import VollladenAutomatik
from .sensor import EnergyImpulsSession
from .const import DOMAIN, DEFAULT_WALLBOX_NAME, DEFAULT_WALLBOX_ID, CONF_USERNAME, CONF_PASSWORD, CONF_WB_DEVICE_NAME, CONF_WB_DEVICE_ID

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}


    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    session = EnergyImpulsSession(hass, username, password)

    try:
        wallbox_data = session.get_wallbox_data()
        device_name = wallbox_data.get("name", WALLBOX_NAME)
        device_id = str(wallbox_data.get("id", "wallbox"))
    except Exception as e:
        wb_device_name = DEFAULT_WALLBOX_NAME
        wb_device_id = DEFAULT_WALLBOX_ID

    hass.data[DOMAIN][CONF_WB_DEVICE_NAME] = wb_device_name
    hass.data[DOMAIN][CONF_WB_DEVICE_ID] = wb_device_id
    hass.data[DOMAIN]["session"] = session
    
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch", "number", "select"])

    hass.data[DOMAIN]["automatik"] = VollladenAutomatik(hass)
    await hass.data[DOMAIN]["automatik"].async_initialize()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
