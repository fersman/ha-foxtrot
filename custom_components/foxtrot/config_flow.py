import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_URL
import homeassistant.helpers.config_validation as cv

class FoxtrotsConfigFlow(config_entries.ConfigFlow, domain="foxtrot"):
    """Handle a config flow for Dynamic Sensors."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default="Foxtrot"): str,
                vol.Required(CONF_URL, default="http://"): str,
            })
        )
