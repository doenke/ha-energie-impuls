
from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD

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
