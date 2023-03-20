from __future__ import annotations

import logging
from contextvars import ContextVar
from typing import Any

from pythonjsonlogger import jsonlogger

from anqa.core.utils.dateutil import utc_now
from anqa.core.utils.json import json_dumps

logger_context: ContextVar[dict[str, Any]] = ContextVar("logger_context", default={})


def update_logger_context(values):
    ctx = logger_context.get()
    token = ctx.update(values)
    logger_context.set(ctx)
    return token


def reset_logger_context(token):
    logger_context.reset(token)


class ContextAwareJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record.update(**logger_context.get())
        if "timestamp" not in log_record:
            log_record["timestamp"] = utc_now()

        log_record["level"] = record.levelname.upper()


def setup_logging(level, fmt: str = "%(name) %(level) %(message)") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(ContextAwareJsonFormatter(fmt, json_encoder=json_dumps))
    logging.basicConfig(handlers=[handler], level=level)
