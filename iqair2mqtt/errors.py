class ConfigVariableMissing(Exception):

    def __init__(self, variable):
        self.variable = variable
        message = f"Config variable '{self.variable}' not set"
        super().__init__(message)


class WrongIQAirLoginOrPassword(Exception):

    def __init__(self, iqair_ip):
        self.iqair_ip = iqair_ip
        message = f"Can't authenthiciate on IQAir '{self.iqair_ip}' using provided credentials"
        super().__init__(message)


class IQAirConnectionError(Exception):

    def __init__(self, iqair_ip):
        self.iqair_ip = iqair_ip
        super().__init__()

    def __str__(self):
        # self.__cause__ is empty on __init__
        message = f"Can't to connect IQAir on '{self.iqair_ip}' because '{self.__cause__}'"
        return message


class IQAirMeasurementsFileNotFoundOrWrong(Exception):

    def __init__(self, iqair_ip):
        self.iqair_ip = iqair_ip
        message = f"IQAir on '{self.iqair_ip}' doesn't have measuerements file, or file isn't json"
        super().__init__(message)
