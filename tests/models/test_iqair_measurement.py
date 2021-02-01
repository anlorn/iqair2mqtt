import json
import pytest
from random import randint
from datetime import datetime, timedelta


from iqair2mqtt.models.device import IQAirDevice
from iqair2mqtt.models.iqair_measurement import IQAirMeasurements, IQAirMeasurement


@pytest.fixture
def device(request):
    """
    Generates 'iqair2mqtt.models.device.IQAirDevice'
    """
    return IQAirDevice(
        name="test_device",
        placement="test_pacement",
        location="test_location",
        external=False
    )


@pytest.fixture
def measurements(request):
    """
    Generates iqair2mqtt.models.iqair_measurement.IQAirMeasurement.
    Accepts a param which defines how many of them should be generated
    """
    res = []
    for i in range(getattr(request, 'param', 1)):
        res.append(
            IQAirMeasurement(
                measured_at=datetime.utcnow() + timedelta(days=i),
                name='test_measurement',
                value=randint(0, 40),
                unit='c'
            )
        )
    return res


@pytest.mark.parametrize('measurements', [1], indirect=['measurements'])
def test_iqair_measurements_to_json(device, measurements):
    iqair_measurements = IQAirMeasurements(23, device, measurements)

    expected_json = {
        'location': device.location,
        'device_type': 'iqair',
        'device_name': device.name,
        'external': device.external,
        'placement': device.placement,
        'measurements': [
            {
                'measered_at': measurements[0].measured_at.isoformat(),
                'type': measurements[0].name,
                'value': measurements[0].value,
                'unit': measurements[0].unit,
            }
        ]
    }

    assert json.dumps(expected_json) == iqair_measurements.to_json()


@pytest.mark.parametrize('measurements', [2], indirect=['measurements'])
def test_iqair_measurements_comparsions(device, measurements):
    measurements_earlier = IQAirMeasurements(23, device, [measurements[0]])
    measurements_earlier_duplicate = IQAirMeasurements(23, device, [measurements[0]])
    measurements_later = IQAirMeasurements(24, device, [measurements[1]])

    assert measurements_earlier < measurements_later
    assert measurements_earlier <= measurements_later
    assert measurements_earlier != measurements_later
    assert measurements_earlier == measurements_earlier_duplicate
    assert measurements_later > measurements_earlier
    assert measurements_later >= measurements_earlier
    assert measurements_later >= measurements_earlier


def test_iqair_measurements_error_on_not_int_revision(device, measurements):
    with pytest.raises(TypeError):
        IQAirMeasurements('23', device, measurements)
