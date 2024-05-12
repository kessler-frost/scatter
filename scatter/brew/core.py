from functools import wraps
from typing import Callable

import msgspec

from scatter.earth.storage import delete, retrieve_struct, encode, decode, store, msgspec_encoder
from scatter.earth.structure import create_struct
from scatter.storm.submit import submit_job as submit


def scatter(func: Callable) -> Callable:

    # function_struct = create_struct(func)
    # encoded_struct = encode(function_struct)

    encoded_callable = encode(func)

    func_name = func.__name__

    # store(encoded_struct, encoded_callable, func_name)
    store(encoded_callable, func_name)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def make_callable(func_name: str) -> Callable:
    encoded_struct = retrieve_struct(func_name)
    function_struct: msgspec.Struct = decode(encoded_struct)

    # TODO: Make it look like the actual function - using __signature__ and function_struct
    def wrapper(*args, **kwargs):
        struct_obj = function_struct(*args, **kwargs)
        encoded_struct_obj = msgspec_encoder.encode(struct_obj)
        return submit(encoded_struct_obj, func_name)

    wrapper.__name__ = func_name

    return wrapper


def vaporize(func_name: str):
    try:
        delete(func_name)
    except KeyError:
        raise KeyError(f"Function {func_name} not found.") from None
