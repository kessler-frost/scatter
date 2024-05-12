from functools import wraps
import msgspec
from typing import Callable, Union

from scatter.earth import (clear_cache, show_versions, retrieve_struct, store,
                           delete, rollback)


__all__ = ["scatter", "assemble", "clear_cache", "show_versions", "vaporize", "rollback"]


def scatter(func: Callable) -> Callable:

    structured_func = create_struct(func)

    store(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def assemble(func_name: str, struct: bool = False) -> Union[Callable, msgspec.Struct]:
    try:
        function_struct = retrieve_struct(func_name)
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
