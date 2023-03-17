from __future__ import annotations

import asyncio
import functools
import time


async def _retry_async(func, max_retries, backoff):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        exc = None
        for i in range(1, max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                exc = e
                await asyncio.sleep(backoff**i)
        raise exc

    return wrapper


def _retry_sync(func, max_retries, backoff):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        exc = None
        for i in range(1, max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                exc = e
                time.sleep(i**backoff)
        raise exc

    return wrapper


def retry(max_retries: int = 3, backoff: int = 2):
    def _wrapper(func):

        if asyncio.iscoroutinefunction(func):
            return _retry_async(func, max_retries, backoff)

        return _retry_sync(func, max_retries, backoff)

    return _wrapper
