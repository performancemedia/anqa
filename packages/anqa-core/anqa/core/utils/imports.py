import importlib
from typing import TYPE_CHECKING, Any, Callable, Generic, Type, TypeVar

from pydantic.validators import errors, str_validator

T = TypeVar("T")
S = TypeVar("S")


def import_from_string(path: str) -> Any:
    module_name, _, obj = path.partition(":")
    module = importlib.import_module(module_name)

    try:
        return getattr(module, obj)
    except AttributeError as e:
        raise ImportError from e


if TYPE_CHECKING:
    ImportedType = Type
else:

    class ImportedType(Generic[T]):
        validate_always = True

        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, value: Any):
            if isinstance(value, Callable):
                return value

            try:
                value = str_validator(value)

            except errors.StrError:
                raise errors.PyObjectError(
                    error_message="value is neither a valid import path not a valid callable"
                )

            try:
                return import_from_string(value)
            except ImportError as e:
                raise errors.PyObjectError(error_message=str(e))
