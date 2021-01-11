class Config:

    def __init__(self, config_file_path: str):
        pass

    @property
    def iqair_ip(self) -> str:
        return '127.0.0.1'

    @property
    def iqair_login(self) -> str:
        return 'iqair_login'

    @property
    def iqair_password(self) -> str:
        return 'iqair_password'

    @property
    def mqtt_hostname(self) -> str:
        return 'localhost'

    @property
    def mqtt_login(self) -> str:
        return 'mqtt_login'

    @property
    def mqtt_password(self) -> str:
        return 'mqtt_password'

    @property
    def update_interal(self) -> int:
        return 3
