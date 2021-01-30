import logging

import time
import click

from iqair2mqtt import errors
from iqair2mqtt.iqair import IQAir
from iqair2mqtt.config import Config
from iqair2mqtt.mqtt import MQTTPublisher
from iqair2mqtt.iqair_parser import parse_measurements


logger = logging.getLogger('iqair2mqtt')


@click.command()
@click.option('-d', '--debug', default=False, is_flag=True)
@click.option('-c', '--config', 'config_path', type=str,
              prompt=False, help="Path to the config file")
def main(config_path: str, debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        # turn off logging for SMB
        logging.getLogger('SMB').setLevel(logging.WARNING)

    config = Config(config_path)
    iqair_device = IQAir(config.iqair_ip, config.iqair_login, config.iqair_password)
    try:
        iqair_device.noop()  # test connection to IQAIR
    except errors.IQAirConnectionError as exc:
        logger.warning(
            "Can't connect to IQAir. Check config. Err: %s",
            exc
        )
        return

    mqtt_publisher = MQTTPublisher(config.mqtt_hostname, config.mqtt_login, config.mqtt_password)

    latest_new_measurement = None
    while True:
        try:
            raw_iqair_measurements = iqair_device.get_latest_measurements()
        except errors.IQAirConnectionError as exc:
            logger.warning(
                "Can't get latest data from IQAir. Err %s",
                exc
            )
            continue
        iqair_measurements = parse_measurements(config, raw_iqair_measurements)

        # check measurements we got from IQAir are new compare to ones
        # we published last time
        if latest_new_measurement is None or iqair_measurements <= latest_new_measurement:
            logger.info(
                "Measurements '%s' from IQAir were already published, will not publish",
                iqair_measurements
            )
        else:
            logger.debug(
                "Got fresh IQAir measurements '%s', going to publish them",
                iqair_measurements
            )

            mqtt_publisher.publish(iqair_measurements.to_json())
            latest_new_measurement = iqair_measurements  # save last published measurements
        logger.debug("Sleeping for %d seconds", config.update_interal)
        time.sleep(config.update_interal)
