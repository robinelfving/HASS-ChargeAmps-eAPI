"""Sensorer för ChargeAmps."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNAVAILABLE, UnitOfEnergy, UnitOfPower
from .handler import ChargeAmpsHandler
from .const import DOMAIN_DATA, CHARGEPOINT_ONLINE, ICON_MAP, DEFAULT_ICON
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ChargeAmpsSensor(SensorEntity):
    """Sensor för connector status."""

    def __init__(self, handler: ChargeAmpsHandler, charge_point_id: str, connector_id: int):
        self.handler = handler
        self.charge_point_id = charge_point_id
        self.connector_id = connector_id
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return f"{self.charge_point_id}_{self.connector_id}"

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        info = self.handler.data[self.charge_point_id]["info"]
        return ICON_MAP.get(info.type, DEFAULT_ICON)

    async def async_update(self):
        await self.handler.update_data(self.charge_point_id)
        status = self.handler.get_connector_status(self.charge_point_id, self.connector_id)
        cp_status = self.handler.data[self.charge_point_id]["status"]
        if status is None or cp_status.status != CHARGEPOINT_ONLINE:
            self._state = STATE_UNAVAILABLE
        else:
            self._state = status.status
            self._attributes["total_consumption_kwh"] = round(status.total_consumption_kwh, 3)