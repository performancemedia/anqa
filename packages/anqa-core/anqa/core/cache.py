import functools
import weakref
from datetime import datetime, timedelta


def timed_cache(maxsize: int = None, **timedelta_kwargs):
    def decorator(func):
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.utcnow() - update_delta

        func = functools.lru_cache(maxsize=maxsize, typed=True)(func)

        @functools.wraps(func)
        def cached_func(*args, **kwargs):
            nonlocal next_update
            now = datetime.utcnow()

            if now >= next_update:
                func.cache_clear()
                next_update = now + update_delta
            try:
                return func(*args, **kwargs)
            except Exception as e:
                next_update = now
                raise e

        return cached_func

    return decorator


def method_cache(maxsize: int = None, **timedelta_kwargs):
    """
    Usage:
    class A:
        @method_cache(maxsize=10, seconds=60)
        def get_smth(self):
            return 1
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            # We're storing the wrapped method inside the instance. If we had
            # a strong reference to self the instance would never die.
            self_weak = weakref.ref(self)

            @functools.wraps(func)
            @timed_cache(maxsize=maxsize, **timedelta_kwargs)
            def cached_method(*fn_args, **fn_kwargs):
                return func(self_weak(), *fn_args, **fn_kwargs)

            setattr(self, func.__name__, cached_method)
            return cached_method(*args, **kwargs)

        return wrapped_func

    return decorator
