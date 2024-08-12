import redis
from typing import Callable
from inspect import getsource
import cloudpickle


VERSIONED_FUNCTION_HASH = "versioned_functions"


r = redis.Redis()
pipeline = r.pipeline()


def save(function_: Callable) -> None:
    name: str = function_.__name__
    source: str = getsource(function_)

    # Increment/create the function version
    r.hincrby(VERSIONED_FUNCTION_HASH, name)
    version = int(r.hget(VERSIONED_FUNCTION_HASH, name))

    # Save the function - using Redis Hash because for now it is simple, but it will have more fields later on
    r.hset(
        f"{name}:{version}",
        mapping={
            "source": source,
        }
    )


def make_callable(name: str) -> Callable:

    version = int(r.hget(VERSIONED_FUNCTION_HASH, name))

    ser_func = r.hget(f"{name}:{version}", "function")

    return cloudpickle.loads(ser_func)
