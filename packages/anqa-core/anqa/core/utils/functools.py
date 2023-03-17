import asyncio
import functools


def to_async(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

    return wrapper


def to_sync(coro):
    @functools.wraps(coro)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_until_complete(functools.partial(coro, *args, **kwargs))

    return wrapper
