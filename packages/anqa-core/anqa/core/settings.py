from typing import Any, Generic, Type, TypeVar

from pydantic import BaseSettings as _BaseSettings
from pydantic import Extra, Field, validator
from pydantic.generics import GenericModel

from anqa.core.logger import setup_logging
from anqa.core.mixins.builder import AutoBuildableMixin
from anqa.core.utils.imports import ImportedType

C = TypeVar("C", bound=AutoBuildableMixin)


class BaseSettings(_BaseSettings):
    pass


class ObjectSettings(BaseSettings, GenericModel, Generic[C]):
    cls: ImportedType[Type[C]] = Field(..., env="CLASS")

    @classmethod
    def build(cls):
        settings = cls()
        return settings.cls.from_settings(settings)


def FromSettings(settings_cls: Type[ObjectSettings], **kwargs: Any):
    return Field(default_factory=settings_cls.build, **kwargs)


class AppSettings(BaseSettings):
    name: str = "app"
    version: str = "0.1.0"
    title: str
    log_level: str = "INFO"
    setup_logging: bool = Field(False, env="CONFIGURE_LOGGING")
    logger_format: str = "%(name) %(level) %(message)"

    @validator("title", always=True, pre=True, allow_reuse=True)
    def validate_tite(cls, v, values):
        return v or values.get("name", "app").title()

    @validator("setup_logging", allow_reuse=True, always=True)
    def enable_logger(cls, v, values):
        if v is True:
            setup_logging(level=values["log_level"], fmt=values["logger_format"])
        return v

    class Config:
        extra = Extra.allow
