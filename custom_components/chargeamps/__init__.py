"""Init för Charge Amps custom component."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .api import ChargeAmpsClient
from .handler import ChargeAmpsHandler
from .coordinator import ChargeAmpsCoordinator
from .const import DOMAIN, DOMAIN_DATA, PLATFORMS

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    email = entry.data["email"]
    password = entry.data["password"]
    api_key = entry.data["api_key"]

    client = ChargeAmpsClient(email=email, password=password, api_key=api_key)
    handler = ChargeAmpsHandler(client)
    coordinator = ChargeAmpsCoordinator(hass, handler)

    hass.data.setdefault(DOMAIN_DATA, {})
    hass.data[DOMAIN_DATA]["handler"] = handler
    hass.data[DOMAIN_DATA]["coordinator"] = coordinator

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    await coordinator.async_config_entry_first_refresh()
    return True