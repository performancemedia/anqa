import asyncio

from pydantic import BaseModel

from anqa.events import CloudEvent, MessageMiddleware, MessageService
from anqa.events.asyncapi.registry import publishes
from anqa.events.brokers.nats.broker import JetStreamBroker

broker = JetStreamBroker(url="nats://localhost:4222")

service = MessageService(name="example-service", version="1.0", broker=broker)


class MyData(BaseModel):
    """Main data for service"""

    counter: int
    info: str


@publishes("test.topic")
class MyEvent(CloudEvent[MyData]):
    """Some custom event"""


class SendMessageMiddleware(MessageMiddleware):
    async def after_service_start(self, broker, service: MessageService):
        self.logger.info(f"After service start, running with {broker}")
        await asyncio.sleep(5)
        for i in range(100):
            await broker.publish(
                "test.topic", type_=MyEvent, data={"counter": i, "info": "default"}
            )
        self.logger.info("Published event(s)")


broker.add_middleware(SendMessageMiddleware())


@service.subscribe("test.topic")
async def example_run(message: MyEvent):
    """Consumer for processing MyEvent(s)"""
    print(f"Received Message {message.id} with data: {message.data}")
