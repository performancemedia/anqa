from __future__ import annotations

from anqa.core.exceptions import ConfigurationError, CoreException


class BrokerConfigurationError(ConfigurationError):
    """Raised by framework when invalid configuration is supplied"""


class BrokerError(CoreException):
    """Base Exception for broker related errors"""


class PublishError(BrokerError):
    """Raised when publishing a message fails"""


class EncoderError(CoreException):
    """Base Encoder error"""


class EncodeError(EncoderError):
    """Error encoding message"""


class DecodeError(EncoderError):
    """Error decoding message"""


class Skip(CoreException):
    """Raise exception to skip message without processing and/or retrying"""


class Fail(CoreException):
    """Fail message without retrying"""


class Retry(CoreException):
    """
    Utility exception for retrying message.
    RetryMessageMiddleware must be added
    """

    def __init__(self, delay: int | None = None):
        self.delay = delay
