from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.event import async_track_state_change_event
from datetime import timedelta

from .automation import AutomatikController
from .api import EnergyImpulsSession
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_WB_DEVICE_NAME, CONF_WB_DEVICE_ID, CONF_MODE_ENTITY, CONF_AUTO_SWITCH_ENTITY, CONF_AUTO_MIN_PV, DEFAULT_AUTO_MIN_PV, DEFAULT_AUTO_MINUTES, CONF_AUTO_MINUTES 

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
    automatik_controller = AutomatikController(hass,entry)
    hass.data[DOMAIN]["automatik_controller"] = automatik_controller
    
    async_track_time_interval(hass, hass.data[DOMAIN]["automatik_controller"].async_update, timedelta(minutes=1))
    
    #async def _handle_state_change(entity_id, old_state, new_state):
    #    await automatik_controller.async_update()

    async def _handle_state_change(event):
#        entity_id = event.data.get("entity_id")
#        old_state = event.data.get("old_state")
#        new_state = event.data.get("new_state")
        await automatik_controller.async_update()
    
    # Das Auto wird abgeklemmt. Die Automatik kann sich wieder einschalten/zurücksetzen
    #async def handle_mode_change(entity_id, old_state, new_state):
    #    if old_state and new_state:
    #        if old_state != "2" and new_state == "2":
    #            await hass.data[DOMAIN]["automatik_controller"].async_reset()

    async def handle_mode_change(event):
        if event.data.get("old_state") and event.data.get("new_state"):
            if event.data.get("old_state") != "2" and event.data.get("new_state") == "2":
                await hass.data[DOMAIN]["automatik_controller"].async_reset()
    
    # Entitäten, die beobachtet werden sollen
    mode_entity_id = hass.data[DOMAIN][CONF_MODE_ENTITY].entity_id
    auto_entity_id = hass.data[DOMAIN][CONF_AUTO_SWITCH_ENTITY].entity_id

    # Registrieren
    async_track_state_change_event(hass, [mode_entity_id, auto_entity_id], _handle_state_change)
    async_track_state_change_event(hass,"sensor.wallbox_mode_code", handle_mode_change)

    
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
