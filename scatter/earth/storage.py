from diskcache import FanoutCache
from scatter.earth.enc_dec import encoder, decoder
from typing import Callable
from pathlib import Path
from scatter.earth.structure import Function


cache_dir = Path(__file__).parent / "disk_cache"


cache = FanoutCache(cache_dir)


# TODO: Look into memoizing the store and retrieve functions?

def store(func: Callable):
    structured_func = Function(name=func.__name__, callable_=func)
    encoded_func = encoder.encode(structured_func)
    cache.set(func.__name__, encoded_func)


def retrieve(func_name: str) -> Callable:
    encoded_func = cache.get(func_name)
    return decoder.decode(encoded_func).callable_


def clear_cache():
    cache.clear()
