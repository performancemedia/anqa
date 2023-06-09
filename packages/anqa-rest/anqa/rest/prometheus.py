import os

from fastapi import FastAPI


def add_prometheus_middleware(app: FastAPI, endpoint: str = "/metrics", **kwargs):
    from starlette_exporter import PrometheusMiddleware, handle_metrics

    kwargs.setdefault("app_name", app.title.lower().replace(" ", "_"))
    kwargs.setdefault("skip_paths", ["/healthz", "/docs", "/openapi.json", "/metrics"])
    kwargs.setdefault("group_paths", True)
    kwargs.setdefault("labels", {"server_name": os.getenv("HOSTNAME")})
    kwargs.setdefault("always_use_int_status", True)
    app.add_middleware(PrometheusMiddleware, **kwargs)
    app.add_route(endpoint, handle_metrics)
