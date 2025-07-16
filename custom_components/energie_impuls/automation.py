from datetime import datetime, timedelta
from .const import DOMAIN, CONF_AUTO_SWITCH_ENTITY, CONF_MODE_ENTITY
from .const import SCHNELLLADEN, SCHNELLLADEN_JSON, UEBERSCHUSS, UEBERSCHUSS_JSON, HYBRID, HYBRID_JSON, NICHTLADEN, NICHTLADEN_JSON, ERROR 
from .const import AM_SCHNELLLADEN, AM_UEBERSCHUSS, AM_HYBRIDAUTOMATIK, AM_UEBERSCHUSS_NACHT, AM_HYBRIDAUTOMATIK_NACHT, AM_MANUAL

class AutomatikController:
     def __init__(self, hass, wallbox_coordinator, energy_coordinator):
        self.hass = hass
        self.wallbox_coordinator = wallbox_coordinator
        self.energy_coordinator = energy_coordinator

        self.activeMode = None
        self.oldMode = None
          
        self.automations = []
        self.automations.append(HybridAutomatikController(hass,wallbox_coordinator,energie_coordinator))

     async def async_update(self):
        for auto in self.automations:
             if self.activeMode != auto.mode and self.oldMode == auto.mode:
                  # dieser Modus ist der alte, welcher abgewählt wurde
                  auto.finish()

        for auto in self.automations:
             if self.activeMode == auto.mode and self.oldMode != auto.mode:
                  # dieser Modus ist der Neue, welcher gerade gewählt wurde
                  auto.start()

        
        for auto in self.automations:
             if self.activeMode == auto.mode and self.oldMode == auto.mode:
                  # dieser Modus ist nach wie vor der gewählte
                  await auto._async_update()
             auto.maintenance()  

class AutomatikBase:     
     def __init__(self, hass, wallbox_coordinator, energy_coordinator):
        self.hass = hass
        self.wallbox_coordinator = wallbox_coordinator
        self.energy_coordinator = energy_coordinator
        self.mode_entity = hass.data[DOMAIN][CONF_MODE_ENTITY]  # WallboxModeSelect-Entity
        self.auto_switch = hass.data[DOMAIN][CONF_AUTO_SWITCH_ENTITY]  # AutomaticModeActiveSwitch-Entity

        self.mode = AM_MANUAL
        self.isActive = False

     def activate(self)
     def start(self):
          self.isActive = True
          self.activate()

     def deactivate(self):
     def finish(self):
          self.isActive = False
          self.deactivate()

     def maintenance(self)
     
     async def async_getValues(self)
     
     async def async_justActivated(self)
     
     async def async_update(self):

     async def _async_update(self):
          if self.isAutoEnabled and self.isCurrentOption:
               
               await async_getValues()
               
               if (not self.isActive)
                    self._justActivated()
          
               
          self.async_update()
          
     
     @property
     def isAutoEnabled(self):
          return self.auto_switch.is_on
     
     @property
     def isCurrentOption(self):
          return self.mode_entity.current_option == self.mode


class HybridAutomatikController(AutomatikBase):
    def __init__(self, hass, wallbox_coordinator, energy_coordinator):
        super.__init__(hass, wallbox_coordinator, energy_coordinator)

         self.mode = AM_HYBRIDAUTOMATIK
         
        self.MIN_HYBRID = 1.5
        self.MIN_HYBRID_MINUTES = 10

        self.last_above = None
        self.last_below = None
        self.last_check = None
        self.currently_in_hybrid = None
        self.pv=0

    async def async_getValues(self):
        try:
            self.pv = float(self.energy_coordinator.data["flow"].get("pv", 0))
        except Exception:
            self.pv=0
 
     
    async def async_update(self):
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
