import logging
from dateutil import parser
from datetime import datetime
from typing import Dict, List
from dateutil.tz import gettz

from iqair2mqtt.config import Config
from iqair2mqtt.errors import IQAirDataCorrupted
from iqair2mqtt.models.device import IQAirDevice
from iqair2mqtt.models.iqair_measurement import IQAirMeasurements, IQAirMeasurement


logger = logging.getLogger(__name__)


def parse_measurements(config: Config, raw_measurements: Dict) -> IQAirMeasurements:
    try:
        settings_section = raw_measurements['settings']
        measurements_section = raw_measurements['measurements']
        date_and_time_section = raw_measurements['date_and_time']
    except KeyError as exc:
        raise IQAirDataCorrupted(f"Data has no '{str(exc)}' section")

    try:
        node_name = settings_section['node_name']
        is_indoor = settings_section['is_indoor']
        timezone = settings_section['timezone']
        date = date_and_time_section['date']
        time = date_and_time_section['time']
        timestamp = int(date_and_time_section['timestamp'])
    except KeyError as exc:
        raise IQAirDataCorrupted(f"Can't fine key '{str(exc)}' in iqair data")

    iqair_device = IQAirDevice(
        name=node_name,
        placement=config.get_placement,
        location=config.get_location,
        external=not is_indoor
    )

    utc_datetime = _convert_to_utc_datetime(date, time, timezone)

    measurements: List[IQAirMeasurement] = []
    if measurements_section:
        logger.debug("Parsing %d measurements", len(measurements_section[0]))
        for measurement_key, value in measurements_section[0].items():
            try:
                data_type, unit = measurement_key.split('_')
                data_type = data_type.lower()
                unit = unit.lower()
                if value.find('.') == -1:  # value is integer
                    value = int(value)
                else:  # value is float
                    value = float(value)
                measurement = IQAirMeasurement(
                    measured_at=utc_datetime,
                    name=data_type,
                    value=value,
                    unit=unit,
                )
                measurements.append(measurement)
                logger.debug(
                    "Parsed measurement %s from device %s, measured_at %s",
                    data_type,
                    node_name,
                    utc_datetime.isoformat()
                )

            except ValueError:
                logger.warning(
                    "Can't parse measurement key %s for device %s. Will skip it",
                    measurement_key,
                    node_name
                )
    else:
        logger.warning("Measurements section is empty")

    return IQAirMeasurements(timestamp, iqair_device, measurements)


def _convert_to_utc_datetime(local_date: str, local_time: str, local_timezone: str) -> datetime:
    local_tz = gettz('America/New_York')
    local_datetime = parser.parse(" ".join([local_date, local_time, "TZ"]), tzinfos={'TZ': local_tz})
    return local_datetime.astimezone(gettz('UTC'))
