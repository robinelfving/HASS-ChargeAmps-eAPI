from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import ChargeAmpsApi, ChargeAmpsApiError
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ChargeAmpsDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator for Charge Amps data."""

    def __init__(self, hass: HomeAssistant, api: ChargeAmpsApi) -> None:
        """Initialize the coordinator."""
        self.api = api

        super().__init__(
            hass,
            _LOGGER,
            name="Charge Amps",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

        # Internal cache: chargepoint_id -> dict
        self.data: dict[str, Any] = {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API and normalize it."""
        try:
            raw_chargepoints = await self.api.get_chargepoints()
        except ChargeAmpsApiError as err:
            raise UpdateFailed(f"Error fetching Charge Amps data: {err}") from err

        chargepoints: dict[str, Any] = {}

        for cp in raw_chargepoints:
            cp_id = cp.get("id")
            if not cp_id:
                _LOGGER.warning("Found chargepoint without id: %s", cp)
                continue

            # Map chargepoint info
            chargepoints[cp_id] = {
                "id": cp_id,
                "name": cp.get("name"),
                "type": cp.get("type"),
                "firmwareVersion": cp.get("firmwareVersion"),
                "hardwareVersion": cp.get("hardwareVersion"),
                "isLoadbalanced": cp.get("isLoadbalanced", False),
                "ownerReadOnly": cp.get("ownerReadOnly", True),
                "ocppVersion": cp.get("ocppVersion"),
                "settings": cp.get("settings", {}),
                "connectors": {},
            }

            # Map connectors
            for connector in cp.get("connectors", []):
                connector_id = connector.get("connectorId")
                if connector_id is None:
                    _LOGGER.warning(
                        "Chargepoint %s has connector without id: %s", cp_id, connector
                    )
                    continue

                chargepoints[cp_id]["connectors"][connector_id] = {
                    "chargePointId": connector.get("chargePointId"),
                    "connectorId": connector_id,
                    "type": connector.get("type"),
                    "connectorUserId": connector.get("connectorUserId"),
                    "settings": connector.get("settings", {}),
                }

        # Update internal cache
        self.data = chargepoints
        return self.data
