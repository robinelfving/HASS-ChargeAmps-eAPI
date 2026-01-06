from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD
from .api import ChargeAmpsApi, ChargeAmpsAuthError

class ChargeAmpsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Charge Amps."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step initiated by the user."""
        errors = {}

        if user_input:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]

            # Test API login using HA session
            session = self.hass.helpers.aiohttp_client.async_get_clientsession()
            api = ChargeAmpsApi(session=session, email=email, password=password)

            try:
                await api._login()
            except ChargeAmpsAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"

            if not errors:
                # All good, create entry
                return self.async_create_entry(
                    title=email,
                    data={
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password
                    }
                )

        # Show form (first time or on errors)
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
