from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from anqa.events.middleware import MessageMiddleware

if TYPE_CHECKING:
    from anqa.events import Broker, CloudEvent, Consumer, MessageService


def default_key_generator(
    service_name: str, consumer_name: str, message_id: str
) -> str:
    return ".".join([service_name, consumer_name, message_id])


class AbstractResultStoreMiddleware(MessageMiddleware, ABC):
    def __init__(
        self,
        namespace: str,
        store_exceptions: bool = False,
        encoder=None,
        key_generator=default_key_generator,
        **options,
    ):
        self.namespace = namespace
        self.store_exceptions = store_exceptions
        self.key_generator = key_generator
        if encoder is None:
            from anqa.events.encoders import get_default_encoder

            encoder = get_default_encoder()
        self.encoder = encoder
        self.options = options

    @abstractmethod
    async def _set(self, key: str, value: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _get(self, key: str) -> bytes | None:
        raise NotImplementedError

    async def after_process_message(
        self,
        broker: Broker,
        service: MessageService,
        consumer: Consumer,
        message: CloudEvent,
        result: Any | None = None,
        exc: Exception | None = None,
    ) -> None:

        if consumer.options.get("store_results") is True:
            result_key = self.key_generator(service.name, consumer.name, message.id)
            if exc is None:
                data = self.encoder.encode(result)
                await self._set(result_key, data)
            elif exc and self.store_exceptions:
                data = self.encoder.encode(
                    {"type": type(exc).__name__, "detail": str(exc)}
                )
                await self._set(result_key, data)

    async def get_result(self, service_name: str, consumer_name: str, message_id: str):
        result_key = self.key_generator(service_name, consumer_name, message_id)
        res = await self._get(result_key)
        if res:
            return self.encoder.decode(res)
