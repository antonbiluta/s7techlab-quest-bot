from typing import Awaitable, Callable, Coroutine


# async def is_exist(func: Callable[..., Awaitable], *args, **kwargs) -> bool:
#     result = await func(*args, **kwargs)
#     return result is not None


# async def is_not_exist(func: Callable[..., Coroutine], *args, **kwargs) -> bool:
#     result = await func(*args, **kwargs)
#     return result is None


def is_exist(result) -> bool:
    return result is not None


def is_not_exist(result) -> bool:
    return result is None

