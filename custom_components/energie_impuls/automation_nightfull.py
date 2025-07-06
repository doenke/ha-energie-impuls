from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

class VollladenAutomatik:
    def __init__(self, hass):
        self.hass = hass
        self.enabled_entity = "switch.vollladen_uber_nacht"
        self.sensor_pv = "sensor.energie_impuls_pv_erzeugung"
        self.sensor_haus = "sensor.energie_impuls_haushalt"
        self.sensor_verbrauch = "sensor.energie_impuls_wallbox_verbrauch"
        self._active = False
        self._timer = None
        self._saved_states = {}
        self._monitor_zero = False
        self._zero_timer = None
        self._status_sensor: VollladenStatusSensor = None

    async def async_initialize(self):
        self._status_sensor = VollladenStatusSensor()
        self.hass.states.async_set(ACTIVE_STATUS_ENTITY, "off")
        self.hass.async_create_task(
            self.hass.helpers.entity_component.async_add_entities([self._status_sensor], update_before_add=True)
        )
        async_track_state_change_event(self.hass, self.sensor_pv, self._state_change_handler)
        async_track_state_change_event(self.hass, self.sensor_haus, self._state_change_handler)
        async_track_state_change_event(self.hass, self.sensor_verbrauch, self._verbrauch_handler)
        async_track_state_change_event(self.hass, self.enabled_entity, self._on_enabled_toggle)

    async def _state_change_handler(self, event):
        try:
            pv = float(self.hass.states.get(self.sensor_pv).state)
            haushalt = float(self.hass.states.get(self.sensor_haus).state)
        except (ValueError, AttributeError, TypeError):
            return

        differenz = pv - haushalt
        if differenz > 2:
            if not self._active:
                _LOGGER.info("Vollladen: Differenz > 2 → Starte Timer")
                self._active = True
                self._timer = async_track_time_interval(self.hass, self._timer_check, timedelta(minutes=10))
        else:
            self._active = False
            if self._timer:
                self._timer()
                self._timer = None

    async def _timer_check(self, now):
        enabled = self.hass.states.get(self.enabled_entity)
        if enabled and enabled.state == "on":
            _LOGGER.info("Vollladen aktiv: Zustände speichern und starten")

            self._saved_states = {
                "switch.uberschussladen": self.hass.states.get("switch.uberschussladen").state,
                "switch.wallbox_sperre": self.hass.states.get("switch.wallbox_sperre").state,
                "number.hybrid_charging_current": self.hass.states.get("number.hybrid_charging_current").state,
            }

            await self._status_sensor.async_turn_on()
            await self.hass.services.async_call("switch", "turn_off", {
                "entity_id": ["switch.uberschussladen", "switch.wallbox_sperre"]
            })
            await self.hass.services.async_call("number", "set_value", {
                "entity_id": "number.hybrid_charging_current",
                "value": 6
            })

            self._monitor_zero = True

        self._active = False
        if self._timer:
            self._timer()
            self._timer = None

    async def _verbrauch_handler(self, event):
        if not self._monitor_zero:
            return
        try:
            val = float(event.data.get("new_state").state)
        except (ValueError, AttributeError, TypeError):
            return
        if val == 0 and self._status_sensor.is_on:
            if not self._zero_timer:
                _LOGGER.info("Wallbox-Verbrauch = 0 → Starte Rücksetz-Timer")
                self._zero_timer = async_track_time_interval(self.hass, self._reset_due_to_zero, timedelta(minutes=10))
        else:
            if self._zero_timer:
                self._zero_timer()
                self._zero_timer = None

    async def _reset_due_to_zero(self, now):
        _LOGGER.info("10 Minuten 0 W Verbrauch → Rücksetzen")
        if self._status_sensor.is_on:
            await self._restore_saved_states()

    async def _on_enabled_toggle(self, event):
        if event.data.get("old_state").state == "on" and event.data.get("new_state").state == "off":
            _LOGGER.info("Vollladen-Schalter aus → Rücksetzen")
            if self._status_sensor.is_on:
                await self._restore_saved_states()

    async def _restore_saved_states(self):
        for entity_id, old_value in self._saved_states.items():
            domain = entity_id.split(".")[0]
            if domain == "switch":
                await self.hass.services.async_call(domain, f"turn_{old_value}", {
                    "entity_id": entity_id
                })
            elif domain == "number":
                await self.hass.services.async_call(domain, "set_value", {
                    "entity_id": entity_id,
                    "value": float(old_value)
                })
        self._saved_states = {}
        await self._status_sensor.async_turn_off()
        self._monitor_zero = False
        if self._zero_timer:
            self._zero_timer()
            self._zero_timer = None
