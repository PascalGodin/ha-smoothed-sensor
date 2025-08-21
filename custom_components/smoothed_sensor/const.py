from __future__ import annotations

from homeassistant.const import Platform

# --- Domain / Platforms ---
DOMAIN = "smoothed_sensor"
PLATFORMS: list[Platform] = [Platform.SENSOR]

# --- Canonical option keys (what the integration uses internally) ---
CONF_NAME = "name"
CONF_SOURCE = "source"
CONF_INTERVAL = "interval"             # seconds
CONF_DECAY_TIME_MIN = "decay_time_min" # minutes
CONF_UNIT = "unit"
CONF_AGGREGATION = "aggregation"       # e.g., "mean", "last", "min", "max", "sum"
CONF_EXPOSE_INPUT = "expose_input"     # bool

# --- Defaults used by config_flow/options and sensor setup ---
DEFAULT_INTERVAL = 15                  # seconds between updates
DEFAULT_DECAY_TIME_MIN = 10            # minutes (tau) default; adjust if you prefer
DEFAULT_UNIT: str | None = None        # keep source unit by default
DEFAULT_AGGREGATION = "mean"           # aggregate source readings within interval
DEFAULT_EXPOSE_INPUT = False

AGGREGATION_OPTIONS = ["mean", "last", "min", "max", "sum"]

# --- Back-compat aliases (older code/imports) ---
# Some earlier versions/branches referenced these names:
CONF_DECAY_MIN = CONF_DECAY_TIME_MIN
DEFAULT_DECAY_MIN = DEFAULT_DECAY_TIME_MIN
