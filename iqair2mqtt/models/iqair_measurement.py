import json
from datetime import datetime
from typing import Union, List, NamedTuple

from iqair2mqtt.models.device import IQAirDevice


class IQAirMeasurement(NamedTuple):
    measured_at: datetime  # UTC
    name: str
    value: Union[int, float]
    unit: str


class IQAirMeasurements:

    def __init__(self, device: IQAirDevice, measurements: List[IQAirMeasurement]):
        self.measurements = measurements
        self.device = device

    def to_json(self) -> str:
        data = {
            'location': self.device.location,
            'device_type': 'iqair',
            'device_name': self.device.name,
            'external': self.device.external,
            'placement': self.device.placement,
            'measurement': []
        }
        for measurement in self.measurements:
            data['measurement'].append(
                {
                    'measered_at': measurement.measured_at,
                    'type': measurement.name,
                    'value': measurement.value,
                    'unit': measurement.unit,
                }
            )
        return json.dumps(data)
