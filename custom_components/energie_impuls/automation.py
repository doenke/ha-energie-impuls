from datetime import datetime, timedelta
from .const import DOMAIN, SCHNELLLADEN, SCHNELLLADEN_JSON, UEBERSCHUSS, UEBERSCHUSS_JSON, HYBRID, HYBRID_JSON, NICHTLADEN, NICHTLADEN_JSON, ERROR 
from .const import AM_SCHNELLLADEN, AM_UEBERSCHUSS, AM_HYBRIDAUTOMATIK, AM_UEBERSCHUSS_NACHT, AM_HYBRIDAUTOMATIK_NACHT, AM_MANUAL

class HybridAutomatikController:
    def __init__(self, hass, wallbox_coordinator, energy_coordinator, mode_entity, auto_switch):
        self.hass = hass
        self.wallbox_coordinator = wallbox_coordinator
        self.energy_coordinator = energy_coordinator
        self.mode_entity = mode_entity  # WallboxModeSelect-Entity
        self.auto_switch = auto_switch  # AutomaticModeActiveSwitch-Entity

        self.MIN_HYBRID = 1.5
        self.MIN_HYBRID_MINUTES = 10

        self.last_above = None
        self.last_below = None
        self.last_check = None
        self.currently_in_hybrid = None

    async def async_update(self):
        # Nur wenn Automatik aktiv und Hybridautomatik ausgewählt
        if not self.auto_switch.is_on or self.mode_entity.current_option != "Hybridautomatik":
            return

        now = datetime.now()
        pv = 0

        try:
            pv = float(self.energy_coordinator.data["flow"].get("pv", 0))
        except Exception:
            return

        # Bei erstmaligem Aufruf direkt entscheiden
        if not self.last_check:
            await self._apply_initial_state(pv)
            self.last_check = now
            return

        # Bei PV > MIN_HYBRID
        if pv >= self.MIN_HYBRID:
            self.last_above = now
            if self.currently_in_hybrid is False and self.last_below:
                if (now - self.last_below) >= timedelta(minutes=self.MIN_HYBRID_MINUTES):
                    await self._set_mode("Hybridladen")
        else:
            self.last_below = now
            if self.currently_in_hybrid is True and self.last_above:
                if (now - self.last_above) >= timedelta(minutes=self.MIN_HYBRID_MINUTES):
                    await self._set_mode("nicht laden")

        self.last_check = now

    async def _apply_initial_state(self, pv):
        if pv >= self.MIN_HYBRID:
            await self._set_mode("Hybridladen")
        else:
            await self._set_mode("nicht laden")

    async def _set_mode(self, mode_name):
        payloads = {
            "Hybridladen": {
                "locked": False,
                "surplus_charging": True,
                "hybrid_charging_current": 6
            },
            "nicht laden": {
                "locked": True
            }
        }
        payload = payloads.get(mode_name)
        if not payload:
            return

        try:
            await self.wallbox_coordinator.async_set_wallbox_mode(payload)
            self.mode_entity._attr_current_option = mode_name
            self.mode_entity.async_write_ha_state()
            self.currently_in_hybrid = mode_name == "Hybridladen"
        except Exception as e:
            _LOGGER.error(f"[HybridAutomatikController] Fehler beim Setzen des Modus {mode_name}: {e}")
