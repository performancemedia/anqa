from anqa.rest.factory import create_fastapi_app

from .api.router import api_router
from .settings import app_settings

app = create_fastapi_app(app_settings, routers=[api_router])
