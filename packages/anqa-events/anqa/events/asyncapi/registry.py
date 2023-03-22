from __future__ import annotations

from anqa.events.models import CloudEvent

from .models import PublishInfo

PUBLISH_REGISTRY: dict[str, PublishInfo] = {}


def publishes(topic: str, **kwargs):
    def wrapper(cls: type[CloudEvent]) -> type[CloudEvent]:
        PUBLISH_REGISTRY[cls.__name__] = PublishInfo(
            topic=topic, event_type=cls, kwargs=kwargs
        )
        return cls

    return wrapper
