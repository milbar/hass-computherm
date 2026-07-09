import broadlink
import logging
import time
from datetime import datetime

from homeassistant.const import (
    PRECISION_HALVES
)

_LOGGER = logging.getLogger(__name__)

BROADLINK_ACTIVE = 1
BROADLINK_IDLE = 0
BROADLINK_POWER_ON = 1
BROADLINK_POWER_OFF = 0
BROADLINK_MODE_MANUAL = 0
BROADLINK_MODE_AUTO = 1
BROADLINK_SENSOR_INTERNAL = 0
BROADLINK_SENSOR_EXTERNAL = 1
BROADLINK_SENSOR_BOTH = 2
BROADLINK_TEMP_AUTO = 0
BROADLINK_TEMP_MANUAL = 1
BROADLINK_HEATING = 0
BROADLINK_COOLING = 1
BROADLINK_LOCK_OFF = 0
BROADLINK_LOCK_ON = 1

CONF_HOST = 'host'
CONF_USE_EXTERNAL_TEMP = 'use_external_temp'
CONF_SCHEDULE = 'schedule'
CONF_UNIQUE_ID = 'unique_id'
CONF_PRECISION = 'precision'
CONF_USE_COOLING = 'use_cooling'

DEFAULT_SCHEDULE = 0
DEFAULT_USE_EXTERNAL_TEMP = True
DEFAULT_PRECISION = PRECISION_HALVES
DEFAULT_USE_COOLING = False


class BroadlinkThermostat:

    def __init__(self, host):
        self._host = host

    def device(self):
        max_attempt = 3
        for attempt in range(0, max_attempt):
            try:
                attempt += 1
                broadlink.timeout = 1
                return broadlink.hello(self._host, timeout=3)
            except broadlink.exceptions.NetworkTimeoutError as e:
                if attempt == max_attempt:
                    _LOGGER.error("Thermostat %s network error: %s", self._host, str(e))

    def set_time(self):
        """Set thermostat time"""
        try:
            device = self.device()
            if device.auth():
                now = datetime.now()
                device.set_time(now.hour,
                                now.minute,
                                now.second,
                                now.weekday() + 1)
                _LOGGER.debug("Thermostat date / time is set")
        except Exception as e:
            _LOGGER.error("Thermostat %s set_time error: %s", self._host, str(e))

    def read_status(self):
        """Read thermostat data"""
        data = None
        try:
            device = self.device()
            if device.auth():
                data = device.get_full_status()
                _LOGGER.debug("Received %s thermostat data: %s", self._host, data)
        except Exception as e:
            _LOGGER.warning("Thermostat %s read_status() error: %s", self._host, str(e))
        finally:
            return data

    def read_raw_registers(self, start=0, count=22):
        """Read raw register data for discovery of undocumented features.

        Returns the raw byte payload from the device, or None on error.
        The standard Hysen protocol has 22 readable registers (addresses 0x00-0x15).
        Some Computherm variants may have additional registers.
        """
        raw = None
        try:
            device = self.device()
            if device.auth():
                raw = device.send_request([0x01, 0x03, start >> 8, start & 0xFF, count >> 8, count & 0xFF])
                _LOGGER.debug("Raw registers [%d..%d] from %s: %s", start, start + count, self._host, raw.hex())
        except Exception as e:
            _LOGGER.warning("Thermostat %s read_raw_registers() error: %s", self._host, str(e))
        finally:
            return raw

    def scan_registers(self, max_count=30):
        """Scan registers to find how many the device supports.

        Tries increasing register counts to find the valid range.
        Returns the maximum number of readable registers.
        """
        device = self.device()
        if not device or not device.auth():
            return 22
        for count in range(22, max_count + 1):
            try:
                device.send_request([0x01, 0x03, 0x00, 0x00, count >> 8, count & 0xFF])
            except Exception:
                return count - 1
        return max_count
