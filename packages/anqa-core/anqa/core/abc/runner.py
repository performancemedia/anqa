import asyncio
from abc import ABC, abstractmethod
from typing import Sequence

from .service import AbstractSideService


class AbstractRunner(ABC):
    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError


class ServiceRunner(AbstractRunner):
    def __init__(self, services: Sequence[AbstractSideService]):
        self.services = services

    def run(self, *args, use_uvloop: bool = True, **kwargs) -> None:
        import aiorun

        aiorun.run(
            self._run(), shutdown_callback=self._stop, use_uvloop=use_uvloop, **kwargs
        )

    async def _run(self):
        await asyncio.gather(*[s.start() for s in self.services])

    async def _stop(self, *args, **kwargs):
        await asyncio.gather(*[s.stop() for s in self.services])
