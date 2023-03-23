from typing import TYPE_CHECKING, Any, Generic, Optional, Type, TypeVar

from pydantic import BaseSettings as _BaseSettings
from pydantic import Extra, Field, validator

from anqa.core.logger import setup_logging
from anqa.core.utils.imports import ImportedType

if TYPE_CHECKING:
    from anqa.core.mixins.builder import AutoBuildableMixin

C = TypeVar("C", bound="AutoBuildableMixin")


class BaseSettings(_BaseSettings):
    pass


class ObjectSettings(BaseSettings, Generic[C]):
    clazz: ImportedType[C] = Field(..., env="CLASS")

    @classmethod
    def build(cls):
        return cls.clazz.from_settings_class(cls)


def FromSettings(settings_cls: Type[ObjectSettings], **kwargs: Any):
    return Field(default_factory=settings_cls.build, **kwargs)


class AppSettings(BaseSettings):
    env: str = Field("dev", env="ENV")
    name: str = "app"
    version: str = "0.1.0"
    title: Optional[str]
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
