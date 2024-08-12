import redis
from typing import Callable, Union
import cloudpickle

FUNC_NAMES_HASH = "func_names_hash"

r = redis.Redis()
pipe = r.pipeline()


def save(func: Callable):
    name: str = func.__name__

    current_version: Union[str, None] = r.hget(FUNC_NAMES_HASH, name)
    ser_func: bytes = cloudpickle.dumps(func)

    # If a function already exists, save it in a new hash
    if current_version is not None:
        current_mapping = r.hgetall(name)
        pipe.hset(
            f"{name}:{int(current_version)}",
            mapping=current_mapping
        )

    # Save the function's updated pickle
    pipe.hset(
        name,
        mapping={
            "ser_func": ser_func
        }
    )

    pipe.hset(FUNC_NAMES_HASH, name, int(current_version or -1) + 1)
    pipe.execute()


def _get_callable(name: str):
    ser_func = r.hget(name, "ser_func")
    func = cloudpickle.loads(ser_func)
    return func


def sync(name_or_func: Union[str, Callable]):
    if isinstance(name_or_func, str):
        return _get_callable(name_or_func)
    else:
        return _get_callable(name_or_func.__name__)
    


def flush():
    r.flushall()
