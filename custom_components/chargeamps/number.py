from __future__ import annotations

import logging
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import ChargeAmpsDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up number entities for all connectors."""
    coordinator: ChargeAmpsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for cp_id, cp_data in coordinator.data.items():
        for connector_id in cp_data["connectors"]:
            entities.append(
                ConnectorMaxCurrentNumber(coordinator, cp_id, connector_id)
            )

    async_add_entities(entities)


class ConnectorMaxCurrentNumber(CoordinatorEntity, NumberEntity):
    """Number entity to set max current on connector."""

    def __init__(
        self,
        coordinator: ChargeAmpsDataUpdateCoordinator,
        chargepoint_id: str,
        connector_id: int
    ) -> None:
        """Initialize number entity."""
        super().__init__(coordinator)
        self.chargepoint_id = chargepoint_id
        self.connector_id = connector_id
        cp_name = coordinator.data[chargepoint_id]["name"]
        self._attr_name = f"{cp_name} Connector {connector_id} Max Current"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 32  # Anpassa efter laddpunktens max

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self.chargepoint_id}_{self.connector_id}_max_current"

    @property
    def native_value(self) -> int | None:
        """Return current maxCurrent value from coordinator."""
        cp_data = self.coordinator.data.get(self.chargepoint_id, {})
        connector_data = cp_data.get("connectors", {}).get(self.connector_id, {})
        return connector_data.get("settings", {}).get("maxCurrent")

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

    async def async_set_native_value(self, value: float) -> None:
        """Set maxCurrent via API and update cache."""
        value_int = int(value)
        _LOGGER.debug(
            "Setting connector %s/%s maxCurrent to %s",
            self.chargepoint_id,
            self.connector_id,
            value_int
        )
        try:
            await self.coordinator.api.set_connector_max_current(
                self.chargepoint_id,
                self.connector_id,
                value_int
            )
        except Exception as err:
            _LOGGER.error(
                "Failed to set maxCurrent for connector %s/%s: %s",
                self.chargepoint_id,
                self.connector_id,
                err
            )
            return

        # Uppdatera intern cache så HA visar direkt det nya värdet
        connector_data = self.coordinator.data[self.chargepoint_id]["connectors"][self.connector_id]
        connector_data["settings"]["maxCurrent"] = value_int
        self.coordinator.async_set_updated_data(self.coordinator.data)
        _LOGGER.debug(
            "Connector %s/%s maxCurrent updated in cache to %s",
            self.chargepoint_id,
            self.connector_id,
            value_int
        )
