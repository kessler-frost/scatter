from diskcache import FanoutCache
from scatter.earth.enc_dec import encoder, decoder
from typing import Callable
from pathlib import Path
from scatter.earth.structure import Function


cache_dir = str(Path(__file__).parent / "disk_cache")
index_name = "versions_index"

cache = FanoutCache(cache_dir)
index = cache.index(index_name)


# TODO: Look into memoizing the store and retrieve functions?

def store(func: Callable):
    # Get the version of the function from the index
    new_version = index.get(func.__name__, 0) + 1

    # Create a structured function with Function object
    structured_func = Function(name=func.__name__, version=new_version, callable_=func)

    # Encode the Function object
    encoded_func = encoder.encode(structured_func)

    # Store the encoded function in the cache
    cache[f"{structured_func.name}-{new_version}"] = encoded_func

    # Update the index with the new version
    index[structured_func.name] = new_version
    print(f"Version: {new_version} of {structured_func.name} stored.")
    print(f"Index: {dict(index.items())}")


def list_functions():
    return list(index.keys())


def retrieve(func_name: str) -> Function:
    encoded_func = cache[f"{func_name}-{index[func_name]}"]
    return decoder.decode(encoded_func)


def delete(func_name: str):
    version = index[func_name]

    del cache[f"{func_name}-{version}"]
    del index[func_name]


def rollback(func_name: str):
    version = index[func_name]

    if version > 1:
        index[func_name] = version - 1
        del cache[f"{func_name}-{version}"]


def clear_cache():
    cache.clear()
    index.clear()
