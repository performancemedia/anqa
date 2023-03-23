import re
from typing import TypeVar

import questionary

from anqa.cli.enum import YesNoEnum

EnumType = TypeVar("EnumType")


def camel_to_snake(text: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def question(choices: EnumType) -> questionary.Question:
    prompt = camel_to_snake(choices.__name__).replace("_", " ")  # type: ignore
    return questionary.select(f"Select the {prompt}: ", choices=list(choices))  # type: ignore


def binary_question(option: str) -> questionary.Question:
    res = questionary.confirm(f"Do you want {option}?", default=False)
    return YesNoEnum.from_bool(res)
