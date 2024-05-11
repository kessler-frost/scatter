from typing import Callable
from scatter.earth import store, retrieve, clear_cache, list_functions
from functools import wraps


__all__ = ["scatter", "assemble", "clear_cache", "list_functions"]


def scatter(func: Callable) -> Callable:

    store(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def assemble(func_name: str) -> Callable:
    return retrieve(func_name)
