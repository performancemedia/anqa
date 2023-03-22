from __future__ import annotations

from starlette.status import HTTP_400_BAD_REQUEST
from anqa.rest.errors.models import ErrorDetails

class APIError(Exception):
    def __init__(
        self,
        detail: str,
        title: str = "Bad Request",
        status: int = HTTP_400_BAD_REQUEST,
        instance: str | None = None,
    ):
        self.detail = detail
        self.status = status
        self.title = title or self.__doc__ or type(self).__name__
        self.instance = instance


def errors(*statuses: int):
    return {s: {"model": ErrorDetails} for s in statuses}
