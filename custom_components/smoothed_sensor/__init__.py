from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up smoothed_sensor from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # NOTE: No options listener here. After changing Options in the UI,
    # manually click "Reload" on the integration or restart HA.
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
