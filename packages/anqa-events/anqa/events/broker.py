from __future__ import annotations

import asyncio
import functools
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generic, cast

import async_timeout
from pydantic import ValidationError

from anqa.core.logger import reset_logger_context, update_logger_context
from anqa.core.mixins.builder import AutoBuildableMixin
from anqa.core.mixins.middleware import MiddlewareDispatcherMixin, dispatched
from anqa.core.utils import str_uuid

from .consumer import Consumer, ConsumerGroup
from .exceptions import DecodeError, Fail, Skip
from .message import RawMessageProxy
from .middleware import MessageMiddleware
from .models import CloudEvent
from .settings import BrokerSettings
from .types import Encoder, RawMessageT

if TYPE_CHECKING:
    from .service import MessageService


class AbstractBroker(
    Generic[RawMessageT],
    AutoBuildableMixin,
    MiddlewareDispatcherMixin[MessageMiddleware],
    ABC,
):
    @abstractmethod
    def parse_incoming_message(self, message: RawMessageT) -> Any:
        raise NotImplementedError

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Return broker connection status"""
        raise NotImplementedError

    @abstractmethod
    async def _publish(self, message: CloudEvent, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _start_consumer(
        self, service: MessageService, consumer: Consumer
    ) -> None:
        raise NotImplementedError

    async def _ack(self, message: RawMessageT) -> None:
        """Empty default implementation for backends that do not support explicit ack"""

    async def _nack(self, message: RawMessageT, delay: int | None = None) -> None:
        """Same as for ._ack()"""


class Broker(AbstractBroker[RawMessageT], Generic[RawMessageT], ABC):
    """Base broker class
    :param description: Broker (Server) Description
    :param encoder: Encoder (Serializer) class
    :param middlewares: Optional list of middlewares
    """

    default_settings_class = BrokerSettings
    reraise = Skip
    protocol: str

    def __init__(
        self,
        *,
        description: str | None = None,
        encoder: Encoder | None = None,
        middlewares: list[MessageMiddleware] | None = None,
        **kwargs,
    ) -> None:

        super().__init__(middlewares=middlewares, **kwargs)
        if encoder is None:
            from .encoders import get_default_encoder

            encoder = get_default_encoder()
        self.description = description or type(self).__doc__
        self.encoder = encoder
        self.consumer_group = ConsumerGroup()
        self._lock = asyncio.Lock()
        self._stopped = True

    def __repr__(self):
        return type(self).__name__

    def get_handler(
        self, service: MessageService, consumer: Consumer
    ) -> Callable[[RawMessageT], Awaitable[Any | None]]:
        async def handler(raw_message: RawMessageT) -> None:
            exc: Exception | None = None
            result: Any = None
            try:
                raw_message = cast(RawMessageT, RawMessageProxy(raw_message))
                parsed = self.parse_incoming_message(raw_message)
                message = consumer.validate_message(parsed)
                message.raw = raw_message
                token = update_logger_context(message.context)

            except (DecodeError, ValidationError) as e:
                self.logger.exception(
                    "Parsing error Decode/Validation error", exc_info=e
                )
                await self._ack(raw_message)
                return

            try:
                await self.dispatch_before(
                    "process_message", service, consumer, message
                )
            except Skip:
                self.logger.info(f"Skipped message {message.id}")
                await self.dispatch_after("skip_message", service, consumer, message)
                await self.ack(service, consumer, raw_message)
                return
            try:
                async with async_timeout.timeout(consumer.timeout):
                    self.logger.info(f"Running consumer {consumer.name}")
                    result = await consumer.process(message, service.ctx)
                if consumer.forward_response and result is not None:
                    await self.publish_message(
                        CloudEvent(
                            type=consumer.forward_response.as_type,
                            topic=consumer.forward_response.topic,
                            data=result,
                            trace_id=message.trace_id,
                            source=service.name,
                        )
                    )
            except Exception as e:
                self.logger.error(f"Exception in {consumer.name} {e}")
                exc = e
            finally:
                if isinstance(exc, Fail):
                    self.logger.error(f"Failing message due to {exc}")
                    raw_message.fail()
                    await self.ack(service, consumer, raw_message)
                    return
                await self.dispatch_after(
                    "process_message", service, consumer, message, result, exc
                )
                await self.ack(service, consumer, raw_message)
                reset_logger_context(token)

        return handler

    async def ack(
        self, service: MessageService, consumer: Consumer, message: RawMessageT
    ) -> None:
        await self.dispatch_before("ack", service, consumer, message)
        await self._ack(message)
        await self.dispatch_after("ack", service, consumer, message)

    async def nack(
        self,
        service: MessageService,
        consumer: Consumer,
        message: RawMessageT,
        delay: int | None = None,
    ) -> None:
        await self.dispatch_after(
            "nack",
            service,
            consumer,
            message,
        )
        await self._nack(message, delay)
        await self.dispatch_after(
            "nack",
            service,
            consumer,
            message,
        )

    @dispatched
    async def broker_connect(self):
        await self.connect()

    async def connect(self) -> None:
        async with self._lock:
            if self._stopped:
                await self.dispatch_before("broker_connect")
                await self._connect()
                self._stopped = False
                await self.dispatch_after("broker_connect")

    async def disconnect(self) -> None:
        async with self._lock:
            if not self._stopped:
                await self.dispatch_before("broker_disconnect")
                await self._disconnect()
                self._stopped = True
                await self.dispatch_after("broker_disconnect")

    async def publish_message(self, message: CloudEvent, **kwargs: Any) -> None:
        """
        :param message: Cloud event object to send
        :param kwargs: Additional params passed to broker._publish
        :rtype: None
        """
        await self.dispatch_before("publish", message)
        await self._publish(message, **kwargs)
        await self.dispatch_after("publish", message)

    async def publish(
        self,
        topic: str,
        data: Any | None = None,
        type_: type[CloudEvent] | str = "CloudEvent",
        source: str = "",
        trace_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Publish message to broker
        :param trace_id:
        :param topic: Topic to publish data
        :param data: Message content
        :param type_: Event type, name or class
        :param source: message sender (service/app name)
        :param kwargs: additional params passed to underlying broker implementation, such as headers
        :rtype: None
        """

        if isinstance(type_, str):
            cls = functools.partial(CloudEvent, type=type_)
        else:
            cls = type_  # type: ignore
        if trace_id is None:
            trace_id = str_uuid()
            update_logger_context({"trace_id": trace_id})

        trace_id = trace_id or str_uuid()
        message: CloudEvent = cls(
            content_type=self.encoder.CONTENT_TYPE,
            topic=topic,
            data=data,
            source=source,
            trace_id=trace_id,
        )
        await self.publish_message(message, **kwargs)

    async def start_consumer(self, service: MessageService, consumer: Consumer):
        await self.dispatch_before("consumer_start", service, consumer)
        await self._start_consumer(service, consumer)
        await self.dispatch_after("consumer_start", service, consumer)
