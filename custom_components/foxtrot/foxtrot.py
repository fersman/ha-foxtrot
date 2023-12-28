"""Platform for sensor integration."""
from __future__ import annotations

from pyfoxtrot import pyfoxtrot
import voluptuous as vol

import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.light import (PLATFORM_SCHEMA,
                                            LightEntity)
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_PORT, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from datetime import timedelta

SCAN_INTERVAL = timedelta(seconds=5)

from . import DOMAIN


_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default='5010'): cv.string,
    
    vol.Optional(CONF_USERNAME): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
})


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    
    host = config[CONF_HOST]
    port = config[CONF_PORT] or '5010'
    username = config[CONF_USERNAME]
    password = config.get(CONF_PASSWORD)

    foxtrot = pyfoxtrot.Foxtrot(host, port, username, password)
    my_api = hass.data[DOMAIN][entry.entry_id]
    coordinator = FoxtrotCoordinator(hass, my_api)
    await coordinator.async_config_entry_first_refresh()

    entities = []
    for name in list:
        if list[name]['type'] == 'light':
            entities.append(FoxtrotLight(name, foxtrot))
        elif list[name]['type'] == 'relay':
            entities.append(FoxtrotSwitch(name, foxtrot))
        elif list[name]['type'] == 'pir':
            entities.append(FoxtrotSensor(name, foxtrot))
        else:
            entities.append(FoxtrotSensor(name, foxtrot))

    add_entities(entities)

class FoxtrotCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, foxtrot):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="My sensor",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self.foxtrot = foxtrot

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(20):
                # Grab active context variables to limit data required to be fetched from API
                # Note: using context is not required if there is no need or ability to limit
                # data retrieved from API.
                listening_idx = set(self.async_contexts())
                return await self.my_api.fetch_data(listening_idx)
        except ApiAuthError as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")




class FoxtrotSensor(CoordinatorEntity, SensorEntity):
    """Representation of a sensor."""

    def __init__(self, entityName, coordinator, foxtrot) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, context=entityName)        
        self._state = None
        self.entityName = entityName
        self._foxtrot = foxtrot

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.getVariablesForEntity(self.entityName)['name']

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self.getVariablesForEntity(self.entityName)['unit'] or ''

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.getVariablesForEntity(self.entityName)['value']

class FoxtrotLight(CoordinatorEntity, LightEntity):
    """Representation of an Awesome Light."""

    def __init__(self, entityName, coordinator, foxtrot) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, context=entityName)
        self._state = None
        self.entityName = entityName
        self._foxtrot = foxtrot

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self.getVariablesForEntity(self.entityName)['name']

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._foxtrot.set(self.entityName, '1')

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._foxtrot.set(self.entityName, '0')

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.getVariablesForEntity(self.entityName)['value']

class FoxtrotSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an Awesome Light."""

    def __init__(self, entityName, coordinator, foxtrot) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, context=entityName)
        self._state = None
        self.entityName = entityName
        self._foxtrot = foxtrot

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self.getVariablesForEntity(self.entityName)['name']

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._foxtrot.set(self.entityName, '1')

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._foxtrot.set(self.entityName, '0')

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.getVariablesForEntity(self.entityName)['value']

