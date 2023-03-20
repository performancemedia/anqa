from __future__ import annotations

from aioredis import Redis

from anqa.core.retries import retry
from anqa.events.middlewares.result import AbstractResultStoreMiddleware

from .broker import RedisBroker


class RedisResultMiddleware(AbstractResultStoreMiddleware):
    def __init__(self, namespace: str, **options):
        self.ttl = options.pop("ttl", 3600)
        super().__init__(namespace, **options)
        self._redis = None

    @property
    def redis(self) -> Redis:
        if self._redis is None:
            raise ValueError("MessageMiddleware not configured")
        return self._redis

    async def after_broker_connect(self, broker: RedisBroker) -> None:  # type: ignore[override]
        assert isinstance(broker, RedisBroker)
        self._redis = broker.redis

    @retry(max_retries=3, backoff=5)
    async def _set(self, key: str, value: bytes) -> None:
        await self.redis.set(f"{self.namespace}/{key}", value, ex=self.ttl)

    @retry(max_retries=3, backoff=5)
    async def _get(self, key: str) -> bytes | None:
        return await self.redis.get(f"{self.namespace}/{key}")
