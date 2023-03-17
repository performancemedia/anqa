class CoreException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class ConfigurationError(CoreException):
    pass


class NotFound(CoreException):
    pass


class Duplicate(CoreException):
    pass
