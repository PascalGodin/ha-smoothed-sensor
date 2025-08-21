from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import selector

from .const import (
    DOMAIN,
    CONF_SOURCE,
    CONF_NAME,
    CONF_INTERVAL,
    CONF_DECAY_MIN,
    CONF_UNIT,
    CONF_AGGREGATION,
    CONF_EXPOSE_INPUT,
    DEFAULT_INTERVAL,
    DEFAULT_DECAY_MIN,
    DEFAULT_AGGREGATION,
    DEFAULT_EXPOSE_INPUT,
)

AGGREGATION_OPTIONS = [
    {"label": "None (use latest value)", "value": "none"},
    {"label": "Sample mean (all updates in interval)", "value": "sample_mean"},
    {"label": "Time-weighted mean (irregular updates)", "value": "time_weighted"},
]


class SmoothedSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME): cv.string,
                vol.Required(CONF_SOURCE): selector({"entity": {"domain": "sensor"}}),
                vol.Required(CONF_INTERVAL, default=DEFAULT_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=3600)
                ),
                # MINUTES in UI
                vol.Required(CONF_DECAY_MIN, default=DEFAULT_DECAY_MIN): vol.All(
                    vol.Coerce(float), vol.Range(min=0.0)
                ),
                vol.Optional(CONF_UNIT): cv.string,  # avoid literal None in schema
                vol.Required(CONF_AGGREGATION, default=DEFAULT_AGGREGATION): selector(
                    {"select": {"options": AGGREGATION_OPTIONS}}
                ),
                vol.Required(CONF_EXPOSE_INPUT, default=DEFAULT_EXPOSE_INPUT): selector(
                    {"boolean": {}}
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SmoothedSensorOptionsFlow(config_entry)


class SmoothedSensorOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = {**self.entry.data, **self.entry.options}

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=data.get(CONF_NAME, "")): cv.string,
                vol.Required(CONF_SOURCE, default=data.get(CONF_SOURCE, "")): selector(
                    {"entity": {"domain": "sensor"}}
                ),
                vol.Required(CONF_INTERVAL, default=data.get(CONF_INTERVAL, DEFAULT_INTERVAL)): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=3600)
                ),
                # MINUTES in UI
                vol.Required(CONF_DECAY_MIN, default=data.get(CONF_DECAY_MIN, DEFAULT_DECAY_MIN)): vol.All(
                    vol.Coerce(float), vol.Range(min=0.0)
                ),
                vol.Optional(CONF_UNIT, default=(data.get(CONF_UNIT) or "")): cv.string,
                vol.Required(CONF_AGGREGATION, default=data.get(CONF_AGGREGATION, DEFAULT_AGGREGATION)): selector(
                    {"select": {"options": AGGREGATION_OPTIONS}}
                ),
                vol.Required(CONF_EXPOSE_INPUT, default=data.get(CONF_EXPOSE_INPUT, DEFAULT_EXPOSE_INPUT)): selector(
                    {"boolean": {}}
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)
