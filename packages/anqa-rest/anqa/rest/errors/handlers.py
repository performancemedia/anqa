from fastapi import Request
from fastapi.responses import ORJSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from anqa.core.exceptions import CoreException

from .exceptions import APIError
from .models import ErrorDetails
from .utils import find_model_for_exc


def api_error_handler(request: Request, exc: APIError):
    return ORJSONResponse(
        status_code=exc.status,
        content=ErrorDetails(
            detail=exc.detail,
            title=exc.title,
            status=exc.status,
            instance=exc.instance or request.url.path,
        ).dict(),
    )


def core_exception_handler(request, exc: CoreException):
    model_cls = find_model_for_exc(type(exc).__name__)
    if model_cls:
        model = model_cls(detail=exc.detail, instance=request.url.path)
        return ORJSONResponse(status_code=model.status, content=model.dict())
    return ORJSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorDetails(
            title="Internal Server Error",
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.detail,
            instance=request.url.path,
        ).dict(),
    )


def server_error_handler(request, exc):
    return ORJSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorDetails(
            title="Internal Server Error",
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=type(exc).__name__,
            instance=request.url.path,
        ).dict(),
    )


def add_error_handlers(app):
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(CoreException, core_exception_handler)
    app.add_exception_handler(Exception, server_error_handler)
