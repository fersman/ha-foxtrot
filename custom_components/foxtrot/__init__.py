"""Tecomat Foxtrot."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = 'foxtrot'

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""

    hass.helpers.discovery.load_platform('foxtrot', DOMAIN, {}, config)

    return True
    