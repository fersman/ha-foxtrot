import logging
import aiohttp
from datetime import timedelta
from typing import List

from pyfoxtrot import pyfoxtrot

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)  # Polling interval

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Foxtrot platform."""
    coordinator = SensorDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for sensor_id, sensor_data in coordinator.data.items():
        sensors.append(Foxtrot(sensor_id, sensor_data, coordinator))

    async_add_entities(sensors, True)

class SensorDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching sensor data."""

    def __init__(self, hass):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name="dynamic_sensors",
            update_interval=SCAN_INTERVAL,
        )
        self._session = aiohttp.ClientSession()
        self._api_url = "http://<your-add-on-ip>:3000/sensors"

    async def _async_update_data(self):
        """Fetch data from the API."""
        try:
            async with self._session.get(self._api_url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as ex:
            raise UpdateFailed(f"Error communicating with API: {ex}")

class Foxtrot(SensorEntity):
    """Representation of a dynamic sensor."""

    def __init__(self, sensor_id: str, sensor_data: dict, coordinator: SensorDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        self._sensor_id = sensor_id
        self._sensor_data = sensor_data
        self._coordinator = coordinator

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._sensor_id

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"Dynamic Sensor {self._sensor_id}"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self._sensor_data.get('state')

    async def async_update(self) -> None:
        """Fetch new state data from the API."""
        await self._coordinator.async_request_refresh()

    @property
    def available(self) -> bool:
        """Return True if the entity is available."""
        return self._coordinator.last_update_success
