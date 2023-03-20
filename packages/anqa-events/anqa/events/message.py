from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anqa.events import RawMessage


class RawMessageProxy:
    def __init__(self, message: RawMessage):
        self._message = message
        self._failed = False

    def __getattr__(self, item):
        return getattr(self._message, item)

    def fail(self) -> None:
        self._failed = True

    @property
    def failed(self) -> bool:
        return self._failed
