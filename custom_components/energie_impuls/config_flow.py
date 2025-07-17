from homeassistant import config_entries
import voluptuous as vol
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_AUTO_MIN_PV,
    CONF_AUTO_MINUTES,
    DEFAULT_AUTO_MIN_PV,
    DEFAULT_AUTO_MINUTES,
)


class EnergieImpulsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Konfigurations-Flow für Energie Impuls."""

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Energie Impuls", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        return EnergieImpulsOptionsFlowHandler(config_entry)


class EnergieImpulsOptionsFlowHandler(config_entries.OptionsFlow):
    """Options-Flow für Energie Impuls."""

    def __init__(self, entry: config_entries.ConfigEntry):
        super().__init__()  # wichtig für Kompatibilität ab 2025.12
        self._entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Richtig: neue Optionen speichern in `options`, Zugangsdaten weiter in `data`
            self.hass.config_entries.async_update_entry(
                self._entry,
                data={  # Zugangsdaten bleiben in data
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                },
                options={  # Optionen separat speichern
                    CONF_AUTO_MIN_PV: user_input[CONF_AUTO_MIN_PV],
                    CONF_AUTO_MINUTES: user_input[CONF_AUTO_MINUTES],
                },
            )
            await self.hass.config_entries.async_reload(self._entry.entry_id)
            return self.async_create_entry(title="", data={})
    
        # 🛠 Hier ist der kritische Punkt: Entweder Optionen oder Fallback auf Defaults
        current_data = self._entry.data
        current_options = self._entry.options
    
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME, default=current_data.get(CONF_USERNAME, "")): str,
                vol.Required(CONF_PASSWORD, default=current_data.get(CONF_PASSWORD, "")): str,
                vol.Required(
                    CONF_AUTO_MIN_PV,
                    default=current_options.get(CONF_AUTO_MIN_PV, DEFAULT_AUTO_MIN_PV)
                ): vol.Coerce(float),
                vol.Required(
                    CONF_AUTO_MINUTES,
                    default=current_options.get(CONF_AUTO_MINUTES, DEFAULT_AUTO_MINUTES)
                ): int,
            }),
        )
