from enum import Enum, EnumMeta


class BaseEnumMeta(EnumMeta):
    def __contains__(self, other):
        try:
            self(other)
        except ValueError:
            return False
        else:
            return True


class StrEnum(str, Enum, metaclass=BaseEnumMeta):
    pass


class PythonVersion(StrEnum):
    PY3_7 = "3.7"
    PY3_8 = "3.8"
    PY3_9 = "3.9"
    PY3_10 = "3.10"
    PY3_11 = "3.11"


class PackageEnum(StrEnum):
    core = "anqa-core"
    db = "anqa-db"
    events = "anqa-events"
    rest = "anqa-rest"


class CreateEnum(StrEnum):
    api = "api"
    app = "app"
    service = "service"
