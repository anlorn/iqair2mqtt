import pytest
from mock import MagicMock, call
from datetime import datetime
from dateutil.tz import gettz

from iqair2mqtt import iqair_parser
from iqair2mqtt.config import Config
from iqair2mqtt.models.iqair_measurement import IQAirMeasurements, IQAirMeasurement, IQAirDevice


@pytest.fixture
def iqair_data():
    data = {
        'date_and_time':
        {
            'date': '2020/12/27',
            'time': '15:55:01',
            'timestamp': '1609084501'
        },
        'measurements':
        [
            {
                'co2_ppm': '429',
                'humidity_RH': '22',
                'pm01_ugm3': '2.0',
                'pm10_ugm3': '2',
                'pm25_AQICN': '3',
                'pm25_AQIUS': '8',
                'pm25_ugm3': '2.0',
                'temperature_C': '20.6',
                'temperature_F': '69.0',
                'voc_ppb': '-1'
            }
        ],
        'serial_number': 'XXXXXXXXXX',
        'settings':
        {
            'follow_mode': 'station',
            'followed_station': '00000',
            'is_aqi_usa': True,
            'is_concentration_showed': False,
            'is_indoor': True,
            'is_lcd_on': True,
            'is_network_time': True,
            'is_temperature_celsius': True,
            'language': 'en-US',
            'lcd_brightness': 0,
            'node_name': 'test',
            'power_saving':
            {
                '2slots':
                [
                    {'hour_off': 9, 'hour_on': 7},
                    {'hour_off': 22, 'hour_on': 18}
                ],
                'mode': 'yes',
                'running_time': 99,
                'yes': [
                    {'hour': 8, 'minute': 45}, {'hour': 22, 'minute': 0}
                ]
            },
            'sensor_mode': {'custom_mode_interval': 3, 'mode': 1},
            'speed_unit': 'mph',
            'timezone': 'America/New_York',
            'tvoc_unit': 'ppm'
        },
        'status':
        {
            'app_version': '1.0000',
            'battery': 100,
            'datetime': 1609084501,
            'device_name': 'AIRVISUAL-XXXXXXXXXX',
            'ip_address': '127.0.0.1',
            'mac_address': 'aaaaaaaaaaaa',
            'model': 30,
            'sensor_life': {'pm25': 28800000},
            'sensor_pm25_serial': 'XXXXXXXXXXXX',
            'sync_time': 250000,
            'system_version': 'XXXXXXXXX',
            'used_memory': 2,
            'wifi_strength': 5
        }
    }
    return data


@pytest.fixture
def config():
    config = MagicMock(
        spec=Config,
        get_placement='test_placement',
        get_location='test_location',
    )
    return config


def test_parser(iqair_data, config, monkeypatch):
    measurements = MagicMock(spec=IQAirMeasurements, return_value='test')
    monkeypatch.setattr(iqair_parser, 'IQAirMeasurements', measurements)
    parsed_data = iqair_parser.parse_measurements(config, iqair_data)

    expected_measured_at = datetime(
        2020, 12, 27, 20, 55, 1, tzinfo=gettz('UTC')
    )

    expected_device_info = IQAirDevice(
        name='test', placement='test_placement',
        location='test_location', external=False
    )

    expected_measurements = [
        IQAirMeasurement(measured_at=expected_measured_at, name='co2', value=429, unit='ppm'),
        IQAirMeasurement(measured_at=expected_measured_at, name='humidity', value=22, unit='rh'),
        IQAirMeasurement(measured_at=expected_measured_at, name='pm01', value=2.0, unit='ugm3'),
        IQAirMeasurement(measured_at=expected_measured_at, name='pm10', value=2, unit='ugm3'),
        IQAirMeasurement(measured_at=expected_measured_at, name='pm25', value=3, unit='aqicn'),
        IQAirMeasurement(measured_at=expected_measured_at, name='pm25', value=8, unit='aqius'),
        IQAirMeasurement(measured_at=expected_measured_at, name='pm25', value=2.0, unit='ugm3'),
        IQAirMeasurement(measured_at=expected_measured_at, name='temperature', value=20.6, unit='c'),
        IQAirMeasurement(measured_at=expected_measured_at, name='temperature', value=69.0, unit='f'),
        IQAirMeasurement(measured_at=expected_measured_at, name='voc', value=-1, unit='ppb')
    ]

    assert parsed_data == measurements.return_value
    assert measurements.call_args_list == [call(1609084501, expected_device_info, expected_measurements)]
