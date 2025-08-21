DOMAIN = "smoothed_sensor"

CONF_SOURCE = "source"
CONF_NAME = "name"
CONF_INTERVAL = "interval"        # seconds; how often to aggregate + update
CONF_DECAY = "decay_time"         # tau in seconds; smoothing memory
CONF_UNIT = "unit"
CONF_AGGREGATION = "aggregation"  # "none" | "sample_mean" | "time_weighted"
CONF_EXPOSE_INPUT = "expose_input"  # bool: also create an "input" sensor

DEFAULT_INTERVAL = 15
DEFAULT_DECAY = 60
DEFAULT_AGGREGATION = "none"
VALID_AGGREGATIONS = ["none", "sample_mean", "time_weighted"]
DEFAULT_EXPOSE_INPUT = False
