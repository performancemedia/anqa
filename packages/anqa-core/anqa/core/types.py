from typing import TypeVar, Union
from uuid import UUID

from pydantic import constr

Str = constr(min_length=1, max_length=255, strip_whitespace=True)

ID = TypeVar("ID", bound=Union[int, str, UUID, bytes])
