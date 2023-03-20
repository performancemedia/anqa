from typing import Optional

from pydantic import Field
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from anqa.core.exceptions import Duplicate, NotFound, ServiceUnavailable
from anqa.core.schema import BaseSchema

from .utils import register_for_exc


class ErrorDetails(BaseSchema):
    """
    Base Model for https://www.rfc-editor.org/rfc/rfc7807
    """

    type: str = Field(
        "about:blank",
        description="Error type",
    )
    title: Optional[str] = Field("Bad Request", description="Error title")
    status: int = Field(HTTP_400_BAD_REQUEST, description="Error status")
    detail: str = Field(
        ...,
        description="Error detail",
    )
    instance: Optional[str] = Field(None, description="Requested instance")

    @classmethod
    def get_status(cls) -> int:
        return cls.__fields__["status"].default


@register_for_exc(NotFound)
class NotFoundAPIError(ErrorDetails):
    title: str = Field("Not Found", const=True)
    status: int = Field(HTTP_404_NOT_FOUND, const=True)


@register_for_exc(Duplicate)
class ConflictAPIError(ErrorDetails):
    title: str = Field("Conflict", const=True)
    status: int = Field(HTTP_409_CONFLICT, const=True)


@register_for_exc(ServiceUnavailable)
class ServiceUnavailableAPIError(ErrorDetails):
    title: str = Field("Service Unavailable", const=True)
    status: int = Field(HTTP_503_SERVICE_UNAVAILABLE, const=True)
