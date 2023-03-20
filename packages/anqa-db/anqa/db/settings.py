from pydantic import Field, PyObject

from anqa.core.settings import BaseSettings
from anqa.core.utils.json import json_dumps, json_loads


class DatabaseSettings(BaseSettings):
    url: str = Field("postgres://localhost:5432", env="URL")
    pool_size: int = Field(10, env="POOL_SIZE")
    echo_pool: bool = Field(True, env="ECHO_POOL")
    max_overflow: int = Field(0, env="MAX_OVERFLOW")
    pool_recycle: int = Field(3600, env="POOL_RECYCLE")
    poolclass: PyObject = "sqlalchemy.AsyncAdaptedQueuePool"
    json_serializer = json_dumps
    json_deserializer = json_loads

    class Config:
        env_prefix = "DATABASE_"
