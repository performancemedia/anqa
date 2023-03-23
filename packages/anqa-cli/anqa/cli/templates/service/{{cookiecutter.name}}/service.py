from anqa.events import MessageService

from .handlers import consumer_group
from .settings import ServiceSettings

service = MessageService.from_settings_class(ServiceSettings)

service.add_consumer_group(consumer_group)
