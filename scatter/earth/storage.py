from diskcache import FanoutCache
from scatter.earth.enc_dec import encoder, decoder
from typing import Callable

CACHE_NAME = "disk_cache"


cache = FanoutCache(CACHE_NAME)


def store(func: Callable):
    encoded_func = encoder.encode(func)
    cache.set(func.__name__, encoded_func)


def retrieve(func_name: str) -> Callable:
    encoded_func = cache.get(func_name)
    return decoder.decode(encoded_func).callable_
