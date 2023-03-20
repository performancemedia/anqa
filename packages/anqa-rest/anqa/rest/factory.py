from __future__ import annotations

import functools
from typing import Any

from fastapi import FastAPI

from anqa.core.abc.service import AbstractSideService

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
    settings_cls: type[ApiSettings] = ApiSettings, **kwargs: Any
) -> FastAPI:
    settings = settings_cls(**kwargs)
    app = FastAPI(**settings.dict(exclude={"side_services"}))
    add_error_handlers(app)
    add_prometheus_middleware(app)
    for side_service in settings.side_services:
        add_side_service(app, side_service)
    for router in settings.routers:
        app.include_router(router)
    app.on_event("startup")(simplify_operation_ids)
    return app
