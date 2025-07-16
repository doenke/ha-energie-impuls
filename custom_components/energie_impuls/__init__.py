from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .automation import HybridAutomatikController
from .api import EnergyImpulsSession
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_WB_DEVICE_NAME, CONF_WB_DEVICE_ID

from .coordinator import EnergieImpulsCoordinator, WallboxCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    session = EnergyImpulsSession(hass, username, password)

    hass.data[DOMAIN]["session"] = session

    energie_coordinator = EnergieImpulsCoordinator(hass, session)
    await energie_coordinator.async_config_entry_first_refresh()
    
    wallbox_coordinator = WallboxCoordinator(hass, session)
    await wallbox_coordinator.async_config_entry_first_refresh()


    
    # 🔄 Asynchron Wallbox-Daten abrufen
    try:
        wallbox_data = wallbox_coordinator.data
        wb_device_name = wallbox_data.get("name", "Wallbox")
        wb_device_id = str(wallbox_data.get("id", "wallbox"))
    except Exception as e:
        wb_device_name = "Wallbox"
        wb_device_id = "wallbox"
    
    hass.data[DOMAIN][CONF_WB_DEVICE_NAME] = wb_device_name
    hass.data[DOMAIN][CONF_WB_DEVICE_ID] = wb_device_id

    hass.data[DOMAIN]["coordinator_energie"] = energie_coordinator
    hass.data[DOMAIN]["coordinator_wallbox"] = wallbox_coordinator
    
    # Plattformen laden
    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "switch", "number", "select"]
    )

    # Automatik-Logik initialisieren
    #hass.data[DOMAIN]["automatik"] = Automatik(hass)
    hass.data[DOMAIN]["automatik_controller_hybrid"] = HybridAutomatikController(hass,wallbox_coordinator,energie_coordinator)

    #await hass.data[DOMAIN]["automatik"].async_initialize()
    async_track_time_interval(hass, hass.data[DOMAIN]["automatik_controller_hybrid"].async_update, timedelta(minutes=1))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Optional: session schließen
    if DOMAIN in hass.data and "session" in hass.data[DOMAIN]:
        await hass.data[DOMAIN]["session"].async_close()

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["sensor", "switch", "number", "select"]
    )

    if unload_ok:
        hass.data.pop(DOMAIN, None)

    return unload_ok
