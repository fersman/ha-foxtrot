"""Tecomat Foxtrot."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import discovery

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = 'foxtrot'

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Foxtrot component."""
    # Initialize your custom component
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Foxtrot from a config entry."""
    # Register the entries discovery
    await discovery.async_load_platform(hass, "foxtrot", DOMAIN, {}, entry)
    return True
