from typing import Dict

from iqair2mqtt.models.iqair_measurement import IQAirMeasurements


def parse_measurements(raw_measurements: Dict) -> IQAirMeasurements:
    return IQAirMeasurements()
