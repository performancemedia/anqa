import asyncio

from anqa.events import CloudEvent, MessageService
from anqa.events.brokers.stub import StubBroker


def test_service(service):
    assert isinstance(service, MessageService)
    assert isinstance(service.broker, StubBroker)
    assert service.name == "test_service"


async def test_service_scope(running_service: MessageService, ce):
    assert isinstance(running_service, MessageService)
    assert running_service.broker is not None
    await running_service.publish_message(ce)
    assert isinstance(running_service.broker, StubBroker)
    queue: asyncio.Queue = running_service.broker.topics[ce.topic]
    msg = await queue.get()
    queue.task_done()
    decoded = running_service.broker.encoder.decode(msg.data)
    ce2 = CloudEvent.parse_obj(decoded)
    assert ce.dict() == ce2.dict()
