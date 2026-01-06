from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD

class ChargeAmpsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Charge Amps."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]

            # För enkelhet, vi sparar bara inloggning här
            return self.async_create_entry(
                title=email,
                data={
                    CONF_EMAIL: email,
                    CONF_PASSWORD: password
                }
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )
