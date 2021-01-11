import logging

import time
import click

from iqair2mqtt.iqair import IQAir
from iqair2mqtt.config import Config
from iqair2mqtt.mqtt import MQTTPublisher
from iqair2mqtt.iqair_parser import parse_measurements


logger = logging.getLogger(__name__)


@click.command()
@click.option('--config_path', prompt='Config file path')
def main(config_path: str):
    config = Config(config_path)
    iqair_device = IQAir(config.iqair_ip, config.iqair_login, config.iqair_password)
    mqtt_publisher = MQTTPublisher(config.mqtt_hostname, config.mqtt_login, config.mqtt_password)

    while True:
        raw_iqair_measurements = iqair_device.get_latest_measurements()
        iqair_measurements = parse_measurements(raw_iqair_measurements)
        mqtt_publisher.publish(iqair_measurements.to_json())
        time.sleep(config.update_interal)


if __name__ == '__main__':
    main()
