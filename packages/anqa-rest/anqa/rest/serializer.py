from typing import Any, AsyncIterable, Iterable

from pydantic import BaseModel

from anqa.core.schema import BaseSchema


class Serializer(BaseSchema):
    @classmethod
    async def serialize(cls, obj: Any):
        if isinstance(obj, Serializer):
            return obj
        if isinstance(obj, dict):
            return cls.parse_obj(obj)
        if isinstance(obj, AsyncIterable):
            return [cls.from_orm(obj) async for obj in obj]
        if isinstance(obj, Iterable) and not isinstance(
            obj, (str, bytes, dict, BaseModel)
        ):
            return [await cls.serialize(o) for o in obj]
        else:
            return cls.from_orm(obj)
