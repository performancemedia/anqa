from __future__ import annotations

import asyncio
import functools
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .logger import LoggerMixin

M = TypeVar("M")


class _NoExc(Exception):
    pass


class AbstractDispatcher(ABC):
    @abstractmethod
    async def dispatch(self, full_event: str, *args, **kwargs):
        raise NotImplementedError

    async def dispatch_before(self, event: str, *args, **kwargs):
        await self.dispatch(f"before_{event}", *args, **kwargs)

    async def dispatch_after(self, event: str, *args, **kwargs):
        await self.dispatch(f"after_{event}", *args, **kwargs)


class MiddlewareDispatcherMixin(AbstractDispatcher, LoggerMixin, Generic[M]):
    reraise = _NoExc
    default_middlewares: list[M] = []

    def __init__(
        self, *, middlewares: list[M] | None = None, dispatch_prefix: str = "", **kwargs
    ):
        super.__init__(**kwargs)
        self.middlewares: list[M | type[M]] = []
        self._dispatch_prefix = dispatch_prefix
        for m in middlewares or self.default_middlewares:
            self.add_middleware(m)

    async def dispatch(self, full_event: str, *args, **kwargs):
        if self._dispatch_prefix:
            full_event = f"{self._dispatch_prefix}_{full_event}"
        for m in self.middlewares:
            try:
                await getattr(m, full_event)(self, *args, **kwargs)
            except self.reraise:
                raise
            except Exception as e:
                self.logger.error(f"Unhandled exception %s in middleware {m}", e)

    def add_middleware(self, middleware: M | type[M]) -> None:
        if isinstance(middleware, type):
            middleware = middleware()
        self.middlewares.append(middleware)

    def add_middlewares(self, middlewares: list[M | type[M]]) -> None:
        for m in middlewares:
            self.add_middleware(m)


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


class MiddlewareDispatcherProxy(AbstractDispatcher):
    pass_self: bool = True

    @property
    @abstractmethod
    def proxy_to(self) -> AbstractDispatcher:
        raise NotImplementedError

    async def dispatch(self, full_event: str, *args, **kwargs):
        if self.pass_self:
            args = (self, *args)
        await self.proxy_to.dispatch(full_event, *args, **kwargs)
