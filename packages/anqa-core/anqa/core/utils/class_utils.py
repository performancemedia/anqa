from __future__ import annotations

import inspect
from typing import Any


class SingletonMeta(type):
    _instances: dict[SingletonMeta, Any] = {}

    def __call__(cls: SingletonMeta, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    pass


def get_kwargs(cls, dict_obj):
    worker_args = set(inspect.signature(cls).parameters.keys())
    return {k: v for k, v in dict_obj.items() if k in worker_args}


def classproperty(func):
    """Decorator to use class properties"""
    return _ClassPropertyDescriptor(classmethod(func))


class _ClassPropertyDescriptor:
    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        return self.fget.__get__(obj, klass)()
