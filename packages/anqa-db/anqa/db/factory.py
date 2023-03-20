from __future__ import annotations

import functools
from abc import ABC
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from anqa.core.utils.class_utils import Singleton

from . import Base
from .repository import SQLAlchemyModelRepository
from .settings import DatabaseSettings


class DefaultColumn(sa.Column, ABC):
    def __init__(self, *args, **dialect_kwargs):
        dialect_kwargs.setdefault("nullable", False)
        super().__init__(*args, **dialect_kwargs)


def create_engine_settings(settings_cls: type[DatabaseSettings], **kwargs):
    settings = settings_cls(**kwargs)
    return create_async_engine(**settings.dict())


def create_session_factory(engine):
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def get_session():
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except:  # noqa
                await session.rollback()
                raise

    return get_session


def create_repository_class(obj: str | AsyncEngine) -> type[SQLAlchemyModelRepository]:
    if isinstance(obj, str):
        dialect = obj
    elif isinstance(obj, AsyncEngine):
        dialect = obj.url.get_dialect().name
    else:
        raise TypeError(f"str or AsyncEngine expected, got {type(obj)}")

    if dialect == "postgres":
        from .dialects.postgres import PostgresModelRepository

        return PostgresModelRepository

    elif dialect == "sqlite":
        from .dialects.sqlite import SqliteModelRepository

        return SqliteModelRepository

    return SQLAlchemyModelRepository


get_db: AsyncGenerator[AsyncSession, None] | None = None


class DB(Singleton):
    ORMModel = Base
    Column = DefaultColumn

    def __init__(
        self, settings: type[DatabaseSettings], inject_name: str = "session", **kwargs
    ):
        global get_db
        self.inject_name = inject_name
        self.engine = create_engine_settings(settings, **kwargs)
        self.session_factory = create_session_factory(engine=self.engine)
        self.session_scope = asynccontextmanager(self.session_factory)
        get_db = self.session_factory

        self.__call__ = staticmethod(self.session_factory)
        self.Repository = create_repository_class(self.engine)

    def inject(self):
        def wrapper(func):
            @functools.wraps(func)
            async def wrapped(*args, **kwargs):
                if self.inject_name not in kwargs or kwargs[self.inject_name] is None:
                    async with self.session_scope() as session:
                        kwargs[self.inject_name] = session
                        return await func(*args, **kwargs)

                return await func(*args, **kwargs)

            return wrapped

        return wrapper
