import logging


class LoggerMixin:
    logger: logging.Logger

    def __init_subclass__(cls, **kwargs):
        cls.logger = logging.getLogger(cls.__name__)
