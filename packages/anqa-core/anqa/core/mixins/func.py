from typing import Any, Callable


class FnWrapperMixin:
    def __init__(self, *, fn: Callable, **kwargs: Any):
        super().__init__(**kwargs)
        self.fn = fn

    @classmethod
    def as_decorator(cls, **kwargs):
        def wrapper(func):
            return cls(fn=func, **kwargs)

        return wrapper
