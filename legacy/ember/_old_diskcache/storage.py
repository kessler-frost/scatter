from diskcache import FanoutCache
from pathlib import Path
from typing import List


cache_dir = str(Path(__file__).parent / "disk_cache")

cache = FanoutCache(cache_dir)


# -------------------------- Storage / Retrieval --------------------------

def store(encoded_callable: bytes, func_name: str):

    callables = cache.get(f"callables@{func_name}")
    if not callables:
        callables = [encoded_callable]

    # Store the callable in the cache
    cache.set(f"callables@{func_name}", callables)


def retrieve_callable(func_name: str) -> bytes:
    """
    To be used inside a worker to retrieve the encoded callable from the cache.
    """

    # Return the encoded callable from the cache
    return cache.get(f"callables@{func_name}")[0]


# -------------------------- Deletion / Rollback --------------------------

def delete(func_name: str):
    del cache[f"callables@{func_name}"]


def rollback(func_name: str):
    callables: List[bytes] = cache.get(f"callables@{func_name}")
    if callables:
        del callables.pop[0]
        cache.set(f"callables@{func_name}", callables)


def clear_cache():
    cache.clear()
