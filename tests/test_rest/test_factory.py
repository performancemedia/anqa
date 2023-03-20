from fastapi import FastAPI

from anqa.rest.factory import add_prometheus_middleware, create_fastapi_app


def test_add_prometheus_middleware(fastapi_app):
    add_prometheus_middleware(fastapi_app)
    assert any([route.path == "/metrics" for route in fastapi_app.routes])


def test_create_fastapi_app():
    app = create_fastapi_app()
    assert isinstance(app, FastAPI)
    assert app.title == "App"
