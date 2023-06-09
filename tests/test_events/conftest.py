import asyncio
from datetime import date
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from anqa.events import CloudEvent, Consumer, GenericConsumer, MessageService
from anqa.events.brokers.stub import StubBroker
from anqa.events.context import Context
from anqa.events.middleware import MessageMiddleware


@pytest_asyncio.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def middleware():
    class EmptyMiddleware(MessageMiddleware):
        pass

    return EmptyMiddleware()


@pytest.fixture
def broker(middleware):
    return StubBroker(middlewares=[middleware])


@pytest.fixture
def service(broker):
    return MessageService(name="test_service", broker=broker)


@pytest.fixture(scope="session")
def handler():
    async def example_handler(message: CloudEvent) -> int:
        assert isinstance(message, CloudEvent)
        return 42

    return example_handler


@pytest.fixture
def test_consumer(service, handler):
    consumer_name = "test_consumer"
    service.subscribe("test_topic", name=consumer_name)(handler)
    return service.consumer_group.consumers[consumer_name]


@pytest.fixture()
def generic_test_consumer(service) -> Consumer:
    generic_consumer_name = "test_generic_consumer"

    @service.subscribe("test_topic")
    class TestConsumer(GenericConsumer[CloudEvent]):
        name = generic_consumer_name

        async def process(self, message: CloudEvent, ctx: Context):
            return 42

    return service.consumer_group.consumers[generic_consumer_name]


@pytest.fixture()
def ce() -> CloudEvent:
    return CloudEvent(
        type="TestEvent",
        topic="test_topic",
        data={"today": date.today().isoformat(), "arr": [1, "2", 3.0]},
    )


@pytest_asyncio.fixture()
async def running_service(service: MessageService) -> AsyncGenerator:
    await service.start()
    yield service
    await service.stop()
