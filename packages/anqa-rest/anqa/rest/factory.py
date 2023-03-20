from __future__ import annotations

import functools
from typing import Any

from fastapi import FastAPI

from anqa.core.abc.service import AbstractSideService

from ..core.utils.class_utils import get_kwargs
from .errors.handlers import add_error_handlers
from .openapi import simplify_operation_ids
from .prometheus import add_prometheus_middleware
from .settings import ApiSettings


def add_side_service(app: FastAPI, service: AbstractSideService):
    app.on_event("startup")(service.start)
    app.on_event("shutdown")(service.stop)

    if hasattr(service, "endpoint_definitions"):
        for e in service.endpoint_definitions:
            app.add_api_route(**e)


@functools.cache
def create_fastapi_app(
    settings: ApiSettings | type[ApiSettings] = ApiSettings, **kwargs: Any
) -> FastAPI:
    if isinstance(settings, type):
        settings = settings(**kwargs)
    kw = {**settings.dict(), **kwargs}
    filtered_kw = get_kwargs(FastAPI, kw)
    app = FastAPI(**filtered_kw)
    add_error_handlers(app)
    add_prometheus_middleware(app)
    for side_service in settings.side_services:
        add_side_service(app, side_service)
    for router in settings.routers:
        app.include_router(router)
    app.on_event("startup")(simplify_operation_ids)
    return app
