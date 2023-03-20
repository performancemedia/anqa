from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class OnConflict(TypedDict, total=False):
    index_elements: Any | None
    index_where: Any | None
    set_: set[str] | None
    where: Any | None
