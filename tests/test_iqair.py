import pytest
from socket import timeout
from mock import MagicMock, call

from smb.smb_structs import OperationFailure

from iqair2mqtt import iqair, errors


class TestIqAir:

    test_login = "login"
    test_password = "password"
    test_ip = "ip"

    def test_noop_success(self, monkeypatch):
        """
        Test succesfull class initialization, with connection tested
        """
        smb_connection = MagicMock(spec='smb.SMBConnection.SMBConnection')
        monkeypatch.setattr(iqair, 'SMBConnection', smb_connection)
        iqair_instance = iqair.IQAir(self.test_ip, self.test_login, self.test_password)

        iqair_instance.noop()

        # smb.SMBConnection.SMBConnection(...)  call testing
        assert smb_connection.call_args_list \
            == [call(self.test_login, self.test_password, "iqair2mqtt", "airvisual")]

        # smb.SMBConnection.SMBConnection(...).connect call testing
        assert smb_connection.return_value.connect.call_args_list \
            == [call(self.test_ip, timeout=iqair.CONNECTION_TIMEOUT)]

    def test_initialization_wrong_credentials(self, monkeypatch):
        """
        Test succesfull class initialization, with connection tested
        """
        smb_connection = MagicMock(spec='smb.SMBConnection.SMBConnection')
        monkeypatch.setattr(iqair, 'SMBConnection', smb_connection)

        smb_connection.return_value.connect.return_value = False
        iqair_instance = iqair.IQAir(self.test_ip, self.test_login, self.test_password)

        with pytest.raises(errors.WrongIQAirLoginOrPassword):
            iqair_instance.noop()

    def test_retry_connection_on_error_with_success(self, monkeypatch):
        """
        We check that in case of network problems we try to reconnect N times, with success
        in the end
        """
        smb_connection = MagicMock(spec='smb.SMBConnection.SMBConnection')
        monkeypatch.setattr(iqair, 'SMBConnection', smb_connection)

        def connection_error_first_n_tries(n: int):
            """
            Fail first 'n' connection attempts
            """
            attempts = 1

            def mock_connection_error(*args, **kwargs):
                nonlocal attempts
                if attempts <= n:
                    attempts += 1
                else:
                    return True
                raise ConnectionError("test error")
            return mock_connection_error

        smb_connection.return_value.connect.side_effect = connection_error_first_n_tries(iqair.CONNECTION_ATTEMPTS - 1)
        iqair_instance = iqair.IQAir(self.test_ip, self.test_login, self.test_password)

        iqair_instance.noop()

    def test_retry_connection_on_error_without_success(self, monkeypatch):
        """
        Here we test that after N attempts we stop trying to reconnect and raise an error
        """
        smb_connection = MagicMock(spec='smb.SMBConnection.SMBConnection')
        monkeypatch.setattr(iqair, 'SMBConnection', smb_connection)

        smb_connection.return_value.connect.side_effect = ConnectionError("test error")
        iqair_instance = iqair.IQAir(self.test_ip, self.test_login, self.test_password)

        with pytest.raises(errors.IQAirConnectionError):
            iqair_instance.noop()

    def test_get_last_measurements_success(self, monkeypatch):
        smb_connection = MagicMock(spec='smb.SMBConnection.SMBConnection')
        monkeypatch.setattr(iqair, 'SMBConnection', smb_connection)

        def mock_retrieve_file(share, file_path, temp_fh):
            # verify we fetch file from correct shared folder
            assert share == 'airvisual'
            # verify we use correct file path
            assert file_path == '/latest_config_measurements.json'
            temp_fh.write(b'{"test_key": "test_value"}')
            return (None, 10)

        smb_connection.return_value.retrieveFile.side_effect = mock_retrieve_file

        iqair_instance = iqair.IQAir(self.test_ip, self.test_login, self.test_password)

        result = iqair_instance.get_latest_measurements()

        assert {"test_key": "test_value"} == result

    def test_get_last_measurements_no_file_found(self, monkeypatch):
        smb_connection = MagicMock(spec='smb.SMBConnection.SMBConnection')
        monkeypatch.setattr(iqair, 'SMBConnection', smb_connection)

        smb_connection.return_value.retrieveFile.side_effect = OperationFailure("Unable to open file", "")

        iqair_instance = iqair.IQAir(self.test_ip, self.test_login, self.test_password)

        with pytest.raises(errors.IQAirMeasurementsFileNotFoundOrWrong):
            iqair_instance.get_latest_measurements()

    def test_get_last_measurements_wrong_file(self, monkeypatch):
        smb_connection = MagicMock(spec='smb.SMBConnection.SMBConnection')
        monkeypatch.setattr(iqair, 'SMBConnection', smb_connection)

        def mock_retrieve_broken_file(_, __, temp_fh):
            temp_fh.write(b'not_a_json')
            return (None, 10)

        smb_connection.return_value.retrieveFile.side_effect = mock_retrieve_broken_file

        iqair_instance = iqair.IQAir(self.test_ip, self.test_login, self.test_password)

        with pytest.raises(errors.IQAirMeasurementsFileNotFoundOrWrong):
            iqair_instance.get_latest_measurements()
