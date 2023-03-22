from __future__ import annotations

from collections import defaultdict

from anqa.events.middlewares.result import AbstractResultStoreMiddleware


class InMemoryResultStoreMiddleware(AbstractResultStoreMiddleware):
    def __init__(self, namespace: str, **options):
        super().__init__(namespace, **options)
        self._data: dict[str, dict[str, bytes]] = defaultdict(dict)

    async def _set(self, key: str, value: bytes) -> None:
        self._data[self.namespace][key] = value

    async def _get(self, key: str) -> bytes | None:
        return self._data[self.namespace].get(key)
