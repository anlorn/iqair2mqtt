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

    def __init__(self, revision: int, device: IQAirDevice, measurements: List[IQAirMeasurement]):

        # just in case check and fall early
        if not isinstance(revision, int):
            raise TypeError("Revision must be an integer")
        self.revision = revision
        self.measurements = measurements
        self.device = device

    def to_json(self) -> str:
        measurements = []
        for measurement in self.measurements:
            measurements.append(
                {
                    'measered_at': measurement.measured_at.isoformat(),
                    'type': measurement.name,
                    'value': measurement.value,
                    'unit': measurement.unit,
                }
            )

        data = {
            'location': self.device.location,
            'device_type': 'iqair',
            'device_name': self.device.name,
            'external': self.device.external,
            'placement': self.device.placement,
            'measurements': measurements
        }

        return json.dumps(data)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can't compare {self.__class__} to {type(other)}")
        return self.revision < other.revision

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can't compare {self.__class__} to {type(other)}")
        return self.revision <= other.revision

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can't compare {self.__class__} to {type(other)}")
        return self.revision > other.revision

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can't compare {self.__class__} to {type(other)}")
        return self.revision >= other.revision

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can't compare {self.__class__} to {type(other)}")
        return self.revision == other.revision

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can't compare {self.__class__} to {type(other)}")
        return self.revision == other.revision
