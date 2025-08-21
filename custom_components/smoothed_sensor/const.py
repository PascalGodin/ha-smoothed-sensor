DOMAIN = "smoothed_sensor"

CONF_SOURCE = "source"
CONF_NAME = "name"
CONF_INTERVAL = "interval"           # seconds; update cadence
CONF_DECAY_MIN = "decay_time_min"    # MINUTES in UI; convert to seconds internally
CONF_UNIT = "unit"
CONF_AGGREGATION = "aggregation"     # "none" | "sample_mean" | "time_weighted"
CONF_EXPOSE_INPUT = "expose_input"   # bool: also create an "(input)" sensor

DEFAULT_INTERVAL = 15                # seconds
DEFAULT_DECAY_MIN = 1.0              # minutes (e.g., 1 min default = 60s)
DEFAULT_AGGREGATION = "none"
VALID_AGGREGATIONS = ["none", "sample_mean", "time_weighted"]
DEFAULT_EXPOSE_INPUT = False
