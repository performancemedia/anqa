from abc import ABC, abstractmethod


class AbstractEventBus(ABC):
    @abstractmethod
    async def publish(self, event, *args, **kwargs):
        raise NotImplementedError
