from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import ChargeAmpsApi
from .coordinator import ChargeAmpsDataUpdateCoordinator
from .const import DOMAIN, PLATFORMS

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Charge Amps from a config entry."""
    email = entry.data.get("email")
    password = entry.data.get("password")

    api = ChargeAmpsApi(
        session=hass.helpers.aiohttp_client.async_get_clientsession(),
        email=email,
        password=password
    )
    coordinator = ChargeAmpsDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    # Spara coordinator för entiteter
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Initiera plattformar
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
