class ConfigVariableMissing(Exception):

    def __init__(self, variable):
        self.variable = variable
        message = f"Config variable '{self.variable}' not set"
        super().__init__(message)
