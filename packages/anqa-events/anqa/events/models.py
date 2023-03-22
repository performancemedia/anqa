from datetime import datetime
from typing import Any, Dict, Generic, Optional

from pydantic import Extra, Field, validator
from pydantic.fields import PrivateAttr
from pydantic.generics import GenericModel

from anqa.core.utils import str_uuid
from anqa.core.utils.dateutil import utc_now

from .types import D, RawMessage


class CloudEvent(GenericModel, Generic[D]):
    specversion: Optional[str] = "1.0"
    content_type: str = Field("application/json", alias="datacontenttype")
    id: str = Field(default_factory=str_uuid)
    trace_id: str = Field(default_factory=str_uuid, alias="traceid")
    time: datetime = Field(default_factory=utc_now)
    topic: str = Field(..., alias="subject")
    type: Optional[str] = None
    source: Optional[str] = None
    data: Optional[D] = None

    _raw: Optional[Any] = PrivateAttr()

    def __eq__(self, other):
        if not isinstance(other, CloudEvent):
            return False
        return self.id == other.id

    @validator("type", allow_reuse=True, always=True, pre=True)
    def get_type_from_cls_name(cls, v) -> str:
        return v or cls.__name__

    @property
    def raw(self) -> RawMessage:
        if self._raw is None:
            raise AttributeError("raw property accessible only for incoming messages")
        return self._raw

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault("by_alias", True)
        return super().dict(**kwargs)

    @classmethod
    def from_object(cls, obj: D, **kwargs):
        return cls(data=obj, **kwargs)

    @property
    def context(self) -> Dict[str, Any]:
        return {"trace_id": self.trace_id, "id": self.id}

    @property
    def age(self) -> int:
        return (utc_now() - self.time).seconds

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        extra = Extra.allow
