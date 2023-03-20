from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from anqa.core.utils.functools import to_async
from anqa.events.middleware import MessageMiddleware

if TYPE_CHECKING:
    from anqa.events import Broker, CloudEvent, Consumer, MessageService


class ErrorHandlerMessageMiddleware(MessageMiddleware):
    def __init__(self, errors: type[Exception] | tuple[type[Exception]], callback):
        if not asyncio.iscoroutinefunction(callback):
            callback = to_async(callback)
        self.cb = callback
        self.exc = errors

    async def after_process_message(
        self,
        broker: Broker,
        service: MessageService,
        consumer: Consumer,
        message: CloudEvent,
        result: Any | None = None,
        exc: Exception | None = None,
    ):
        if exc and isinstance(exc, self.exc):
            await self.cb(message, exc)
