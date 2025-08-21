# Smoothed Sensor (Home Assistant Integration)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/docs/faq/custom_repositories)
[![GitHub Release](https://img.shields.io/github/release/PascalGodin/ha-smoothed-sensor.svg)](https://github.com/PascalGodin/ha-smoothed-sensor/releases)

## Overview

`smoothed_sensor` is a custom [Home Assistant](https://www.home-assistant.io/) integration that creates a **smoothed version of an existing sensor** using **exponential moving average (EMA)**.

This is useful when:
- The original sensor is noisy or updates irregularly.
- You want a time-weighted mean that reflects a decayed average rather than instantaneous values.
- You need a smoother input for automations or PID controllers.

The integration exposes:
- **Smoothed Sensor** → the calculated EMA value.  
- **Source Value Sensor** → the raw source reading used in the most recent calculation (for debugging/monitoring).  

## Features

- UI-based setup (no YAML required).  
- Adjustable **decay time** (in minutes) to tune how quickly the EMA responds to changes.  
- Works with any numeric sensor.  
- Friendly unique IDs so sensors survive restarts and renaming.  
- Ready for [HACS](https://hacs.xyz) auto-updates.  

## Installation

### HACS (recommended)

1. Go to **HACS → Integrations → Custom Repositories**.  
2. Add this repository:  
https://github.com/PascalGodin/ha-smoothed-sensor
with category: **Integration**.  
3. Search for and install **Smoothed Sensor**.  
4. Restart Home Assistant.

### Manual

1. Copy the `custom_components/smoothed_sensor` folder into your Home Assistant `custom_components` directory.  
2. Restart Home Assistant.  

## Configuration

1. In Home Assistant, go to **Settings → Devices & Services → Add Integration**.  
2. Search for **Smoothed Sensor**.  
3. Select:
- **Source sensor** → the entity you want to smooth.  
- **Decay time (minutes)** → how quickly past values decay in importance.  
4. Done! A new sensor will be created with the smoothed values.

## Example

If you have a noisy temperature sensor that spikes with every update:  

- Raw sensor: `sensor.outdoor_temp`  
- Smoothed sensor: `sensor.outdoor_temp_smoothed`  

This smoothed version can then be used in automations, dashboards, or PID controllers.  

## Notes

- A **decay time of 10 minutes** means old values halve in influence every ~10 minutes.  
- If you change the decay time in the UI, the integration will recalculate automatically.  
- The source value sensor is available for debugging but optional to use.  

---

## Development

Issues and PRs welcome!  

- Repo: [ha-smoothed-sensor](https://github.com/PascalGodin/ha-smoothed-sensor)  
- License: MIT  

