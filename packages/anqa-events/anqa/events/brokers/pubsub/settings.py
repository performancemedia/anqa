from eventiq.settings import BrokerSettings
from pydantic import Field


class PubSubSettings(BrokerSettings):
    service_file: str = Field(..., env="BROKER_SERVICE_FILE_PATH")
