# Computherm Thermostat

[![HACS Validation](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2021.2+-blue.svg)](https://www.home-assistant.io)
[![GitHub Release](https://img.shields.io/github/v/release/milbar/hass-computherm)](https://github.com/milbar/hass-computherm/releases)
[![License](https://img.shields.io/github/license/milbar/hass-computherm)](LICENSE)

Home Assistant integration for **Computherm** (and other Broadlink Hysen-based) WiFi thermostats. Controls 2-pipe fancoil systems with proper heating/cooling mode detection.

Forked from [algirdasc/hass-floureon](https://github.com/algirdasc/hass-floureon) with major fixes for Computherm thermostats.

## Features

- **Heating & Cooling** — correct detection and switching between heat/cool modes
- **HVAC actions** — shows Heating, Cooling, Idle, or Off based on actual thermostat state
- **Scheduled (Auto) / Manual** — follow built-in schedule or override temperature
- **Away preset** — set a separate temperature for away mode
- **Child lock** — lock/unlock thermostat buttons via `computherm.set_child_lock` service
- **External sensor** — use internal or external temperature sensor
- **Switch platform** — on/off control with configurable temperature thresholds
- **Advanced attributes** — hysteresis, anti-freeze, temperature calibration, sensor mode, etc.

> **Note:** Fan speed control is not supported — the Hysen thermostat hardware does not expose this.

## Installation

### HACS (recommended)

1. Open HACS → Integrations → Custom repositories
2. Add `https://github.com/milbar/hass-computherm` with category **Integration**
3. Click **Install**
4. Restart Home Assistant

### Manual

1. Copy the `custom_components/computherm/` directory into your HA `config/custom_components/`
2. Restart Home Assistant

## Configuration

### Climate entity

```yaml
climate:
  - platform: computherm
    name: Office Thermostat
    host: 192.168.1.100
    use_cooling: true
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` (required) | string | — | IP address or hostname of the thermostat |
| `name` (required) | string | — | Friendly name for the entity |
| `unique_id` | string | — | Unique ID for entity customisation in HA GUI |
| `schedule` | integer | `0` | Schedule pattern: `0` = weekdays/weekend, `1` = mon-sat/sun, `2` = all days |
| `use_external_temp` | boolean | `true` | `false` to use internal sensor instead of external |
| `precision` | float | `0.5` | Temperature precision: `0.5`, `1.0`, or `0.1` |
| `use_cooling` | boolean | `false` | Set to `true` if your system supports cooling |

### Switch entity (alternative on/off control)

```yaml
switch:
  - platform: computherm
    name: Office Thermostat
    host: 192.168.1.100
    turn_off_mode: min_temp
    turn_on_mode: max_temp
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` (required) | string | — | IP address or hostname of the thermostat |
| `name` (required) | string | — | Friendly name |
| `unique_id` | string | — | Unique ID |
| `turn_off_mode` | string or float | `min_temp` | Off method: `min_temp`, `turn_off`, or a float (e.g. `17`) |
| `turn_on_mode` | string or float | `max_temp` | On method: `max_temp` or a float (e.g. `23.5`) |
| `use_external_temp` | boolean | `true` | Sensor selection |

## Services

### `computherm.set_child_lock`

Lock or unlock the thermostat's physical buttons.

```yaml
service: computherm.set_child_lock
data:
  entity_id: climate.office_thermostat
  child_lock: true
```

### Template switch for child lock (UI control)

```yaml
switch:
  - platform: template
    switches:
      thermostat_child_lock:
        friendly_name: "Thermostat Child Lock"
        value_template: "{{ state_attr('climate.office_thermostat', 'child_lock') }}"
        turn_on:
          service: computherm.set_child_lock
          data:
            entity_id: climate.office_thermostat
            child_lock: true
        turn_off:
          service: computherm.set_child_lock
          data:
            entity_id: climate.office_thermostat
            child_lock: false
```

## Extra attributes

The climate entity exposes these additional attributes:

| Attribute | Description |
|-----------|-------------|
| `heating_cooling` | `heat` or `cool` — current HVAC mode setting |
| `child_lock` | `true`/`false` — physical button lock status |
| `hysteresis` | Deadzone temperature (1–9°C) |
| `room_temp_adj` | Temperature calibration offset |
| `anti_freeze` | `true`/`false` — anti-freeze function |
| `osv` | External sensor temperature range |
| `sensor_mode` | Sensor mode (0=internal, 1=external, 2=both) |
| `loop_mode` | Current schedule pattern |
| `away_set_point` | Away mode target temperature |
| `manual_set_point` | Manual mode target temperature |

## Supported devices

This integration works with Broadlink Hysen-based thermostats, including:

- Computherm (various models)
- Floureon
- Beca Energy / Beok
- Decdeal
- Hysen HY02B05H / HY03WE

If your thermostat works with the **Broadlink** app and has a similar form factor, it will likely work.

## License

Apache 2.0
