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


class Python(StrEnum):
    v38 = "3.8"
    v39 = "3.9"
    v3_10 = "3.10"
    v3_11 = "3.11"


class PackageEnum(StrEnum):
    core = "core"
    db = "db"
    events = "events"
    rest = "rest"


class CreateEnum(StrEnum):
    api = "api"
    app = "app"
    service = "service"
