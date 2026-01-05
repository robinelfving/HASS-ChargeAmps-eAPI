"""Handler för ChargeAmps: hanterar chargepoints och connectors."""
import logging
from datetime import datetime, timedelta

from .const import DOMAIN, DOMAIN_DATA, DEFAULT_SCAN_INTERVAL, CHARGEPOINT_ONLINE
from .api import ChargeAmpsClient, ChargePoint, ChargePointConnectorStatus, ChargePointSettings, ChargePointConnectorSettings

_LOGGER = logging.getLogger(__name__)

class ChargeAmpsHandler:
    """Hantera kommunikation med ChargeAmps API och lagra data."""

    def __init__(self, client: ChargeAmpsClient, scan_interval: timedelta = timedelta(seconds=DEFAULT_SCAN_INTERVAL)):
        self.client = client
        self.scan_interval = scan_interval
        self.charge_point_ids: list[str] = []
        self.last_scanned: dict[str, datetime] = {}
        self.data: dict = {}

    async def initialize_chargepoints(self):
        """Hämta alla chargepoints från API."""
        cps = await self.client.get_chargepoints()
        self.charge_point_ids = [cp.id for cp in cps]
        for cp in cps:
            self.last_scanned[cp.id] = datetime.fromtimestamp(0)
            self.data[cp.id] = {
                "info": cp,
                "status": None,
                "settings": None,
                "connector_status": {},
                "connector_settings": {}
            }

    async def update_data(self, charge_point_id: str):
        """Hämta och uppdatera data för en chargepoint."""
        now = datetime.now()
        if now - self.last_scanned.get(charge_point_id, datetime.fromtimestamp(0)) < self.scan_interval:
            return
        self.last_scanned[charge_point_id] = now

        # Hämta status och settings
        status = await self.client.get_chargepoint_status(charge_point_id)
        settings = await self.client.get_chargepoint_settings(charge_point_id)

        self.data[charge_point_id]["status"] = status
        self.data[charge_point_id]["settings"] = settings

        # Hämta connector status och settings
        for conn_status in status.connector_statuses:
            connector_id = conn_status.connector_id
            self.data[charge_point_id]["connector_status"][connector_id] = conn_status
            connector_settings = await self.client.get_chargepoint_connector_settings(charge_point_id, connector_id)
            self.data[charge_point_id]["connector_settings"][connector_id] = connector_settings

    def get_chargepoint_status(self, charge_point_id: str) -> ChargePointConnectorStatus:
        return self.data[charge_point_id]["status"]

    def get_connector_status(self, charge_point_id: str, connector_id: int) -> ChargePointConnectorStatus:
        return self.data[charge_point_id]["connector_status"].get(connector_id)