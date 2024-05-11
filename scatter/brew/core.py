from functools import wraps
from typing import Callable, Union

from scatter.earth import (clear_cache, show_versions, retrieve, store,
                           delete, rollback)
from scatter.earth.structure import Function


__all__ = ["scatter", "assemble", "clear_cache", "show_versions", "vaporize", "rollback"]


def scatter(func: Callable) -> Callable:

    store(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def assemble(func_name: str, struct: bool = False) -> Union[Callable, Function]:
    try:
        function_struct = retrieve(func_name)
        if struct:
            return function_struct
        return function_struct.callable_
    except KeyError:
        raise KeyError(f"Function {func_name} not found.") from None


def vaporize(func_name: str):
    try:
        delete(func_name)
    except KeyError:
        raise KeyError(f"Function {func_name} not found.") from None
