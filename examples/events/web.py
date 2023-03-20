from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse, Response

from anqa.events import CloudEvent, MessageService
from anqa.events.brokers.nats import (
    JetStreamBroker,
    NatsJetStreamResultMessageMiddleware,
)
from anqa.events.middlewares import HealthCheckMessageMiddleware

broker = JetStreamBroker(url="nats://localhost:4222")
kv = NatsJetStreamResultMessageMiddleware(namespace="test")

broker.add_middleware(HealthCheckMessageMiddleware)
broker.add_middleware(kv)

service = MessageService(name="example-service", broker=broker)


app = FastAPI()


@app.on_event("startup")
async def start_service():
    await service.start()


@app.on_event("shutdown")
async def stop_service():
    await service.stop()


@service.subscribe("events.topic", name="test_consumer", store_results=True)
async def handler(message: CloudEvent):
    print(f"Received Message {message.id} with data: {message.data}")
    return message.data


@app.post("/publish", status_code=202, response_model=CloudEvent)
async def publish_event(data: Any = Body(...)):
    event: CloudEvent[Any] = CloudEvent(topic="events.topic", data=data)
    await service.publish_message(event)
    return event


@app.get("/{consumer}/{key}")
async def get_result(consumer: str, key: str):
    res = await kv.get_result(service.name, consumer, key)
    if res is None:
        return Response(status_code=404, content="Key not found")
    return JSONResponse(content=res)
