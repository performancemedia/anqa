import asyncio
from abc import ABC, abstractmethod
from datetime import timedelta

from .abc.service import AbstractSideService
from .mixins import LoggerMixin
from .utils.dateutil import utc_now


class PeriodicService(AbstractSideService, LoggerMixin, ABC):
    """
    Periodic services are relatively lightweight maintenance routines that need to run periodically.
    This class makes it straightforward to design and integrate them. Users only need to
    define the `run_once` coroutine to describe the behavior of the service on each loop.
    """

    # The number of seconds the loop should repeat on when in operation
    loop_seconds_default = 600

    # shutdown flag for gracefully exiting the infinite loop
    is_running = True

    def __init__(self, loop_seconds: int = None):
        if loop_seconds:
            assert (
                loop_seconds > 0
            ), "Cannot create loop service with negative loop interval"
        self.loop_seconds = loop_seconds or self.loop_seconds_default
        self.name = type(self).__name__

    async def start(self, *args, **kwargs) -> None:
        """
        Run the service forever.
        """
        await asyncio.sleep(5)
        await self.on_startup()

        last_log = utc_now()

        while self.is_running:
            start_time = utc_now()

            try:
                await self.run_once()

            # if an error is raised, log and continue
            except Exception as exc:
                self.logger.error(f"Unexpected error: {repr(exc)}", exc_info=True)

            # next run is every "loop seconds" after each previous run started
            # note this might be in the past, leading to tight loops
            next_run = start_time + timedelta(seconds=self.loop_seconds)

            # if the loop interval is too short, warn
            now = utc_now()
            if next_run < now:
                self.logger.warning(
                    f"{self.name} took longer to run than its loop interval of {self.loop_seconds} seconds."
                )
                next_run = now

            # don't log more than once every 5 minutes
            if now - last_log > timedelta(minutes=5):
                self.logger.debug(
                    f"Heartbeat from {self.name}: next run at {next_run.replace(microsecond=0)}"
                )
                last_log = now

            await asyncio.sleep(max(0, (next_run - now).seconds))

        await self.on_shutdown()

    async def stop(self, *args, **kwargs) -> None:
        """
        Stops a running LoopService. This is a classmethod, so it will affect
        all instances of the class.
        """
        self.is_running = False

    @abstractmethod
    async def run_once(self) -> None:
        """
        Run the service once.
        Users should override this method.
        """
        raise NotImplementedError

    async def on_shutdown(self) -> None:
        """
        Any actions that must be performed on service shutdown
        """
        self.logger.info("Shutting down...")

    async def on_startup(self) -> None:
        """
        Hook for any actions before running
        """
        pass
