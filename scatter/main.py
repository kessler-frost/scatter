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
    ser_func: bytes = cloudpickle.dumps(function_)

    # Increment/create the function version
    r.hincrby(VERSIONED_FUNCTION_HASH, name)
    version = int(r.hget(VERSIONED_FUNCTION_HASH, name))

    # Save the function
    r.hset(
        f"{name}:{version}",
        mapping={
            "source": source,
            "function": ser_func
        }
    )


def make_callable(name: str, pipelined: bool = False) -> Callable:

    version = int(r.hget(VERSIONED_FUNCTION_HASH, name))

    if pipelined:
        pipeline.hget(f"{name}:{version}", "function")
        return pipeline

    ser_func = r.hget(f"{name}:{version}", "function")

    return cloudpickle.loads(ser_func)
