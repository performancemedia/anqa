from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from anqa.core.types import ID

E = TypeVar("E")


class AbstractRepository(ABC, Generic[E]):
    @abstractmethod
    async def add(self, entity: E) -> E:
        raise NotImplementedError

    @abstractmethod
    async def get(self, pk: ID) -> E | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, *args, **kwargs) -> E | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list(self, *args, **kwargs) -> list[E]:
        raise NotImplementedError
