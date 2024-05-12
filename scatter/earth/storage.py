import typing

import cloudpickle as pickle
import msgspec

from scatter.earth.cache import cache, index
from scatter.earth.key_helpers import (func_name_to_callable_key,
                                       func_name_to_struct_key)

# -------------------------- Encoder / Decoder --------------------------

encoder = msgspec.msgpack.Encoder()
decoder = msgspec.msgpack.Decoder()


def encode_callable(func: typing.Callable) -> bytes:
    return pickle.dumps(func)


def decode_callable(obj: bytes) -> typing.Callable:
    return pickle.loads(obj)


# -------------------------- Storage / Retrieval --------------------------

def store(structured_func: msgspec.Struct, func_callable: typing.Callable):

    # Get the name of the function
    func_name = func_callable.__name__

    # Get the version of the function from the index
    new_version = index.get(func_name, 0) + 1

    # Store the encoded function struct in the cache
    struct_key = func_name_to_struct_key(func_name, new_version)
    encoded_func_struct = encoder.encode(structured_func)
    cache[struct_key] = encoded_func_struct

    # Store the callable in the cache
    callable_key = func_name_to_callable_key(func_name, new_version)
    encoded_callable = encode_callable(func_callable)
    cache[callable_key] = encoded_callable

    # Update the index with the new version
    index[func_name] = new_version

    # Print the version and index items
    print(f"Version: {new_version} of {func_name} stored.")
    print(f"Index: {dict(index.items())}")


def show_versions() -> dict:
    return dict(index.items())


def retrieve_struct(func_name: str) -> msgspec.Struct:
    version = index[func_name]
    struct_key = func_name_to_struct_key(func_name, version)

    encoded_struct = cache[struct_key]
    return decoder.decode(encoded_struct)


def retrieve_callable(func_name: str) -> typing.Callable:
    version = index[func_name]
    callable_key = func_name_to_callable_key(func_name, version)

    encoded_callable = cache[callable_key]
    return decode_callable(encoded_callable)


# -------------------------- Deletion / Rollback --------------------------

def delete(func_name: str):
    version = index[func_name]

    for i in range(1, version + 1):
        del cache[func_name_to_struct_key(func_name, i)]
        del cache[func_name_to_callable_key(func_name, i)]
    del index[func_name]


def rollback(func_name: str):
    version = index[func_name]

    if version > 1:
        index[func_name] = version - 1
        del cache[func_name_to_struct_key(func_name, version)]


def clear_cache():
    cache.clear()
    index.clear()
