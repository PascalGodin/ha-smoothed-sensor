from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "smoothed_sensor"

# List the HA platforms this integration provides
PLATFORMS: list[Platform] = [Platform.SENSOR]

# (Optional) centralize your option keys so UI + code stay in sync
CONF_NAME = "name"
CONF_SOURCE = "source"
CONF_INTERVAL = "interval"
CONF_DECAY_TIME_MIN = "decay_time_min"
CONF_UNIT = "unit"
CONF_AGGREGATION = "aggregation"
CONF_EXPOSE_INPUT = "expose_input"
