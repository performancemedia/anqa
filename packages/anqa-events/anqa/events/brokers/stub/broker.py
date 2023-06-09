from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from anqa.events.broker import Broker
from anqa.events.middleware import MessageMiddleware

if TYPE_CHECKING:
    from anqa.events import CloudEvent, Consumer, MessageService
    from anqa.events.types import Encoder


@dataclass
class Message:
    data: bytes
    queue: asyncio.Queue


class StubBroker(Broker[Message]):
    """This is in-memory implementation of a broker class, mainly designed for testing."""

    protocol = "in-memory"

    def __init__(
        self,
        *,
        encoder: Encoder | None = None,
        middlewares: list[MessageMiddleware] | None = None,
        **options: Any,
    ) -> None:
        super().__init__(encoder=encoder, middlewares=middlewares, **options)
        self.topics: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        self._stopped = False

    def parse_incoming_message(self, message: Message) -> Any:
        return self.encoder.decode(message.data)

    async def _disconnect(self) -> None:
        self._stopped = True

    async def _start_consumer(self, service: MessageService, consumer: Consumer):
        queue = self.topics[consumer.topic]
        handler = self.get_handler(service, consumer)
        while not self._stopped:
            message = await queue.get()
            await handler(message)

    async def _connect(self) -> None:
        pass

    async def _publish(self, message: CloudEvent, **_) -> None:
        queue = self.topics[message.topic]
        data = self.encoder.encode(message.dict())
        msg = Message(data=data, queue=queue)
        await queue.put(msg)

    async def _ack(self, message: Message) -> None:
        message.queue.task_done()

    async def _nack(self, message: Message, delay: int | None = None) -> None:

        if delay:
            await asyncio.sleep(delay)
        await message.queue.put(message)

    def is_connected(self) -> bool:
        return True
