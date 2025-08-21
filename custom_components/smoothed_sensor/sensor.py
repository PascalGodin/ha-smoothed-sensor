from __future__ import annotations

import math
from datetime import timedelta
from typing import Any, Optional, List

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import (
    async_track_time_interval,
    async_track_state_change_event,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_SOURCE,
    CONF_NAME,
    CONF_INTERVAL,
    CONF_DECAY_MIN,          # MINUTES from UI
    CONF_UNIT,
    CONF_AGGREGATION,
    CONF_EXPOSE_INPUT,
    DEFAULT_INTERVAL,
    DEFAULT_DECAY_MIN,
    DEFAULT_AGGREGATION,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Create the entity (and optional input entity) for this config entry."""
    main = EmaSmoothedSensor(hass, entry)
    entities: List[SensorEntity] = [main]

    expose_input = dict(entry.options).get(
        CONF_EXPOSE_INPUT, dict(entry.data).get(CONF_EXPOSE_INPUT, False)
    )
    if expose_input:
        entities.append(EmaInputSensor(main))

    async_add_entities(entities)


class EmaSmoothedSensor(RestoreEntity, SensorEntity):
    """Smoothed numeric sensor with optional per-interval aggregation + EMA decay."""

    _attr_should_poll = False
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry

        data = dict(entry.data)
        options = dict(entry.options)

        self._source = options.get(CONF_SOURCE, data.get(CONF_SOURCE))
        self._name = options.get(CONF_NAME, data.get(CONF_NAME))
        self._interval = int(options.get(CONF_INTERVAL, data.get(CONF_INTERVAL, DEFAULT_INTERVAL)))
        # MINUTES → SECONDS
        self._decay_min = float(options.get(CONF_DECAY_MIN, data.get(CONF_DECAY_MIN, DEFAULT_DECAY_MIN)))
        self._decay_s = self._decay_min * 60.0

        self._aggregation = options.get(CONF_AGGREGATION, data.get(CONF_AGGREGATION, DEFAULT_AGGREGATION))

        unit_raw = options.get(CONF_UNIT, data.get(CONF_UNIT))
        self._unit = unit_raw if unit_raw else None

        self._alpha = self._compute_alpha(self._interval, self._decay_s)

        self._attr_name = self._name
        # Stable unique_id: config entry id only
        self._attr_unique_id = entry.entry_id
        if self._unit:
            self._attr_native_unit_of_measurement = self._unit

        self._attr_device_class = None

        self._state: Optional[float] = None
        self._last_input: Optional[float] = None

        # Dependents updated each tick (e.g., input sensor)
        self._dependents: list[SensorEntity] = []

        # Aggregation accumulators
        self._sum = 0.0
        self._count = 0

        self._tw_last_value: Optional[float] = None
        self._tw_last_time = None
        self._tw_weighted_sum = 0.0
        self._tw_duration = 0.0

        self._unsub_timer = None
        self._unsub_state = None

    @staticmethod
    def _compute_alpha(dt_s: float, tau_s: float) -> float:
        """EMA alpha from interval (dt_s) and decay time constant tau_s."""
        if tau_s <= 0:
            return 1.0  # no smoothing
        # alpha = dt / (tau + dt) == 1 - exp(-dt/tau)
        return float(dt_s / (tau_s + dt_s))

    async def async_added_to_hass(self) -> None:
        # Mirror unit/device_class from source if not explicitly set
        src = self.hass.states.get(self._source)
        if src is not None:
            attrs = src.attributes or {}
            if not self._unit:
                unit = attrs.get("unit_of_measurement")
                if unit:
                    self._unit = unit
                    self._attr_native_unit_of_measurement = unit
            dc = attrs.get("device_class")
            if dc and self._attr_device_class is None and isinstance(dc, str):
                try:
                    self._attr_device_class = SensorDeviceClass(dc)
                except ValueError:
                    pass

        # Restore EMA state
        last = await self.async_get_last_state()
        if last and last.state not in (None, "unknown", "unavailable"):
            try:
                self._state = float(last.state)
            except (ValueError, TypeError):
                self._state = None

        # Listen for source updates (for aggregation)
        @callback
        def _on_source_change(event):
            new_state = event.data.get("new_state")
            if new_state is None:
                return
            try:
                val = float(new_state.state)
            except Exception:
                return

            now = dt_util.utcnow()

            # Sample mean accumulators
            self._sum += val
            self._count += 1

            # Time-weighted accumulators
            if self._tw_last_time is None:
                self._tw_last_time = now
                self._tw_last_value = val
            else:
                dt = (now - self._tw_last_time).total_seconds()
                if dt > 0 and self._tw_last_value is not None:
                    self._tw_weighted_sum += self._tw_last_value * dt
                    self._tw_duration += dt
                self._tw_last_time = now
                self._tw_last_value = val

        self._unsub_state = async_track_state_change_event(
            self.hass, [self._source], _on_source_change
        )

        @callback
        def _tick(now):
            self._recompute()

        self._unsub_timer = async_track_time_interval(
            self.hass, _tick, timedelta(seconds=self._interval)
        )

        # Seed TW path with current value so flat periods count correctly
        current = self._get_source_value()
        if current is not None:
            self._tw_last_value = current
            self._tw_last_time = dt_util.utcnow()

        # Compute immediately once
        self._recompute()

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None
        if self._unsub_state:
            self._unsub_state()
            self._unsub_state = None

    def _get_source_value(self) -> Optional[float]:
        st = self.hass.states.get(self._source)
        if not st:
            return None
        try:
            return float(st.state)
        except (ValueError, TypeError):
            return None

    @callback
    def _aggregate_value(self) -> Optional[float]:
        """Compute per-interval input x via selected aggregation, then reset accumulators."""
        x = None
        if self._aggregation == "sample_mean":
            if self._count > 0:
                x = self._sum / self._count
        elif self._aggregation == "time_weighted":
            now = dt_util.utcnow()
            if self._tw_last_time is not None and self._tw_last_value is not None:
                dt = (now - self._tw_last_time).total_seconds()
                if dt > 0:
                    self._tw_weighted_sum += self._tw_last_value * dt
                    self._tw_duration += dt
                    self._tw_last_time = now
            if self._tw_duration > 0:
                x = self._tw_weighted_sum / self._tw_duration

        # Reset per-interval accumulators
        self._sum = 0.0
        self._count = 0
        self._tw_weighted_sum = 0.0
        self._tw_duration = 0.0
        # Keep _tw_last_time/_tw_last_value so it continues into next interval

        if x is None:
            x = self._get_source_value()
        return x

    @callback
    def _recompute(self) -> None:
        x = self._aggregate_value()
        if x is None:
            return

        # Record input for dependent sensors
        self._last_input = x

        # EMA update
        if self._state is None:
            self._state = x
        else:
            a = self._alpha
            self._state = (a * x) + ((1.0 - a) * self._state)

        # Write our state
        self.async_write_ha_state()

        # Notify dependents only if they're already attached to HA
        for dep in list(self._dependents):
            if getattr(dep, "hass", None) is not None:
                dep.async_write_ha_state()

    @property
    def native_value(self) -> Optional[float]:
        return None if self._state is None else round(self._state, 4)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        # expose both minutes & seconds for clarity
        return {
            "source": self._source,
            "interval_s": self._interval,
            "decay_time_min": round(self._decay_min, 4),
            "decay_time_s": round(self._decay_s, 3),
            "alpha": round(self._alpha, 6),
            "aggregation": self._aggregation,
            "last_input": None if self._last_input is None else round(self._last_input, 4),
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Smoothed Sensor",
            manufacturer="Community",
            model="EMA",
        )


class EmaInputSensor(SensorEntity):
    """Companion entity that exposes the last aggregated input value."""

    _attr_should_poll = False
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, parent: EmaSmoothedSensor) -> None:
        self._parent = parent
        self._attr_name = f"{parent.name} (input)"
        self._attr_unique_id = f"{parent.unique_id}_input"

        # inherit unit/device_class from parent (which mirrors source)
        self._attr_native_unit_of_measurement = parent._unit
        self._attr_device_class = parent.device_class

        # register as dependent so parent can push updates
        parent._dependents.append(self)

    async def async_added_to_hass(self) -> None:
        return

    @property
    def native_value(self) -> Optional[float]:
        val = self._parent._last_input  # latest aggregated input
        return None if val is None else round(val, 4)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "source": self._parent._source,
            "aggregation": self._parent._aggregation,
            "interval_s": self._parent._interval,
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Smoothed Sensor",
            manufacturer="Community",
            model="EMA",
        )
