from __future__ import annotations

from collections import UserDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anqa.events import Broker, CloudEvent, MessageService


class Context(UserDict):
    @property
    def service(self) -> MessageService:
        return self["service"]

    @property
    def broker(self) -> Broker:
        return self.service.broker

    async def publish(self, *args, **kwargs):
        return await self.service.publish(*args, **kwargs)

    async def publish_message(self, message: CloudEvent, **kwargs):
        return await self.service.publish_message(message, **kwargs)
