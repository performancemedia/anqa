from ..types import Encoder


def get_default_encoder() -> Encoder:
    from .json import JsonEncoder

    return JsonEncoder()
