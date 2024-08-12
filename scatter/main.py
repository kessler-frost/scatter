import redis
from typing import Callable, Dict
import inspect
import cloudpickle

FUNC_NAMES_HASH = "func_names_hash"

r = redis.Redis()
pipe = r.pipeline()


def save(func: Callable):
    name: str = func.__name__
    source: str = inspect.getsource(func)

    new_version = int(r.hget(FUNC_NAMES_HASH, name) or -1) + 1
    ser_func: bytes = cloudpickle.dumps(func)
        
    # Save the function's pickle
    pipe.hset(
        name,
        mapping={
            "ser_func": ser_func
        }
    )

    # Save the source code for patching later
    pipe.hset(
        f"{name}:{new_version}",
        mapping={
            "source": source
        }
    )

    pipe.hset(FUNC_NAMES_HASH, name, new_version)
    pipe.execute()


def _get_source(name: str):
    version = r.hget(FUNC_NAMES_HASH, name)
    if version is None:
        raise RuntimeError(f"Function {name} does not exist")
    else:
        version = int(version)

    return r.hget(
        f"{name}:{version}",
        "source"
    ).decode()


def setup(name: str) -> Callable:

    ser_func = r.hget(name, "orig_func")
    func = cloudpickle.loads(ser_func)
    return func


def sync(name: str):
    source: str = _get_source(name)
    print(f"Patched: {source}")


def flush():
    r.flushall()
