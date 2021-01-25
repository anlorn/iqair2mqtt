import logging
from os import environ

from iqair2mqtt.errors import ConfigVariableMissing

logger = logging.getLogger(__name__)


class Config:

    required_variables = [
        'IQAIR_IP',
        'IQAIR_LOGIN',
        'IQAIR_PASSWORD',
        'MQTT_HOSTNAME',
        'MQTT_LOGIN',
        'MQTT_PASSWORD',
    ]

    def __init__(self, config_file_path: str):
        for required_variable in self.required_variables:
            if required_variable not in environ:
                raise ConfigVariableMissing(required_variable)
            attr_name = f'_{required_variable.lower()}'
            setattr(self, attr_name, environ[required_variable])
            logger.debug("Saved variable '%s' to attribute 'self.%s'", required_variable, attr_name)

    @property
    def iqair_ip(self) -> str:
        return self._iqair_ip

    @property
    def iqair_login(self) -> str:
        return self._iqair_login

    @property
    def iqair_password(self) -> str:
        return self._iqair_password

    @property
    def mqtt_hostname(self) -> str:
        return self._mqtt_hostname

    @property
    def mqtt_login(self) -> str:
        return self._mqtt_login

    @property
    def mqtt_password(self) -> str:
        return self._mqtt_password

    @property
    def update_interal(self) -> int:
        return 15

    @property
    def get_location(self) -> str:
        return "some_location"

    @property
    def get_placement(self) -> str:
        return "some_placement"
