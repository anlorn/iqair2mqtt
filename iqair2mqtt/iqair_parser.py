import logging
from typing import Dict, List

from iqair2mqtt.models.config import Config
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

    node_name = settings_section['node_name']
    is_indoor = settings_section['is_indoor']

    timestamp = date_and_time_section['timestamp']

    iqair_device = IQAirDevice(
        name=node_name,
        placement=config.get_placement,
        location=config.get_location,
        external=not is_indoor
    )

    measurements: List[IQAirMeasurement] = []

    for measurement_key, value in measurements_section.items():
        try:
            data_type, unit = measurement_key.split('_')
            data_type = data_type.lower()
            unit = unit.lower()
            measurement = IQAirMeasurement(
                measured_at=timestamp,
                name=data_type,
                value=value,
                unit=unit,
            )
            measurements.append(measurement)
            logger.debug(
                "Parsed measurement %s from device %s and timestamp %s",
                data_type,
                node_name,
                timestamp
            )
            if value.find('.') == -1:  # value is integer
                value = int(value)
            else:  # value is float
                value = float(value)

        except ValueError:
            logger.warning(
                "Can't parse measurement key %s for device %s. Will skip it",
                measurement_key,
                node_name
            )

    return IQAirMeasurements(iqair_device, measurements)
