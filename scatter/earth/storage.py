from diskcache import FanoutCache
from scatter.earth.enc_dec import encoder, decoder
from typing import Callable
from pathlib import Path
from scatter.earth.structure import Function


cache_dir = str(Path(__file__).parent / "disk_cache")
index_dir = str(Path(__file__).parent / "function_names")


cache = FanoutCache(cache_dir)


# TODO: Look into memoizing the store and retrieve functions?

def store(func: Callable):

    index = cache.index(index_dir)

    # Get the version of the function from the index
    version = index.get(func.__name__, 0) + 1

    structured_func = Function(name=func.__name__, version=version, callable_=func)

    # Encode the Function object
    encoded_func = encoder.encode(structured_func)

    # Store the encoded function in the cache
    cache.set(structured_func.name, encoded_func)

    # Update the index with the new version
    index[func.__name__] = version


def list_functions():
    index = cache.index(index_dir)
    return list(index.keys())


def retrieve(func_name: str) -> Function:
    encoded_func = cache.get(func_name)
    return decoder.decode(encoded_func)


def clear_cache():
    cache.clear()
