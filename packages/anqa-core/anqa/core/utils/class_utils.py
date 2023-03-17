from __future__ import annotations

from typing import Any


class Singleton(type):
    _instances: dict[Singleton, Any] = {}

    def __call__(cls: Singleton, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def get(cls: Singleton) -> Any | None:
        return cls._instances.get(cls)


def classproperty(func):
    """Decorator to use class properties"""
    return _ClassPropertyDescriptor(classmethod(func))


class _ClassPropertyDescriptor:
    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        return self.fget.__get__(obj, klass)()
