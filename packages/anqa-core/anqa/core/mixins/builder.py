from __future__ import annotations

from typing import Any, Generic, TypeVar

from anqa.core.settings import BaseSettings
from anqa.core.utils.class_utils import get_kwargs

S = TypeVar("S", bound=BaseSettings)


class AutoBuildableMixin(Generic[S]):
    default_settings_class: S | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_settings(cls, settings: S):
        kw = get_kwargs(cls, settings.dict())
        return cls(**kw)

    @classmethod
    def from_settings_class(cls, settings_cls: type[S] = None, **kwargs: Any):
        settings_cls = settings_cls or cls.default_settings_class
        if not settings_cls:
            raise ValueError("Settings class not found")
        settings = settings_cls(**kwargs)
        return cls.from_settings(settings)
