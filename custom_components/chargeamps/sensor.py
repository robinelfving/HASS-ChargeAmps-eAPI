from __future__ import annotations

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import ChargeAmpsDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = [
    "firmwareVersion",
    "hardwareVersion",
    "dimmer",
    "downLight",
    "isLoadbalanced",
    "ownerReadOnly",
    "ocppVersion",
]


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors for all chargepoints and connectors."""
    coordinator: ChargeAmpsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for cp_id, cp_data in coordinator.data.items():
        # Chargepoint-level sensors
        for sensor_type in SENSOR_TYPES:
            if sensor_type in cp_data:
                entities.append(
                    ChargePointSensor(coordinator, cp_id, sensor_type)
                )

        # Connector-level sensors
        for connector_id, connector_data in cp_data["connectors"].items():
            connector_settings = connector_data.get("settings", {})
            for key in connector_settings:
                entities.append(
                    ConnectorSensor(coordinator, cp_id, connector_id, key)
                )

    _LOGGER.debug("Adding %d Charge Amps sensors", len(entities))
    async_add_entities(entities)


class ChargePointSensor(CoordinatorEntity, SensorEntity):
    """Sensor for a chargepoint attribute."""

    def __init__(
        self,
        coordinator: ChargeAmpsDataUpdateCoordinator,
        chargepoint_id: str,
        attr_name: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.chargepoint_id = chargepoint_id
        self.attr_name = attr_name
        self._attr_name = f"{coordinator.data[chargepoint_id]['name']} {attr_name}"
        _LOGGER.debug("Created ChargePointSensor: %s", self._attr_name)

    @property
    def unique_id(self) -> str:
        return f"{self.chargepoint_id}_{self.attr_name}"

    @property
    def name(self) -> str:
        return self._attr_name

    @property
    def native_value(self):
        cp_data = self.coordinator.data.get(self.chargepoint_id, {})
        return cp_data.get(self.attr_name)

    @property
    def device_info(self) -> dict[str, str]:
        cp = self.coordinator.data.get(self.chargepoint_id, {})
        return {
            "identifiers": {(DOMAIN, self.chargepoint_id)},
            "name": cp.get("name"),
            "manufacturer": "Charge Amps",
            "sw_version": cp.get("firmwareVersion"),
            "model": cp.get("type"),
        }


class ConnectorSensor(CoordinatorEntity, SensorEntity):
    """Sensor for a connector setting."""

    def __init__(
        self,
        coordinator: ChargeAmpsDataUpdateCoordinator,
        chargepoint_id: str,
        connector_id: int,
        attr_name: str
    ) -> None:
        """Initialize the connector sensor."""
        super().__init__(coordinator)
        self.chargepoint_id = chargepoint_id
        self.connector_id = connector_id
        self.attr_name = attr_name
        self._attr_name = f"{coordinator.data[chargepoint_id]['name']} Connector {connector_id} {attr_name}"
        _LOGGER.debug("Created ConnectorSensor: %s", self._attr_name)

    @property
    def unique_id(self) -> str:
        return f"{self.chargepoint_id}_{self.connector_id}_{self.attr_name}"

    @property
    def name(self) -> str:
        return self._attr_name

    @property
    def native_value(self):
        cp_data = self.coordinator.data.get(self.chargepoint_id, {})
        connector_data = cp_data.get("connectors", {}).get(self.connector_id, {})
        return connector_data.get("settings", {}).get(self.attr_name)

    @property
    def device_info(self) -> dict[str, str]:
        cp = self.coordinator.data.get(self.chargepoint_id, {})
        return {
            "identifiers": {(DOMAIN, self.chargepoint_id)},
            "name": cp.get("name"),
            "manufacturer": "Charge Amps",
            "sw_version": cp.get("firmwareVersion"),
            "model": cp.get("type"),
        }
