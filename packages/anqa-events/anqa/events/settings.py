from typing import TYPE_CHECKING, List, Optional, Type

from pydantic import Field

from anqa.core.settings import AppSettings, FromSettings, ObjectSettings
from anqa.core.utils.imports import ImportedType

if TYPE_CHECKING:
    from anqa.events import Broker, ConsumerGroup, Encoder, MessageMiddleware


class BrokerSettings(ObjectSettings):
    description: str = ""
    middlewares: Optional[List[ImportedType["MessageMiddleware"]]] = None
    encoder: ImportedType[Type["Encoder"]] = Field(
        "anqa.events.encoders.json:JsonEncoder", env="ENCODER_CLASS"
    )

    class Config:
        env_prefix = "BROKER_"


class MessageServiceSettings(AppSettings):
    consumer_groups: List[ImportedType["ConsumerGroup"]] = []
    broker: "Broker" = FromSettings(BrokerSettings)
