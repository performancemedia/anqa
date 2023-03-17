from typing import Any, Callable, get_type_hints

from fastapi import APIRouter

from .views.views import View


class InferringRouter(APIRouter):
    """
    Overrides the route decorator logic to use the annotated return type as the `response_model` if unspecified.
    """

    def add_api_route(
        self, path: str, endpoint: Callable[..., Any], **kwargs: Any
    ) -> None:
        if kwargs.get("response_model") is None:
            kwargs["response_model"] = get_type_hints(endpoint).get("return")
        return super().add_api_route(path, endpoint, **kwargs)


def register_view(router: APIRouter, view: View, prefix: str = ""):
    for route_params in view.get_api_actions(prefix):
        router.add_api_route(**route_params)


class ViewRouter(InferringRouter):
    register_view = register_view
