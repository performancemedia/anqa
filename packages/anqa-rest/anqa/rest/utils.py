from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import ErrorDetails

CORE_TO_MODELS_MAP: dict[str, type[ErrorDetails]] = {}


def register_for_exc(exc: type[Exception]):
    def wrapper(cls: type[ErrorDetails]) -> type[ErrorDetails]:

        CORE_TO_MODELS_MAP[exc.__name__] = cls
        return cls

    return wrapper


@lru_cache(maxsize=128, typed=True)
def find_model_for_exc(exc: str) -> type[ErrorDetails] | None:
    for e, m in CORE_TO_MODELS_MAP.items():
        if exc == e:
            return m
    return None
