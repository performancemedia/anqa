import typing

import orjson
from fastapi.responses import JSONResponse
from pydantic.json import pydantic_encoder


class JsonResponse(JSONResponse):
    def render(self, content: typing.Any) -> bytes:
        return orjson.dumps(
            content,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
            default=pydantic_encoder,
        )
