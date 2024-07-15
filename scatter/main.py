import redis
from typing import Callable
from inspect import getsource
import cloudpickle

r = redis.Redis()
pipeline = r.pipeline()


def save(function_: Callable) -> None:
    name: str = function_.__name__
    source: str = getsource(function_)
    ser_func: bytes = cloudpickle.dumps(function_)

    current_version = r.get(f"{name}.latest")
    if current_version is None:
        version = 0
    else:
        version = int(current_version) + 1
    pipeline.set(f"{name}.latest", version)
    pipeline.set(f"{name}.{version}.source", source)
    pipeline.set(f"{name}.{version}.function", ser_func)

    pipeline.execute()


def make_callable(name: str) -> Callable:
    version = r.get(f"{name}.latest")
    ser_func = r.get(f"{name}.{version}.function")
    return cloudpickle.loads(ser_func)
