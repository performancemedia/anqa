from __future__ import annotations

import asyncio
import functools
from typing import Generic, TypeVar

from .logger import LoggerMixin

M = TypeVar("M")


class _NoExc(Exception):
    pass


class MiddlewareDispatcherMixin(LoggerMixin, Generic[M]):
    reraise = _NoExc
    default_middlewares: list[M] = []

    def __init__(self, *, middlewares: list[M] | None = None, **kwargs):
        super.__init__(**kwargs)
        self.middlewares = middlewares or self.default_middlewares

    async def _dispatch_event(self, full_event: str, *args, **kwargs):
        for m in self.middlewares:
            try:
                await getattr(m, full_event)(self, *args, **kwargs)
            except self.reraise:
                raise
            except Exception as e:
                self.logger.error(f"Unhandled exception %s in middleware {m}", e)

    async def dispatch_before(self, event: str, *args, **kwargs):
        await self._dispatch_event(f"before_{event}", *args, **kwargs)

    async def dispatch_after(self, event: str, *args, **kwargs):
        await self._dispatch_event(f"after_{event}", *args, **kwargs)


def dispatched(func):
    event = func.__name__

    @functools.wraps(func)
    async def wrapped(self: MiddlewareDispatcherMixin, *args, **kwargs):
        await self.dispatch_before(event, *args, **kwargs)
        res = await func(self, *args, **kwargs)
        await self.dispatch_after(event, *args, **kwargs)
        return res

    return wrapped


class MiddlewareDispatcherMeta(type):
    def __new__(mcs, name, bases, namespace):
        for k, v in namespace.items():
            if asyncio.iscoroutinefunction(v) and not k.startswith("_"):
                namespace[k] = dispatched(v)
        return super().__new__(mcs, name, bases, namespace)
