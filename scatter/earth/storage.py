from diskcache import FanoutCache
from pathlib import Path


cache_dir = str(Path(__file__).parent / "disk_cache")
# index_name = "versions_index"

cache = FanoutCache(cache_dir)
# index = cache.index(index_name)


# -------------------------- Storage / Retrieval --------------------------

def store(encoded_callable: bytes, func_name: str):

    # Get the version of the function from the index
    # new_version = index.get(func_name, 0) + 1

    new_version = 1

    # Store the callable in the cache
    cache[f"callable@{func_name}@{new_version}"] = encoded_callable

    # Update the index with the new version
    # index[func_name] = new_version


# def retrieve_callable(func_name: str) -> bytes:
#     """
#     To be used inside a worker to retrieve the encoded callable from the cache.
#     """

#     version = index[func_name]

#     # Return the encoded callable from the cache
#     return cache[f"callable@{func_name}@{version}"]


# def show_versions() -> dict:
    # return dict(index.items())


# -------------------------- Deletion / Rollback --------------------------

# def delete(func_name: str):
#     version = index[func_name]

#     for i in range(1, version + 1):
#         del cache[f"callable@{func_name}@{i}"]
#     del index[func_name]


# def rollback(func_name: str):
#     version = index[func_name]

#     if version > 1:
#         index[func_name] = version - 1
#         del cache[f"callable@{func_name}@{version}"]


# def clear_cache():
#     cache.clear()
#     index.clear()
