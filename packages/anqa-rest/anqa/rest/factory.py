from fastapi import FastAPI

from .error_handlers import add_error_handlers
from .openapi import simplify_operation_ids
from .prometheus import add_prometheus_middleware


def add_side_service(app, service):
    app.on_event("startup")(service.start)
    app.on_event("shutdown")(service.stop)

    if hasattr(service, "endpoint_definitions"):
        for e in service.endpoint_definitions:
            app.add_api_route(**e)


def create_fastapi_app(*args, side_services=None, **kwargs) -> FastAPI:
    app = FastAPI(*args, **kwargs)
    add_error_handlers(app)
    add_prometheus_middleware(app)
    for side_service in side_services or []:
        add_side_service(app, side_service)
    app.on_event("startup")(simplify_operation_ids)
    return app
