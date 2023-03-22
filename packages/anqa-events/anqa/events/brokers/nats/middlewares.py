from __future__ import annotations

from typing import TYPE_CHECKING

from nats.js.errors import KeyNotFoundError
from nats.js.kv import KeyValue

from anqa.core.retries import retry
from anqa.events.middlewares.result import AbstractResultStoreMiddleware

if TYPE_CHECKING:
    from .broker import JetStreamBroker


class NatsJetStreamResultMessageMiddleware(AbstractResultStoreMiddleware):
    def __init__(self, namespace: str, **options):
        super().__init__(namespace, **options)
        self._kv = None

    @retry(max_retries=3, backoff=5)
    async def _set(self, key: str, value: bytes) -> None:
        await self.kv.put(key, value)

    @retry(max_retries=3, backoff=5)
    async def _get(self, key: str) -> bytes | None:
        try:
            return await self.kv.get(key)
        except KeyNotFoundError:
            self.logger.warning(f"Key {key} not found")
            return None

    @property
    def kv(self) -> KeyValue:
        if self._kv is None:
            raise ValueError("MessageMiddleware not configured")
        return self._kv

    async def after_broker_connect(self, broker: JetStreamBroker) -> None:
        if isinstance(broker, JetStreamBroker):
            self._kv = await broker.js.create_key_value(
                bucket=self.namespace, **self.options
            )
        else:
            self.logger.warning("Expected JetstreamBroker, got %s", type(broker))
