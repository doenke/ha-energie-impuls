from datetime import datetime, timedelta
from typing import Optional
from .const import DOMAIN, CONF_AUTO_SWITCH_ENTITY, CONF_MODE_ENTITY
from .const import SCHNELLLADEN, SCHNELLLADEN_JSON, UEBERSCHUSS, UEBERSCHUSS_JSON, HYBRID, HYBRID_JSON, NICHTLADEN, NICHTLADEN_JSON, ERROR 
from .const import AM_SCHNELLLADEN, AM_UEBERSCHUSS, AM_HYBRIDAUTOMATIK, AM_UEBERSCHUSS_NACHT, AM_HYBRIDAUTOMATIK_NACHT, AM_MANUAL

import logging
_LOGGER = logging.getLogger(__name__)


class AutomatikController:
     def __init__(self, hass, wallbox_coordinator, energy_coordinator):
        self.hass = hass
        self.wallbox_coordinator = wallbox_coordinator
        self.energy_coordinator = energy_coordinator

        self.activeMode = None
        self.oldMode = None
          
        self.automations = []
        self.automations.append(HybridAutomatikController(hass,wallbox_coordinator,energy_coordinator))

     async def async_disconnected(self):
          self.hass.data[DOMAIN][CONF_AUTO_SWITCH_ENTITY].async_turn_on()
     
     async def async_update(self, now: Optional[datetime] = None):
        self.activeMode = self.hass.data[DOMAIN][CONF_MODE_ENTITY].current_option
        for auto in self.automations:
             if self.activeMode != auto.mode and self.oldMode == auto.mode:
                  # dieser Modus ist der alte, welcher abgewählt wurde
                  await auto.async_getValues()
                  await auto.async_finish()

        for auto in self.automations:
             if self.activeMode == auto.mode and self.oldMode != auto.mode:
                  # dieser Modus ist der Neue, welcher gerade gewählt wurde
                  await auto.async_getValues()
                  await auto.async_start()
        
        for auto in self.automations:
             
             if self.activeMode == auto.mode and self.oldMode == auto.mode:
                  # dieser Modus ist nach wie vor der gewählte
                  await auto.async_getValues()
                  await auto.async_worker()
             else:
                  await auto.async_maintenance()  
             
        self.oldMode = self.activeMode

class AutomatikBase:     
     def __init__(self, hass, wallbox_coordinator, energy_coordinator):
        self.hass = hass
        self.wallbox_coordinator = wallbox_coordinator
        self.energy_coordinator = energy_coordinator
        self.mode_entity = hass.data[DOMAIN][CONF_MODE_ENTITY]  # WallboxModeSelect-Entity
        self.auto_switch = hass.data[DOMAIN][CONF_AUTO_SWITCH_ENTITY]  # AutomaticModeActiveSwitch-Entity

        self.mode = AM_MANUAL
        self.isActive = False

     async def async_activate(self):
          pass
          
     async def async_start(self):
          self.isActive = True
          await self.async_activate()

     async def async_deactivate(self):
          pass
          
     async def async_finish(self):
          self.isActive = False
          await self.async_deactivate()

     async def async_maintenance(self):
          pass
          
     async def async_getValues(self):
          pass
     
     async def async_justActivated(self):
          pass

     async def async_worker(self):
          pass
          
     
     @property
     def isAutoEnabled(self):
          return self.auto_switch.is_on
     
     @property
     def isCurrentOption(self):
          return self.mode_entity.current_option == self.mode

     async def _set_mode(self, mode_name):
        payloads = {
            HYBRID: HYBRID_JSON,
            NICHTLADEN: NICHTLADEN_JSON
        }
        payload = payloads.get(mode_name)
        if not payload:
            return

        try:
            await self.wallbox_coordinator.async_set_wallbox_mode(payload)
            self.mode_entity.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"[HybridAutomatikController] Fehler beim Setzen des Modus {mode_name}: {e}")


class HybridAutomatikController(AutomatikBase):
    def __init__(self, hass, wallbox_coordinator, energy_coordinator):
        super().__init__(hass, wallbox_coordinator, energy_coordinator)

        self.mode = AM_HYBRIDAUTOMATIK
         
        self.MIN_HYBRID = 1.5
        self.MIN_HYBRID_MINUTES = 10

        self.last_above = None
        self.last_below = None
        self.last_check = None
        self.pv=0

    async def async_getValues(self):
        try:
            self.pv = float(self.energy_coordinator.data["flow"].get("pv", 0))
        except Exception:
            self.pv=0
 
     
    async def async_worker(self):
        now = datetime.now()

        # Bei PV > MIN_HYBRID
        if self.pv >= self.MIN_HYBRID:
            self.last_above = now
            if self.isActive is False and self.last_below:
                if (now - self.last_below) >= timedelta(minutes=self.MIN_HYBRID_MINUTES):
                    await self._set_mode(HYBRID)
        else:
            self.last_below = now
            if self.isActive is True and self.last_above:
                if (now - self.last_above) >= timedelta(minutes=self.MIN_HYBRID_MINUTES):
                    await self._set_mode(NICHTLADEN)

        self.last_check = now

    async def async_activate(self):
        if self.pv >= self.MIN_HYBRID:
            await self._set_mode(HYBRID)
        else:
            await self._set_mode(NICHTLADEN)

    
