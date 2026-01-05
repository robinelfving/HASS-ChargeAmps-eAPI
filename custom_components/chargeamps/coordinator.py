"""DataUpdateCoordinator för ChargeAmps."""
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta

from .const import DEFAULT_SCAN_INTERVAL
from .handler import ChargeAmpsHandler

_LOGGER = logging.getLogger(__name__)

class ChargeAmpsCoordinator(DataUpdateCoordinator):
    """Koordinator som hanterar uppdatering av ChargeAmps-data."""

    def __init__(self, hass, handler: ChargeAmpsHandler):
        super().__init__(
            hass,
            _LOGGER,
            name="ChargeAmps",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.handler = handler

    async def _async_update_data(self):
        """Hämta data för alla chargepoints."""
        try:
            for cp_id in self.handler.charge_point_ids:
                await self.handler.update_data(cp_id)
        except Exception as err:
            raise UpdateFailed(f"Fel vid uppdatering: {err}") from err