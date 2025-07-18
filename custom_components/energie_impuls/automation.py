from datetime import datetime, timedelta
from typing import Optional
from .const import DOMAIN, CONF_AUTO_SWITCH_ENTITY, CONF_MODE_ENTITY, CONF_AUTO_MINUTES, CONF_AUTO_MIN_PV, DEFAULT_AUTO_MINUTES, DEFAULT_AUTO_MIN_PV
from .const import SCHNELLLADEN, SCHNELLLADEN_JSON, UEBERSCHUSS, UEBERSCHUSS_JSON, HYBRID, HYBRID_JSON, NICHTLADEN, NICHTLADEN_JSON, ERROR 
from .const import AM_SCHNELLLADEN, AM_UEBERSCHUSS, AM_HYBRIDAUTOMATIK, AM_UEBERSCHUSS_NACHT, AM_HYBRIDAUTOMATIK_NACHT, AM_MANUAL

import logging
_LOGGER = logging.getLogger(__name__)


class AutomatikController:
     def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.wallbox_coordinator = self.hass.data[DOMAIN]["coordinator_wallbox"]
        self.energy_coordinator =  self.hass.data[DOMAIN]["coordinator_energie"]

        self.activeMode = None
        self.oldMode = None
          
        self.automations = [
              AutomatikControllerPVGrenze(hass, entry, AM_HYBRIDAUTOMATIK, UEBERSCHUSS, HYBRID),
              SchnellladenAutomatikController(hass, entry, AM_SCHNELLLADEN),
              UeberschussAutomatikController(hass, entry, AM_UEBERSCHUSS),
              AutomatikControllerPVGrenze(hass, entry, AM_HYBRIDAUTOMATIK_NACHT, SCHNELLLADEN, HYBRID),
              AutomatikControllerPVGrenze(hass, entry, AM_UEBERSCHUSS_NACHT, SCHNELLLADEN, UEBERSCHUSS),
        ]

   
     
     async def async_reset(self):
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
     def __init__(self, hass, entry, mode):
        self.mode = mode
        self.hass = hass
        self.entry = entry  
        self.wallbox_coordinator = self.hass.data[DOMAIN]["coordinator_wallbox"]
        self.energy_coordinator =  self.hass.data[DOMAIN]["coordinator_energie"]
        self.mode_entity = hass.data[DOMAIN][CONF_MODE_ENTITY]  # WallboxModeSelect-Entity
        self.auto_switch = hass.data[DOMAIN][CONF_AUTO_SWITCH_ENTITY]  # AutomaticModeActiveSwitch-Entity

        self.isActive = False

        self.last_above = None
        self.last_below = None
        self.last_check = None


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
            NICHTLADEN: NICHTLADEN_JSON,
            SCHNELLLADEN: SCHNELLLADEN_JSON,
            UEBERSCHUSS: UEBERSCHUSS_JSON
        }
        payload = payloads.get(mode_name)
        if not payload:
            return

        try:
            await self.wallbox_coordinator.async_set_wallbox_mode(payload)
            self.mode_entity.async_write_ha_state()
            _LOGGER.info(f"[{self.mode}] Wallbox-Modus gesetzt auf: {mode_name}")
        except Exception as e:
            _LOGGER.error(f"[HybridAutomatikController] Fehler beim Setzen des Modus {mode_name}: {e}")

class AutomatikControllerPVGrenze(AutomatikBase):
    def __init__(self, hass, entry, mode, offaction, onaction):
         super().__init__(hass, mode, entry)
         self.offaction = offaction
         self.onaction = onaction 
     
    async def async_worker(self):
        now = datetime.now()
        try:
            self.pv = float(self.energy_coordinator.data["flow"].get("pv", 0))
        except Exception:
            self.pv=0

        # Bei PV > MIN_HYBRID
        if self.pv >= self.entry.options.get(CONF_AUTO_MIN_PV, DEFAULT_AUTO_MIN_PV):
            self.last_above = now
            if self.isActive is False and self.last_below:
                if (now - self.last_below) >= timedelta(minutes=self.entry.options.get(CONF_AUTO_MINUTES, DEFAULT_AUTO_MINUTES)):
                    await self._set_mode(self.onaction)
        else:
            self.last_below = now
            if self.isActive is True and self.last_above:
                if (now - self.last_above) >= timedelta(minutes=self.entry.options.get(CONF_AUTO_MINUTES, DEFAULT_AUTO_MINUTES)):
                    await self._set_mode(self.offaction)

        self.last_check = now
     
    async def async_activate(self):
        try:
            self.pv = float(self.energy_coordinator.data["flow"].get("pv", 0))
        except Exception:
            self.pv=0
        if self.pv >= self.entry.options.get(CONF_AUTO_MIN_PV, DEFAULT_AUTO_MIN_PV):
            await self._set_mode(self.onaction)
        else:
            await self._set_mode(self.offaction)

class SchnellladenAutomatikController(AutomatikBase):     
    async def async_activate(self):
       await self._set_mode(SCHNELLLADEN)

class UeberschussAutomatikController(AutomatikBase):
    async def async_activate(self):
       await self._set_mode(UEBERSCHUSS)



