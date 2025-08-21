from __future__ import annotations
from homeassistant.const import Platform

DOMAIN = "smoothed_sensor"

# Platforms provided by this integration
PLATFORMS: list[Platform] = [Platform.SENSOR]

# Canonical keys
CONF_NAME = "name"
CONF_SOURCE = "source"
CONF_INTERVAL = "interval"            # seconds
CONF_DECAY_TIME_MIN = "decay_time_min"  # minutes
CONF_UNIT = "unit"
CONF_AGGREGATION = "aggregation"
CONF_EXPOSE_INPUT = "expose_input"

# ---- Back-compat aliases (so older code keeps working) ----
CONF_DECAY_MIN = CONF_DECAY_TIME_MIN   # <- alias expected by config_flow.py
