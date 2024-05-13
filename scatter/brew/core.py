from functools import wraps
from typing import Callable

from scatter.earth.storage import store, delete
from scatter.storm.submit import submit_job as submit
import cloudpickle as pickle


def scatter(func: Callable) -> Callable:

    encoded_callable = pickle.dumps(func)
    store(encoded_callable, func.__name__)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def make_callable(func_name: str) -> Callable:
    # TODO: Make it look like the actual function - using __signature__ and function_struct
    return submit(func_name)


def vaporize(func_name: str):
    try:
        delete(func_name)
    except KeyError:
        raise KeyError(f"Function {func_name} not found.") from None
