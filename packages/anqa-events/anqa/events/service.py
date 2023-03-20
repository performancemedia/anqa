from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from anqa.core.abc.service import AbstractSideService
from anqa.core.exceptions import ServiceUnavailable
from anqa.core.mixins import (
    AbstractDispatcher,
    AutoBuildableMixin,
    LoggerMixin,
    MiddlewareDispatcherProxy,
)

from .consumer import ConsumerGroup, ForwardResponse
from .context import Context
from .models import CloudEvent
from .settings import MessageServiceSettings

if TYPE_CHECKING:
    from .broker import Broker
    from .types import TagMeta


class MessageService(
    AbstractSideService,
    AutoBuildableMixin,
    MiddlewareDispatcherProxy,
    LoggerMixin,
):
    """Logical group of consumers. Provides group (queue) name and handles versioning"""

    default_settings_class = MessageServiceSettings

    @property
    def proxy_to(self) -> AbstractDispatcher:
        return self.broker

    def __init__(
        self,
        name: str,
        broker: Broker,
        title: str | None = None,
        version: str = "0.1.0",
        description: str = "",
        tags_metadata: list[TagMeta] | None = None,
        consumer_groups=None,
        ctx: Context | None = None,
        **kwargs,
    ):

        super().__init__(**kwargs)
        self.name = name
        self.broker = broker
        self.title = title or name.title()
        self.version = version
        self.description = description
        self.tags_metadata = tags_metadata or []

        self.consumer_group = ConsumerGroup()
        if consumer_groups:
            for cg in consumer_groups:
                self.add_consumer_group(cg)
        self.ctx = ctx or Context()
        self.ctx.update({"service": self})

    def subscribe(
        self,
        topic: str,
        *,
        name: str | None = None,
        timeout: int = 240,
        dynamic: bool = False,
        forward_response: ForwardResponse | None = None,
        **options,
    ):
        return self.consumer_group.subscribe(
            topic=topic,
            name=name,
            timeout=timeout,
            dynamic=dynamic,
            forward_response=forward_response,
            **options,
        )

    def add_consumer_group(self, consumer_group: ConsumerGroup) -> None:
        self.consumer_group.add_consumer_group(consumer_group)

    async def publish(
        self,
        topic: str,
        data: Any | None = None,
        type_: type[CloudEvent] | str = "CloudEvent",
        **kwargs,
    ):
        kwargs.setdefault("source", self.name)
        return await self.broker.publish(topic, data, type_, **kwargs)

    @property
    def consumers(self):
        return self.consumer_group.consumers.values()

    async def publish_message(self, message: CloudEvent, **kwargs):
        if not message.source:
            message.source = self.name
        return await self.broker.publish_message(message, **kwargs)

    async def start(self):
        await self.broker.connect()
        await self.dispatch_before("service_start")
        for consumer in self.consumers:
            asyncio.create_task(self.broker.start_consumer(self, consumer))
        await self.dispatch_after("service_start")

    async def stop(self, *args, **kwargs):
        await self.dispatch_before("service_stop")
        await self.broker.disconnect()
        await self.dispatch_after("service_stop")

    def endpoint_definitions(self):
        endpoints = []
        from .asyncapi.generator import get_async_api_spec
        from .asyncapi.models import AsyncAPI

        spec = get_async_api_spec(self)

        def get_asyncapi_spec():
            """Return service Async API specification"""
            return spec

        endpoints.append(
            {
                "response_model": AsyncAPI,
                "methods": ["GET"],
                "endpoint": get_asyncapi_spec,
                "path": "/asyncapi.json",
            }
        )
        for m in self.broker.middlewares:
            if hasattr(m, "get_health_status") and callable(m.get_health_status):  # type: ignore

                def get_health_status():
                    """Return get broker connection status"""
                    status = m.get_health_status()
                    if status:
                        return {"status": "ok"}
                    raise ServiceUnavailable("Connection error")

                endpoints.append(
                    {
                        "response_model": ...,
                        "methods": ["GET"],
                        "endpoint": get_health_status,
                        "path": "/healthz",
                    }
                )
                break
        return endpoints
