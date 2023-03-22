from typing import Any, Callable, Dict, Type

from fastapi import Request
from starlette.status import HTTP_400_BAD_REQUEST

from anqa.core.exceptions import NotFound
from anqa.rest.errors.exceptions import APIError


class DetailViewMixin:
    detail_route: str = "/{id}"
    raise_on_none: bool = True
    request: Request
    get_name: Callable[..., str]

    @classmethod
    def get_detail_route(cls, action: str):
        return cls.detail_route

    def raise_not_found_error(self):
        raise NotFound(f"{self.get_name()} does not exist.")


class ErrorHandlerMixin:
    request: Request
    default_error_message = {
        "detail": "Something went wrong",
        "status": HTTP_400_BAD_REQUEST,
    }

    error_messages: Dict[Type[Exception], Dict[str, Any]] = {}

    def get_error_message(self, key: Type[Exception]):
        return self.error_messages.get(key, self.default_error_message)

    def handle_error(self, exc_type: Type[Exception], exc: Exception, **kwargs):
        kwargs.update(**self.get_error_message(exc_type))
        kwargs.setdefault("instance", self.request.url.path)
        kwargs.setdefault("title", exc_type.__name__)
        kwargs.setdefault("detail", str(exc))
        raise APIError(**kwargs)
