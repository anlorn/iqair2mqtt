import json
import logging
import tempfile
from socket import timeout
from typing import Dict

from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure

from iqair2mqtt import errors

logger = logging.getLogger()

CONNECTION_TIMEOUT = 3
CONNECTION_ATTEMPTS = 3


class IQAir:
    """
    Class responsible for communication with IQAIR device.
    """

    def __init__(self, ip: str, login: str, password: str):
        self._ip = ip
        self._login = login
        self._password = password

        # just verify right on the start that provided credentials/ip are correct
        connection = self._connect_to_iqair()
        if connection:
            connection.close()

    def get_latest_measurements(self) -> Dict:
        """
        Returns dict which is parsed `latest_config_measurements.json`.
        This fils contains last measures and information about device itself.

        Can raise the exceptions:
            1) IQAirConnectionError - if can't connect to airvisual, check IP
            2) WrongIQAirLoginOrPassword - if provided login/password is wrong, check credentials
            3) IQAirMeasurementsFileNotFoundOrWrong - it porbably means, airvisual has new firmware
               which isn't supported yet
        """
        file_data = {}
        logger.debug("Going to fetch last measurements from IQAir")
        try:
            raw_file_content = self._fetch_file('/latest_config_measurements.json')
            file_data = json.loads(raw_file_content)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise errors.IQAirMeasurementsFileNotFoundOrWrong(self._ip) from exc
        logger.debug("Fetched the following IQAir last measurements file content: %s", file_data)
        return file_data

    def _connect_to_iqair(self) -> SMBConnection:
        """
        Function connects to IQAIR. In case of network problems
        it makes few attempts to connect. Function can raise
        an exception 'WrongIQAirLoginOrPassword'. Or exception
        'IQAirConnectionError' if after N attempts(where N is 'CONNECTION_ATTEMPTS')
        connection has failed.

        function returns a connection which ALWAYS must be closed after usage
        """
        for connection_attempt in range(1, CONNECTION_ATTEMPTS + 1):
            try:
                connection = SMBConnection(self._login, self._password, 'iqair2mqtt', 'airvisual')
                connected = connection.connect(self._ip, timeout=CONNECTION_TIMEOUT)
                if not connected:
                    raise errors.WrongIQAirLoginOrPassword(self._ip)
                logger.debug(
                    "Connected to IQAir on %s",
                    self._ip
                )
                break
            except (ConnectionError, timeout) as exc:
                # we will retry connection
                if connection_attempt < CONNECTION_ATTEMPTS:
                    logger.warning(
                        "Can't connect to '%s', error: %s, will retry",
                        self._ip,
                        exc
                    )
                else:  # we've reached maximum number of retries, raise an exception
                    raise errors.IQAirConnectionError(self._ip) from exc
            else:
                if connection_attempt > 1:
                    logger.info(
                        "Connected to IQAir after %d attemps, check for network problems",
                        connection_attempt
                    )
        return connection

    def _fetch_file(self, file_path: str) -> str:
        """
        Return content of a file on airvisual shared drive.
        File path must be a full path with file name, for files
        in root folder use '/<FILENAME>'

        Will raise an aexception if 'FileNotFoundError' if filed wasn't found.
        In caise of connection issues you might see exceptions from '_connect_to_iqair'

        """
        temp_fh = tempfile.NamedTemporaryFile('w+b')
        connection = None
        result = ''
        try:
            connection = self._connect_to_iqair()
            res = connection.retrieveFile('airvisual', file_path, temp_fh)
            logger.debug(
                "Read %d bytes from file '%s' on iqair",
                res[1],
                file_path
            )
            temp_fh.seek(0)
            result = temp_fh.read().decode()
        except OperationFailure as exc:
            if exc.message.find('Unable to open file') != -1:
                raise FileNotFoundError(file_path) from exc
            raise  # if we have any other error
        finally:
            temp_fh.close()
            if connection is not None:
                connection.close()
        return result
