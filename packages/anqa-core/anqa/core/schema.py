from pydantic import BaseModel
from pydantic.dataclasses import create_pydantic_model_from_dataclass

from .utils.json import json_dumps, json_loads


class BaseSchema(BaseModel):
    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        json_dumps = json_dumps
        json_loads = json_loads
        orm_mode = True

    @classmethod
    def from_dataclass(cls, dcs):
        return create_pydantic_model_from_dataclass(dcs, config=cls.Config)
