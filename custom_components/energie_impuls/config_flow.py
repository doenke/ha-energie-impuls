from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD

DEFAULT_MIN_HYBRID = 1.5
DEFAULT_MIN_HYBRID_MINUTES = 10

class EnergieImpulsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Energie Impuls", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    def async_get_options_flow(self, config_entry):
        return EnergieImpulsOptionsFlowHandler(config_entry)


class EnergieImpulsOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Speichern und reload anstoßen
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                },
                options={
                    CONF_AUTO_MIN_PV: user_input[CONF_AUTO_MIN_PV],
                    CONF_AUTO_MINUTES: user_input[CONF_AUTO_MINUTES],
                },
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        current_data = self.config_entry.data
        current_options = self.config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME, default=current_data.get(CONF_USERNAME, "")): str,
                vol.Required(CONF_PASSWORD, default=current_data.get(CONF_PASSWORD, "")): str,
                vol.Required("min_hybrid", default=current_options.get(CONF_AUTO_MIN_PV, DEFAULT_MIN_HYBRID)): float,
                vol.Required("min_hybrid_minutes", default=current_options.get(CONF_AUTO_MINUTES, DEFAULT_MIN_HYBRID_MINUTES)): int,
            }),
        )
