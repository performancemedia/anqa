from anqa.events import CloudEvent, GenericConsumer, MessageService
from anqa.events.brokers.stub import StubBroker
from anqa.events.context import Context
from anqa.events.types import T

broker = StubBroker()

service = MessageService(name="example-service", broker=broker)


@service.subscribe("example.topic")
class MyConsumer(GenericConsumer[CloudEvent]):
    # optionally replace `CloudEvent` with more specific class
    name = "example_consumer"

    async def process(self, message: T, ctx: Context):
        print(message)
