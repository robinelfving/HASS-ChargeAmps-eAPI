from __future__ import annotations

import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import ChargeAmpsDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up switches for all connectors in Charge Amps."""
    coordinator: ChargeAmpsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for cp_id, cp_data in coordinator.data.items():
        for connector_id in cp_data["connectors"]:
            entities.append(
                ConnectorSwitch(coordinator, cp_id, connector_id)
            )

    async_add_entities(entities)


class ConnectorSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to start/stop charging on a connector."""

    def __init__(
        self,
        coordinator: ChargeAmpsDataUpdateCoordinator,
        chargepoint_id: str,
        connector_id: int
    ) -> None:
        """Initialize the connector switch."""
        super().__init__(coordinator)
        self.chargepoint_id = chargepoint_id
        self.connector_id = connector_id
        cp_name = coordinator.data[chargepoint_id]["name"]
        self._attr_name = f"{cp_name} Connector {connector_id} Charging"

    @property
    def unique_id(self) -> str:
        """Return a unique ID for this switch."""
        return f"{self.chargepoint_id}_{self.connector_id}_charging"

    @property
    def is_on(self) -> bool:
        """Return True if connector is charging."""
        cp_data = self.coordinator.data.get(self.chargepoint_id, {})
        connector_data = cp_data.get("connectors", {}).get(self.connector_id, {})
        return connector_data.get("settings", {}).get("mode") == "Charging"

    @property
    def device_info(self) -> dict[str, str]:
        """Return device info for HA device registry."""
        cp = self.coordinator.data.get(self.chargepoint_id, {})
        return {
            "identifiers": {(DOMAIN, self.chargepoint_id)},
            "name": cp.get("name"),
            "manufacturer": "Charge Amps",
            "sw_version": cp.get("firmwareVersion"),
            "model": cp.get("type"),
        }

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the connector on (start charging)."""
        await self._set_mode("Charging")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the connector off (stop charging)."""
        await self._set_mode("Off")

    async def _set_mode(self, mode: str) -> None:
        """Set the connector mode via API and update cache."""
        _LOGGER.debug(
            "Setting connector %s/%s mode to %s",
            self.chargepoint_id,
            self.connector_id,
            mode
        )
        try:
            # PUT to Charge Amps API
            await self.coordinator.api.set_connector_mode(
                self.chargepoint_id,
                self.connector_id,
                mode
            )
        except Exception as err:
            _LOGGER.error(
                "Failed to set mode for connector %s/%s: %s",
                self.chargepoint_id,
                self.connector_id,
                err
            )
            return

        # Uppdatera intern cache så HA ser direkt ändringen
        connector_data = self.coordinator.data[self.chargepoint_id]["connectors"][self.connector_id]
        connector_data["settings"]["mode"] = mode
        self.coordinator.async_set_updated_data(self.coordinator.data)
        _LOGGER.debug(
            "Connector %s/%s mode updated in cache to %s",
            self.chargepoint_id,
            self.connector_id,
            mode
        )
