import pytest
from mock import MagicMock, call

from iqair2mqtt import iqair, errors


class TestIqAir:
 
    test_login = "login"
    test_password = "password"
    test_ip = "ip"

    def test_initialization_success(self, monkeypatch):
        """
        Test succesfull class initialization, with connection tested
        """
        smb_connection = MagicMock(spec='smb.SMBConnection.SMBConnection')
        monkeypatch.setattr(iqair, 'SMBConnection', smb_connection)
        iqair.IQAir(self.test_ip, self.test_login, self.test_password)

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

        with pytest.raises(errors.WrongIQAirLoginOrPassword):
            iqair.IQAir(self.test_ip, self.test_login, self.test_password)
