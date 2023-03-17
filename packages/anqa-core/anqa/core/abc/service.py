from abc import ABC, abstractmethod


class AbstractSideService(ABC):
    @abstractmethod
    async def start(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def stop(self, *args, **kwargs) -> None:
        raise NotImplementedError
